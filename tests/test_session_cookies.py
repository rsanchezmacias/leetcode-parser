from requests.cookies import RequestsCookieJar

from services.session_cookies import chrome_cookie_files, load_leetcode_cookies


def make_jar(**cookies) -> RequestsCookieJar:
    jar = RequestsCookieJar()
    for name, value in cookies.items():
        jar.set(name, value, domain=".leetcode.com", path="/")
    return jar


def test_uses_first_profile_with_session():
    jars = {
        "default": make_jar(csrftoken="only-csrf"),
        "profile1": make_jar(LEETCODE_SESSION="session-1", csrftoken="csrf-1"),
        "profile2": make_jar(LEETCODE_SESSION="session-2"),
    }
    result = load_leetcode_cookies(cookie_files=["default", "profile1", "profile2"], loader=jars.__getitem__)
    assert result is jars["profile1"]


def test_skips_profiles_that_fail_to_load():
    def loader(path):
        if path == "broken":
            raise PermissionError("Keychain access denied")
        return make_jar(LEETCODE_SESSION="session")

    result = load_leetcode_cookies(cookie_files=["broken", "ok"], loader=loader)
    assert result.get("LEETCODE_SESSION") == "session"


def test_returns_none_when_no_profile_has_session():
    result = load_leetcode_cookies(cookie_files=["a", "b"], loader=lambda path: make_jar(csrftoken="x"))
    assert result is None


def test_returns_none_when_every_profile_fails():
    def loader(path):
        raise RuntimeError("cannot decrypt")

    assert load_leetcode_cookies(cookie_files=["a"], loader=loader) is None


def test_returns_none_without_cookie_files():
    assert load_leetcode_cookies(cookie_files=[], loader=lambda path: make_jar(LEETCODE_SESSION="s")) is None


def test_chrome_cookie_files_finds_profiles(tmp_path):
    (tmp_path / "Default" / "Network").mkdir(parents=True)
    (tmp_path / "Default" / "Network" / "Cookies").write_text("")
    (tmp_path / "Profile 2").mkdir()
    (tmp_path / "Profile 2" / "Cookies").write_text("")
    (tmp_path / "Profile 3").mkdir()  # no cookie DB: ignored
    (tmp_path / "System Profile").mkdir()  # not a user profile: ignored

    assert chrome_cookie_files(str(tmp_path)) == [
        str(tmp_path / "Default" / "Network" / "Cookies"),
        str(tmp_path / "Profile 2" / "Cookies"),
    ]


def test_chrome_cookie_files_missing_chrome_dir(tmp_path):
    assert chrome_cookie_files(str(tmp_path / "does-not-exist")) == []
