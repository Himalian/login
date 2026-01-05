# pyright: strict
from src.cmcc_login import CMCCAuthenticator
from src.config import settings
from src.redirect import is_cmcc


def main() -> None:
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
    main()
