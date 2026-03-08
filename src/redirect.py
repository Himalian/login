import re

import requests
import os
from requests import Response


def is_cmcc() -> bool:
    """check if `CMCC-PTU` connected"""
    import subprocess

    try:
        if os.name == "posix":
            ssid = subprocess.check_output(
                ["nmcli", "connection", "show", "--active"], stderr=subprocess.DEVNULL
            )
        else:
            ssid = subprocess.check_output(
                ["netsh", "WLAN", "show", "interfaces"], stderr=subprocess.DEVNULL
            )

        return b"CMCC-PTU" in ssid
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_redirect_response(
    url: str = "http://www.msftconnecttest.com/redirect",
    timeout: int = 10,
) -> Response:
    """Get redirect response from a URL"""
    s = requests.session()
    s.proxies.clear()
    s.trust_env = False
    try:
        result: Response = s.get(
            url, timeout=timeout, proxies=None, allow_redirects=False, verify=False
        )
        return result
    except Exception as e:
        print(f"Failed to get redirect url {e}")
        raise


def parse_redirect(resp: Response | None = None) -> str | None:
    """
    从重定向页面解析校园网登录参数

    Args:
            resp: 从重定向url获取的响应。如果为 None，则调用 get_redirect_response()。

    Returns:
            str: 用于登录的url, 如果已登录返回 "ALREADY_LOGGED"
    """
    if resp is None:
        try:
            resp = get_redirect_response()
        except Exception:
            return None

    # 1. 从 HTTP 头获取
    if resp.status_code in [301, 302, 303, 307, 308]:
        redirect_url = resp.headers.get("Location", "")
        if "go.microsoft.com" in redirect_url:
            print("该设备已经登录过了")
            return "ALREADY_LOGGED"
        elif redirect_url:
            print(f"从 HTTP headers获取到重定向 URL: {redirect_url}")
            return redirect_url
    else:
        # 2. Extract authentication url
        # 尝试匹配 location.href
        m = re.search(r"location\.href\s*=\s*['\"](http[^'\"]+)['\"]", resp.text)
        if m:
            redirect_url = m.group(1)
            print(f"从 HTML (script) 提取到重定向 URL: {redirect_url}")
            return redirect_url

        # Fallback: 尝试匹配 <a href="...">
        m = re.search(r"<a\s+href=['\"](http[^'\"]+)['\"]", resp.text)
        if m:
            redirect_url = m.group(1)
            print(f"从 HTML (a tag) 提取到重定向 URL: {redirect_url}")
            return redirect_url

    return None


if __name__ == "__main__":
    url = get_redirect_response()
    if url:
        print(url)
    else:
        print("Failed to get redirect URL")
