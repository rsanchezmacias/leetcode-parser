import glob
import os
from http.cookiejar import CookieJar
from typing import Callable

# Google Chrome's user data directory on macOS
CHROME_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Google", "Chrome")

# Cookie LeetCode uses to identify a logged-in session
SESSION_COOKIE_NAME = "LEETCODE_SESSION"

LEETCODE_DOMAIN = "leetcode.com"


def chrome_cookie_files(chrome_dir: str = CHROME_DIR) -> list[str]:
    """
    Lists the cookie database of every Chrome profile, "Default" first.

    Args:
        chrome_dir (str): Chrome's user data directory.

    Returns:
        list[str]: Paths to existing cookie databases.
    """
    profiles = [os.path.join(chrome_dir, "Default")] + sorted(glob.glob(os.path.join(chrome_dir, "Profile *")))

    cookie_files = []
    for profile in profiles:
        # Newer Chrome versions keep cookies under Network/
        for relative_path in (os.path.join("Network", "Cookies"), "Cookies"):
            path = os.path.join(profile, relative_path)
            if os.path.isfile(path):
                cookie_files.append(path)
                break
    return cookie_files


def _load_with_browser_cookie3(cookie_file: str) -> CookieJar:
    """Reads and decrypts leetcode.com cookies from one Chrome cookie database."""
    import browser_cookie3  # imported lazily: it shells out to the Keychain on first use
    return browser_cookie3.chrome(cookie_file=cookie_file, domain_name=LEETCODE_DOMAIN)


def load_leetcode_cookies(
    cookie_files: list[str] | None = None,
    loader: Callable[[str], CookieJar] | None = None,
) -> CookieJar | None:
    """
    Finds the user's LeetCode session in Chrome.

    The first time this runs, macOS asks permission to read "Chrome Safe Storage"
    from the Keychain. Any failure is treated as "not logged in" so that free
    problems keep working.

    Args:
        cookie_files (list[str], optional): Cookie databases to search. Defaults to all Chrome profiles.
        loader (callable, optional): Reads one cookie database. Defaults to browser_cookie3.

    Returns:
        CookieJar | None: leetcode.com cookies from the first profile with a session, or None.
    """
    if cookie_files is None:
        cookie_files = chrome_cookie_files()
    if loader is None:
        loader = _load_with_browser_cookie3

    for cookie_file in cookie_files:
        try:
            jar = loader(cookie_file)
        except Exception:
            continue
        if any(cookie.name == SESSION_COOKIE_NAME for cookie in jar):
            return jar
    return None
