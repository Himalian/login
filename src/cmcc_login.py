# pyright: standard
import json
import re
import time
from datetime import datetime
from typing import Final, Optional
from urllib.parse import urlencode

import requests
from pydantic import BaseModel


class SessionContext(BaseModel):
    username: str
    password: str
    login_ip: str = "192.168.116.8"
    login_url: str = ""
    wlan_acname: str = "SR8805F"
    wlan_acip: str = "218.207.103.209"
    wlan_mac: str = "98BD80DBFE66"
    wlan_ip: str = "172.30.137.210"


class CMCCAuthenticator:
    REDIRECT_PATTERN: Final = re.compile(
        r"wlanuserip=([\d\.]+).*?wlanacname=([^&]+).*?wlanacip=([\d\.]+).*?(?:mac|wlanusermac)=([\w\-:]+)",
        re.I,
    )
    JSONP_PATTERN: Final = re.compile(r"dr(\d+)\((.*)\)")

    STATUS_MAPPING: Final = {
        "1": "登录成功",
        "8": "用户名或密码错误",
        "logout_ok": "退出成功",
    }

    def __init__(self, username: str, password: str) -> None:
        self.ctx = SessionContext(username=username, password=password)
        self.is_authenticated = False

    def authenticate(self) -> None:
        if self._check_already_logged():
            return

        self._update_pattern_from_redirect()

        if self.is_authenticated:
            return

        response = self._request_login()
        if response:
            self._handle_login_response(response)

    def _check_already_logged(self) -> bool:
        from .redirect import parse_redirect

        redirect_url = parse_redirect()
        if redirect_url == "ALREADY_LOGGED":
            self.is_authenticated = True
            return True

        if redirect_url:
            self.ctx.login_url = redirect_url

        return False

    def _update_pattern_from_redirect(self) -> None:
        match = self.REDIRECT_PATTERN.search(self.ctx.login_url)
        if not match:
            return

        ip, ac_name, ac_ip, mac = match.groups()
        self.ctx.wlan_ip = ip
        self.ctx.wlan_acname = ac_name
        self.ctx.wlan_acip = ac_ip
        self.ctx.wlan_mac = mac.replace("-", "").replace(":", "").upper()

    def _request_login(self) -> Optional[str]:
        url, headers = self._build_request_payload()

        try:
            resp = requests.get(url, headers=headers, timeout=12)
            resp.raise_for_status()
            return resp.text.strip()
        except requests.RequestException:
            return None

    def _build_request_payload(self) -> tuple[str, dict]:
        timestamp = int(time.time() * 1000)
        query_params = {
            "c": "Portal",
            "a": "login",
            "callback": f"dr{timestamp}",
            "login_method": "1",
            "user_account": f",0,{self.ctx.username}@fjwlan",
            "user_password": self.ctx.password,
            "wlan_user_ip": self.ctx.wlan_ip,
            "wlan_user_mac": self.ctx.wlan_mac,
            "wlan_ac_ip": self.ctx.wlan_acip,
            "wlan_ac_name": self.ctx.wlan_acname,
            "jsVersion": "3.0",
            "_": timestamp,
        }

        full_url = f"http://{self.ctx.login_ip}:801/eportal/?{urlencode(query_params)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
            "Referer": self.ctx.login_url,
            "Accept": "*/*",
        }
        return full_url, headers

    def _handle_login_response(self, raw_text: str) -> None:
        match = self.JSONP_PATTERN.match(raw_text)
        if not match:
            return

        ms_timestamp, json_payload = match.groups()

        try:
            data = json.loads(json_payload)
            self._log_formatted_result(data, ms_timestamp)
        except json.JSONDecodeError:
            pass

    def _log_formatted_result(self, data: dict, ms_timestamp: str) -> None:
        ret_code = str(data.get("ret_code") or data.get("result") or "")
        status = self.STATUS_MAPPING.get(ret_code, f"Unknown({ret_code})")

        print(f"\n[CMCC Auth] {status}")
        if uid := data.get("uid"):
            print(f"User: {uid}")

        if request_time := self._parse_ms_timestamp(ms_timestamp):
            print(f"Time: {request_time}")

    def _parse_ms_timestamp(self, ms_str: str) -> Optional[datetime]:
        try:
            return datetime.fromtimestamp(int(ms_str) // 1000)
        except (ValueError, OSError):
            return None
