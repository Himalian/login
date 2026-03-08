from unittest.mock import MagicMock, patch
from requests import Response
from src.redirect import is_cmcc, parse_redirect


def test_is_cmcc_true():
    with patch("subprocess.check_output") as mock_run:
        mock_run.return_value = b"some network\nCMCC-PTU\nother"
        assert is_cmcc() is True


def test_is_cmcc_false():
    with patch("subprocess.check_output") as mock_run:
        mock_run.return_value = b"other-wifi"
        assert is_cmcc() is False


def test_is_cmcc_error():
    with patch("subprocess.check_output", side_effect=FileNotFoundError):
        assert is_cmcc() is False


def test_parse_redirect_from_headers():
    mock_resp = MagicMock(spec=Response)
    mock_resp.status_code = 302
    mock_resp.headers = {"Location": "http://login.page?token=123"}
    assert parse_redirect(mock_resp) == "http://login.page?token=123"


def test_parse_redirect_already_logged():
    mock_resp = MagicMock(spec=Response)
    mock_resp.status_code = 302
    mock_resp.headers = {"Location": "https://go.microsoft.com/fwlink/..."}
    assert parse_redirect(mock_resp) == "ALREADY_LOGGED"


def test_parse_redirect_from_html_script():
    mock_resp = MagicMock(spec=Response)
    mock_resp.status_code = 200
    mock_resp.text = (
        '<html><script>location.href="http://login.page/from_js"</script></html>'
    )
    assert parse_redirect(mock_resp) == "http://login.page/from_js"


def test_parse_redirect_from_html_atag():
    mock_resp = MagicMock(spec=Response)
    mock_resp.status_code = 200
    mock_resp.text = (
        '<html><body><a href="http://login.page/from_a">Login</a></body></html>'
    )
    assert parse_redirect(mock_resp) == "http://login.page/from_a"


def test_parse_redirect_none():
    mock_resp = MagicMock(spec=Response)
    mock_resp.status_code = 200
    mock_resp.text = "<html>No redirect here</html>"
    assert parse_redirect(mock_resp) is None
