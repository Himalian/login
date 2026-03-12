# pyright: strict
from src.cmcc_login import CMCCAuthenticator
from src.redirect import is_cmcc, is_network_connected


def main() -> None:
    from src.config import settings

    if not is_network_connected():
        print("Error: No network connection detected. Please check your network cable or Wi-Fi.")
        return

    username = settings.USERNAME
    password = settings.PASSWORD

    if not is_cmcc():
        from src.dorm_login import login_dorm

        login_dorm(username, password)
        return

    print("Status: CMCC network detected")
    auth = CMCCAuthenticator(username, password)
    auth.authenticate()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Operation canceled by User")
    except Exception as e:
        print(f"Error: {e}")
