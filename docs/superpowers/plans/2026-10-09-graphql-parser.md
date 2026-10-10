# GraphQL Parser Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Selenium/Chrome scraper with one call to LeetCode's GraphQL API, authenticated for Premium problems by reading the `LEETCODE_SESSION` cookie straight from the user's normal Chrome.

**Architecture:** `LeetcodeParser.parse(url, language) -> Question` keeps its public shape, so `QuestionFormatter`, `FileManager`, the templates and file naming stay the same. Inside, the parser extracts the problem slug from the URL, loads leetcode.com cookies from Chrome via `browser_cookie3` (best effort: `None` if unavailable), POSTs one GraphQL query, converts the HTML description to plain text, and picks the starter code for the chosen language from `codeSnippets`. Everything Selenium-specific (Chrome profile, language dropdown, login dialog, "Close Chrome" button) is deleted.

**Tech Stack:** Python 3.13 (pyenv 3.13.0), `requests`, `browser-cookie3`, stdlib `html.parser`, `pytest`, Tkinter GUI, py2app.

**Spec:** No separate spec document. The design was agreed in conversation on 2026-10-09 and is summarized in Architecture and Global Constraints. Evidence it rests on (verified live against `https://leetcode.com/graphql` with no cookie):
- `two-sum` → `{"data":{"question":{"questionFrontendId":"1","title":"Two Sum","difficulty":"Easy","isPaidOnly":false,"content":"<p>…","codeSnippets":[{"langSlug":"swift","code":"class Solution {…"}…]}}}`
- `closest-binary-search-tree-value` (Premium) → `{"data":{"question":{"title":"Closest Binary Search Tree Value","isPaidOnly":true,"content":null,"codeSnippets":null}}}`
- `no-such-problem-xyz` → `{"data":{"question":null}}`

## Global Constraints

- Python 3.13; macOS only; cookies are read from Google Chrome at `~/Library/Application Support/Google/Chrome`.
- New runtime dependencies are exactly: `requests==2.32.3`, `browser-cookie3==0.20.1`. Test dependency: `pytest==8.3.4`. Remove `selenium`.
- Output stays the same: `<questions dir>/<difficulty>/q<number>/q<CamelCaseTitle>.<ext>`, rendered from the existing `templates/base_py.j2` / `templates/base_swift.j2`. Never overwrite an existing file (existing `FileManager.write_file` behaviour).
- The `LEETCODE_SESSION` value is never printed, logged, shown in the GUI, or written to disk by this tool.
- Failing to read cookies (no Chrome, Keychain denied, unreadable DB) must never block free problems; it only affects Premium ones.
- All user-facing errors are one readable sentence, never a traceback.
- Run tests from the project root with `python -m pytest tests -v`.

## Review Focus

1. **Premium problem without a usable session.** The user expects a message saying to log into leetcode.com in Chrome. If there are no cookies vs. there are cookies but no access (expired or not Premium), the message says which. Pinned in Task 4 (`test_premium_without_cookies…`, `test_premium_with_cookies_but_no_access…`).
2. **Cookie reading fails** (Keychain prompt denied, Chrome not installed, a profile's DB unreadable, several Chrome profiles). Free problems still work, and the profile that has the session is the one used. Pinned in Task 3 (`test_skips_profiles_that_fail_to_load`, `test_uses_first_profile_with_session`) and Task 4 (`test_free_problem_works_without_cookies`).
3. **URL variants** the user actually pastes: query strings (`?envType=company&envId=roblox…`), `/description/` or `/editorial/` suffixes, no scheme, `www.`, and non-problem URLs. The first five work; the last gets a clear "not a LeetCode problem URL" error. Pinned in Task 1.
4. **Problem without the chosen language's starter code** (e.g. SQL/shell problems have no Swift snippet). The user gets a clear "no Swift starter code" error instead of an empty file. Pinned in Task 4 (`test_missing_language_snippet…`).
5. **Network / HTTP / API failures** (offline, Cloudflare 403/429, HTML instead of JSON, GraphQL `errors`). The user gets a one-line message. Pinned in Task 4 (`test_http_error…`, `test_network_error…`, `test_non_json_response…`, `test_graphql_errors…`).

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `utility/slug_extractor.py` | Create | `extract_slug(url) -> str`: problem slug from any LeetCode problem URL |
| `utility/url_validator.py` | Modify | Also require a LeetCode problem URL (delegates to `extract_slug`) |
| `utility/html_to_text.py` | Create | `html_to_text(html) -> str`: LeetCode description HTML → readable plain text |
| `services/session_cookies.py` | Create | `load_leetcode_cookies() -> CookieJar \| None`: read leetcode.com cookies from Chrome profiles |
| `services/leetcode_parser.py` | Rewrite | GraphQL fetch → `Question` |
| `errors/exceptions.py` | Modify | Add `LeetcodeAPIException` |
| `models/language.py` | Modify | Replace `site_language()` with `snippet_slug()` |
| `models/constants.py` | Modify | Drop `DOMLabels` and Selenium config keys; add `INVALID_PROBLEM_URL` |
| `models/driver_config.py` | Modify | `AppConfig` keeps only `questions_path_directory` |
| `services/file_manager.py` | Modify | Stop reading/writing Selenium config keys |
| `services/language_selector.py` | Delete | Selenium-only |
| `main.py`, `main_gui.py` | Modify | Use the new parser; remove Chrome lifecycle + login dialog |
| `requirements.txt`, `setup_app.py`, `README.md`, `CLAUDE.md` | Modify | Dependencies, bundle packages, docs |
| `tests/…` | Create | pytest suites per unit |

---

### Task 1: Branch, test setup, and slug extraction

**Files:**
- Modify: `requirements.txt`
- Create: `utility/slug_extractor.py`
- Modify: `utility/url_validator.py`
- Modify: `models/constants.py` (add one message to `UserMessages`)
- Test: `tests/test_slug_extractor.py`

**Interfaces:**
- Produces: `utility.slug_extractor.extract_slug(url: str) -> str`. It raises `errors.exceptions.InvalidInputException` for non-problem URLs. `URLValidator.validate_url(url)` now raises the same exception for non-problem URLs.

- [ ] **Step 1: Create a branch**

```bash
cd ~/Projects/leetcode_formatter
git checkout -b graphql-parser
```

- [ ] **Step 2: Update `requirements.txt` and install**

Replace the whole file with:

```
Jinja2==3.1.5
Pillow==12.1.1
PyYAML==6.0.2
requests==2.32.3
browser-cookie3==0.20.1
pytest==8.3.4
```

Run: `pip install -r requirements.txt`
Expected: installs `browser-cookie3`, `pytest` (and their deps `pycryptodomex`, `lz4`) without errors.

- [ ] **Step 3: Write the failing tests**

Create `tests/test_slug_extractor.py`:

```python
import pytest

from errors.exceptions import InvalidInputException
from utility.slug_extractor import extract_slug
from utility.url_validator import URLValidator


@pytest.mark.parametrize("url", [
    "https://leetcode.com/problems/two-sum/",
    "https://leetcode.com/problems/two-sum",
    "https://leetcode.com/problems/two-sum/description/",
    "https://leetcode.com/problems/two-sum/editorial/",
    "https://www.leetcode.com/problems/two-sum/",
    "leetcode.com/problems/two-sum/",
    "  https://leetcode.com/problems/two-sum/  ",
    "https://leetcode.com/problems/two-sum/description/?envType=company&envId=roblox&favoriteSlug=roblox-thirty-days",
])
def test_extracts_slug_from_problem_urls(url):
    assert extract_slug(url) == "two-sum"


@pytest.mark.parametrize("url", [
    "https://leetcode.com/",
    "https://leetcode.com/problemset/",
    "https://leetcode.com/problems/",
    "https://example.com/problems/two-sum/",
    "not a url",
    "",
])
def test_rejects_non_problem_urls(url):
    with pytest.raises(InvalidInputException):
        extract_slug(url)


def test_url_validator_rejects_non_problem_url():
    with pytest.raises(InvalidInputException):
        URLValidator().validate_url("https://leetcode.com/problemset/")


def test_url_validator_accepts_problem_url():
    assert URLValidator().validate_url("https://leetcode.com/problems/two-sum/") is True
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `python -m pytest tests/test_slug_extractor.py -v`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'utility.slug_extractor'`.

- [ ] **Step 5: Add the user message**

In `models/constants.py`, add this field to `UserMessages` after `INVALID_INPUT_LANGUAGE`:

```python
    INVALID_PROBLEM_URL: str = "Please enter a LeetCode problem URL, e.g. https://leetcode.com/problems/two-sum/"
```

- [ ] **Step 6: Implement `extract_slug`**

Create `utility/slug_extractor.py`:

```python
import re
from urllib.parse import urlparse
from errors.exceptions import InvalidInputException
from models.constants import UserMessages

# Matches "/problems/<slug>" optionally followed by more path segments (description/, editorial/, …)
_PROBLEM_PATH = re.compile(r"^/problems/([a-z0-9-]+)(?:/|$)")


def extract_slug(url: str) -> str:
    """
    Extracts the problem slug from a LeetCode problem URL.

    Args:
        url (str): e.g. "https://leetcode.com/problems/two-sum/description/?envType=…"

    Returns:
        str: The slug, e.g. "two-sum".

    Raises:
        InvalidInputException: If the URL is not a LeetCode problem URL.
    """
    url = url.strip()
    if "://" not in url:
        url = "https://" + url

    parsed_url = urlparse(url)
    host = parsed_url.netloc.lower()
    if host not in ("leetcode.com", "www.leetcode.com"):
        raise InvalidInputException(UserMessages.INVALID_PROBLEM_URL)

    match = _PROBLEM_PATH.match(parsed_url.path.lower())
    if not match:
        raise InvalidInputException(UserMessages.INVALID_PROBLEM_URL)

    return match.group(1)
```

- [ ] **Step 7: Make `URLValidator` require a problem URL**

In `utility/url_validator.py`, add the import `from utility.slug_extractor import extract_slug` and replace the `return True` line inside `validate_url` with:

```python
            extract_slug(url)
            return True
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `python -m pytest tests/test_slug_extractor.py -v`
Expected: 16 passed.

- [ ] **Step 9: Commit**

```bash
git add requirements.txt utility/slug_extractor.py utility/url_validator.py models/constants.py tests/test_slug_extractor.py
git commit -m "Add problem slug extraction and test setup"
```

---

### Task 2: HTML description → plain text

**Files:**
- Create: `utility/html_to_text.py`
- Test: `tests/test_html_to_text.py`

**Interfaces:**
- Produces: `utility.html_to_text.html_to_text(html: str) -> str`. Paragraphs are separated by one blank line, `<li>` items become `- item`, `<sup>` becomes `^` (`10^4`), `<sub>` becomes `_` (`x_i`), and `<pre>` whitespace is preserved. Entities are decoded and non-breaking spaces become plain spaces. There are no trailing spaces, and leading/trailing blank lines are stripped.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_html_to_text.py`:

```python
from utility.html_to_text import html_to_text

LEETCODE_STYLE_HTML = (
    '<p>Given <code>nums</code>&nbsp;and k.</p>\n\n'
    '<p>&nbsp;</p>\n'
    '<p><strong class="example">Example 1:</strong></p>\n\n'
    '<pre>\n<strong>Input:</strong> nums = [2,7]\n<strong>Output:</strong> [0,1]\n</pre>\n\n'
    '<p><strong>Constraints:</strong></p>\n\n'
    '<ul>\n\t<li><code>2 &lt;= n &lt;= 10<sup>4</sup></code></li>\n\t<li>x<sub>i</sub> is unique</li>\n</ul>\n'
)


def test_converts_leetcode_description():
    assert html_to_text(LEETCODE_STYLE_HTML) == (
        "Given nums and k.\n"
        "\n"
        "Example 1:\n"
        "\n"
        "Input: nums = [2,7]\n"
        "Output: [0,1]\n"
        "\n"
        "Constraints:\n"
        "\n"
        "- 2 <= n <= 10^4\n"
        "- x_i is unique"
    )


def test_preserves_leading_spaces_inside_pre():
    assert html_to_text("<p>Tree:</p><pre>\n  1\n /\n2\n</pre>") == "Tree:\n\n  1\n /\n2"


def test_br_becomes_newline():
    assert html_to_text("<p>line one<br>line two</p>") == "line one\nline two"


def test_text_outside_paragraphs_is_kept():
    assert html_to_text("<p>&nbsp;</p>\n<strong>Follow-up:&nbsp;</strong>Can you do O(n<sup>2</sup>)?") == \
        "Follow-up: Can you do O(n^2)?"


def test_empty_input():
    assert html_to_text("") == ""
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_html_to_text.py -v`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'utility.html_to_text'`.

- [ ] **Step 3: Implement `html_to_text`**

Create `utility/html_to_text.py`:

```python
import re
from html.parser import HTMLParser

# Tags that start and end their own paragraph
BLOCK_TAGS = {"p", "div", "pre", "ul", "ol", "table", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"}


class _TextExtractor(HTMLParser):
    """
    Collects readable text from LeetCode description HTML.
    Whitespace is collapsed everywhere except inside <pre> blocks.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.pre_depth = 0

    def _ends_with_newline(self) -> bool:
        for part in reversed(self.parts):
            if part:
                return part.endswith("\n")
        return True

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK_TAGS:
            self.parts.append("\n\n")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag == "sup":
            self.parts.append("^")
        elif tag == "sub":
            self.parts.append("_")

        if tag == "pre":
            self.pre_depth += 1

    def handle_endtag(self, tag):
        if tag == "pre":
            self.pre_depth -= 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_data(self, data):
        if self.pre_depth == 0:
            data = re.sub(r"[ \t\r\n]+", " ", data)
            if self._ends_with_newline():
                data = data.lstrip(" ")
        self.parts.append(data)


def html_to_text(html: str) -> str:
    """
    Converts a LeetCode problem description from HTML to plain text.

    Args:
        html (str): The description HTML returned by LeetCode's GraphQL API.

    Returns:
        str: Readable plain text with paragraphs separated by a blank line.
    """
    extractor = _TextExtractor()
    extractor.feed(html)
    extractor.close()

    text = "".join(extractor.parts).replace("\xa0", " ")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip("\n")
```

Note: the final `strip("\n")` (not `strip()`) keeps leading spaces on the first line of a `<pre>` block, as in `test_preserves_leading_spaces_inside_pre`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_html_to_text.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add utility/html_to_text.py tests/test_html_to_text.py
git commit -m "Add HTML to plain text conversion for problem descriptions"
```

---

### Task 3: Read the LeetCode session from Chrome

**Files:**
- Create: `services/session_cookies.py`
- Test: `tests/test_session_cookies.py`

**Interfaces:**
- Produces:
  - `services.session_cookies.chrome_cookie_files(chrome_dir: str = CHROME_DIR) -> list[str]`: cookie DB paths for `Default` first, then `Profile *` sorted. Each is `<profile>/Network/Cookies` if present, else `<profile>/Cookies`.
  - `services.session_cookies.load_leetcode_cookies(cookie_files: list[str] | None = None, loader: Callable[[str], CookieJar] | None = None) -> CookieJar | None`: the leetcode.com cookie jar from the first profile that has `LEETCODE_SESSION`. Returns `None` if no profile has one or reading fails. It never raises.
  - Constant `SESSION_COOKIE_NAME = "LEETCODE_SESSION"`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_session_cookies.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_session_cookies.py -v`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'services.session_cookies'`.

- [ ] **Step 3: Implement the cookie reader**

Create `services/session_cookies.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_session_cookies.py -v`
Expected: 7 passed.

- [ ] **Step 5: Check against the real Chrome (manual)**

Make sure you're logged into leetcode.com in your normal Chrome, then run:

```bash
python -c "from services.session_cookies import chrome_cookie_files, load_leetcode_cookies; print(chrome_cookie_files()); print('session found:', load_leetcode_cookies() is not None)"
```

Expected: macOS asks to allow access to "Chrome Safe Storage". Click **Always Allow**. The output lists at least one cookie file and prints `session found: True`. The script never prints the cookie value.

If it prints `session found: False` while you're logged in, run the next command to see the underlying error, and fix it before continuing. It could be a cookie format browser_cookie3 doesn't support, or a permissions problem.

```bash
python -c "import browser_cookie3; browser_cookie3.chrome(domain_name='leetcode.com')"
```

- [ ] **Step 6: Commit**

```bash
git add services/session_cookies.py tests/test_session_cookies.py
git commit -m "Read the LeetCode session cookie from Chrome"
```

---

### Task 4: GraphQL-based `LeetcodeParser`

**Files:**
- Rewrite: `services/leetcode_parser.py`
- Modify: `errors/exceptions.py`
- Modify: `models/language.py`
- Test: `tests/test_leetcode_parser.py`

**Interfaces:**
- Consumes: `extract_slug` (Task 1), `html_to_text` (Task 2), `load_leetcode_cookies` (Task 3).
- Produces:
  - `errors.exceptions.LeetcodeAPIException(Exception)`.
  - `Language.snippet_slug(self) -> str`: `"python3"` for PYTHON, `"swift"` for SWIFT. Replaces `site_language()`.
  - `LeetcodeParser(cookie_loader: Callable[[], CookieJar | None] = load_leetcode_cookies, http=requests)` with `parse(url: str, language: Language) -> Question`. The returned `Question` has `url`, `title` as `"<number>. <title>"` (the format `QuestionFormatter.get_title_and_number` expects), `difficulty` (`"Easy"`/`"Medium"`/`"Hard"`), `description` (plain text) and `code`. It raises `InvalidInputException` for bad URLs and `LeetcodeAPIException` for everything else. It has no `clean_up()` and no `auth_prompt_fn` anymore.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_leetcode_parser.py`:

```python
import pytest
import requests
from requests.cookies import RequestsCookieJar

from errors.exceptions import InvalidInputException, LeetcodeAPIException
from models.language import Language
from services.leetcode_parser import GRAPHQL_URL, LeetcodeParser

URL = "https://leetcode.com/problems/two-sum/description/?envType=company"


class FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=None):
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error

    def json(self):
        if self._json_error:
            raise self._json_error
        return self._payload


class FakeHttp:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


def question_payload(**overrides):
    question = {
        "questionFrontendId": "1",
        "title": "Two Sum",
        "difficulty": "Easy",
        "isPaidOnly": False,
        "content": "<p>Find two numbers.</p>",
        "codeSnippets": [
            {"langSlug": "python3", "code": "class Solution:\n    pass"},
            {"langSlug": "swift", "code": "class Solution {\n}"},
        ],
    }
    question.update(overrides)
    return {"data": {"question": question}}


def make_parser(response=None, error=None, cookies=None):
    http = FakeHttp(response or FakeResponse(payload=question_payload()), error)
    return LeetcodeParser(cookie_loader=lambda: cookies, http=http), http


def session_jar():
    jar = RequestsCookieJar()
    jar.set("LEETCODE_SESSION", "session-value", domain=".leetcode.com", path="/")
    jar.set("csrftoken", "csrf-value", domain=".leetcode.com", path="/")
    return jar


def test_parses_question_fields():
    parser, _ = make_parser()
    question = parser.parse(URL, Language.SWIFT)
    assert question.url == URL
    assert question.title == "1. Two Sum"
    assert question.difficulty == "Easy"
    assert question.description == "Find two numbers."
    assert question.code == "class Solution {\n}"


def test_picks_python3_snippet_for_python():
    parser, _ = make_parser()
    assert parser.parse(URL, Language.PYTHON).code == "class Solution:\n    pass"


def test_free_problem_works_without_cookies():
    parser, http = make_parser(cookies=None)
    parser.parse(URL, Language.SWIFT)
    url, kwargs = http.calls[0]
    assert url == GRAPHQL_URL
    assert kwargs["json"]["variables"] == {"titleSlug": "two-sum"}
    assert kwargs["cookies"] is None
    assert "x-csrftoken" not in kwargs["headers"]


def test_sends_chrome_cookies_and_csrf_header():
    jar = session_jar()
    parser, http = make_parser(cookies=jar)
    parser.parse(URL, Language.SWIFT)
    _, kwargs = http.calls[0]
    assert kwargs["cookies"] is jar
    assert kwargs["headers"]["x-csrftoken"] == "csrf-value"


def test_unknown_problem():
    parser, _ = make_parser(FakeResponse(payload={"data": {"question": None}}))
    with pytest.raises(LeetcodeAPIException, match="No LeetCode problem found for 'two-sum'"):
        parser.parse(URL, Language.SWIFT)


def test_premium_without_cookies_asks_to_log_in():
    locked = question_payload(isPaidOnly=True, content=None, codeSnippets=None)
    parser, _ = make_parser(FakeResponse(payload=locked), cookies=None)
    with pytest.raises(LeetcodeAPIException, match="no LeetCode login was found in Chrome"):
        parser.parse(URL, Language.SWIFT)


def test_premium_with_cookies_but_no_access():
    locked = question_payload(isPaidOnly=True, content=None, codeSnippets=None)
    parser, _ = make_parser(FakeResponse(payload=locked), cookies=session_jar())
    with pytest.raises(LeetcodeAPIException, match="doesn't have access"):
        parser.parse(URL, Language.SWIFT)


def test_missing_language_snippet():
    only_sql = question_payload(codeSnippets=[{"langSlug": "mysql", "code": "SELECT 1"}])
    parser, _ = make_parser(FakeResponse(payload=only_sql))
    with pytest.raises(LeetcodeAPIException, match="no Swift starter code"):
        parser.parse(URL, Language.SWIFT)


def test_http_error():
    parser, _ = make_parser(FakeResponse(status_code=403))
    with pytest.raises(LeetcodeAPIException, match="HTTP 403"):
        parser.parse(URL, Language.SWIFT)


def test_network_error():
    parser, _ = make_parser(error=requests.ConnectionError("offline"))
    with pytest.raises(LeetcodeAPIException, match="Could not reach LeetCode"):
        parser.parse(URL, Language.SWIFT)


def test_non_json_response():
    parser, _ = make_parser(FakeResponse(json_error=ValueError("not json")))
    with pytest.raises(LeetcodeAPIException, match="unexpected response"):
        parser.parse(URL, Language.SWIFT)


def test_graphql_errors():
    parser, _ = make_parser(FakeResponse(payload={"errors": [{"message": "boom"}]}))
    with pytest.raises(LeetcodeAPIException, match="LeetCode API error: boom"):
        parser.parse(URL, Language.SWIFT)


def test_invalid_url_is_rejected_before_any_request():
    parser, http = make_parser()
    with pytest.raises(InvalidInputException):
        parser.parse("https://leetcode.com/problemset/", Language.SWIFT)
    assert http.calls == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_leetcode_parser.py -v`
Expected: collection ERROR with `ImportError: cannot import name 'LeetcodeAPIException' from 'errors.exceptions'`.

- [ ] **Step 3: Add the exception**

Append to `errors/exceptions.py`:

```python

class LeetcodeAPIException(Exception):
    """ Exception raised when a problem can't be fetched from LeetCode """
    pass
```

- [ ] **Step 4: Replace `site_language()` with `snippet_slug()`**

In `models/language.py`, replace the whole `site_language` method with:

```python
    def snippet_slug(self):
        """
        Returns LeetCode's identifier for this language in a question's codeSnippets.

        Returns:
            str: The language slug, e.g. "python3".
        """
        mapping = {
            Language.PYTHON: "python3",
            Language.SWIFT: "swift"
        }
        return mapping.get(self)
```

- [ ] **Step 5: Rewrite the parser**

Replace the whole of `services/leetcode_parser.py` with:

```python
from http.cookiejar import CookieJar
from typing import Callable

import requests

from errors.exceptions import LeetcodeAPIException
from models.language import Language
from models.question import Question
from services.session_cookies import load_leetcode_cookies
from utility.html_to_text import html_to_text
from utility.slug_extractor import extract_slug

GRAPHQL_URL = "https://leetcode.com/graphql"
REQUEST_TIMEOUT_SECONDS = 15

QUESTION_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId
    title
    difficulty
    isPaidOnly
    content
    codeSnippets { langSlug code }
  }
}
"""


class LeetcodeParser:
    """
    Fetches question data from LeetCode's GraphQL API.
    """

    def __init__(self, cookie_loader: Callable[[], CookieJar | None] = load_leetcode_cookies, http=requests):
        """
        Initializes the LeetcodeParser.

        Args:
            cookie_loader (callable, optional): Returns leetcode.com cookies for Premium access, or None.
                Defaults to reading them from Chrome.
            http (optional): Object with a requests-compatible post(). Defaults to the requests module.
        """
        self._cookie_loader = cookie_loader
        self._http = http

    def parse(self, url: str, language: Language) -> Question:
        """
        Fetches a LeetCode problem and extracts question details.

        Args:
            url (str): The URL of the LeetCode problem page.
            language (Language): The language whose starter code to use.

        Returns:
            Question: A populated Question object, with title formatted as "<number>. <title>".

        Raises:
            InvalidInputException: If the URL is not a LeetCode problem URL.
            LeetcodeAPIException: If the problem can't be fetched or is locked.
        """
        slug = extract_slug(url)
        cookies = self._cookie_loader()
        data = self._fetch_question(slug, cookies)

        if data is None:
            raise LeetcodeAPIException(f"No LeetCode problem found for '{slug}'. Check the URL.")

        # Premium problems come back with content=None unless the session has access
        if data.get("content") is None:
            raise LeetcodeAPIException(self._locked_message(data.get("title") or slug, cookies))

        question = Question()
        question.url = url
        question.title = f"{data['questionFrontendId']}. {data['title']}"
        question.difficulty = data["difficulty"]
        question.description = html_to_text(data["content"])
        question.code = self._starter_code(data, language)
        return question

    def _fetch_question(self, slug: str, cookies: CookieJar | None) -> dict | None:
        """
        Runs the GraphQL query for a problem.

        Returns:
            dict | None: The "question" object, or None if LeetCode has no such problem.
        """
        headers = {
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/problems/{slug}/",
        }
        csrf_token = self._cookie_value(cookies, "csrftoken")
        if csrf_token:
            headers["x-csrftoken"] = csrf_token

        try:
            response = self._http.post(
                GRAPHQL_URL,
                json={"query": QUESTION_QUERY, "variables": {"titleSlug": slug}},
                headers=headers,
                cookies=cookies,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as e:
            raise LeetcodeAPIException(f"Could not reach LeetCode: {e}")

        if response.status_code != 200:
            raise LeetcodeAPIException(f"LeetCode returned HTTP {response.status_code}. Try again in a moment.")

        try:
            payload = response.json()
        except ValueError:
            raise LeetcodeAPIException("LeetCode returned an unexpected response. Try again in a moment.")

        if payload.get("errors"):
            message = payload["errors"][0].get("message", "unknown error")
            raise LeetcodeAPIException(f"LeetCode API error: {message}")

        return (payload.get("data") or {}).get("question")

    def _starter_code(self, data: dict, language: Language) -> str:
        """Returns the starter code for the language, or raises if LeetCode has none."""
        for snippet in data.get("codeSnippets") or []:
            if snippet.get("langSlug") == language.snippet_slug():
                return snippet["code"]
        raise LeetcodeAPIException(
            f"'{data['title']}' has no {language.name.capitalize()} starter code on LeetCode."
        )

    def _locked_message(self, title: str, cookies: CookieJar | None) -> str:
        """Explains why a Premium problem's content wasn't returned."""
        if cookies is None:
            return (
                f"'{title}' is a Premium problem and no LeetCode login was found in Chrome. "
                "Log into leetcode.com in Chrome with your Premium account, then try again."
            )
        return (
            f"'{title}' is a Premium problem and your Chrome LeetCode session doesn't have access. "
            "The session may have expired or the account may not have Premium. "
            "Log into leetcode.com in Chrome again, then try again."
        )

    @staticmethod
    def _cookie_value(cookies: CookieJar | None, name: str) -> str | None:
        """Returns a cookie's value from the jar, or None."""
        if cookies is None:
            return None
        for cookie in cookies:
            if cookie.name == name:
                return cookie.value
        return None
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m pytest tests -v`
Expected: all tests in the four files pass (13 in `test_leetcode_parser.py`).

- [ ] **Step 7: Commit**

```bash
git add services/leetcode_parser.py errors/exceptions.py models/language.py tests/test_leetcode_parser.py
git commit -m "Fetch problems from LeetCode's GraphQL API instead of scraping"
```

---

### Task 5: Wire up the CLI and GUI, remove Selenium

**Files:**
- Modify: `main.py`
- Modify: `main_gui.py`
- Delete: `services/language_selector.py`
- Modify: `models/constants.py`, `models/driver_config.py`, `services/file_manager.py`
- Modify: `setup_app.py`, `README.md`, `CLAUDE.md`

**Interfaces:**
- Consumes: `LeetcodeParser().parse(url, language) -> Question` (Task 4).
- Produces: `AppConfig(questions_path_directory=None)` with a single attribute.

- [ ] **Step 1: Update `main.py`**

Replace the end of `main()`, from `parser = LeetcodeParser(config=app_config)` through the `finally:` block, with:

```python
    parser = LeetcodeParser()
    output_path = parse_question(parser, raw_url, language, question_formatter, file_manager, app_config)
    open_generated_file(app_launcher, output_path, language)
```

`clean_up(exit_code=0)` at the very end of `main()` stays.

- [ ] **Step 2: Simplify `main_gui.py`**

Make these edits:
1. In `__init__`, delete `self._active_parser: LeetcodeParser | None = None` and `self.protocol("WM_DELETE_WINDOW", self._on_quit)`.
2. Delete the methods `_set_done`, `_on_close_chrome` and `_on_quit`.
3. Delete the whole "Auth dialog" section: the comment banner and `_show_auth_dialog`.
4. Replace `_run_parse` with:

```python
    def _run_parse(self, url: str, language: Language):
        try:
            app_config = self._app_config or self._file_manager.get_app_config()
        except Exception as e:
            self._log_msg(f"❌ Config error: {e}")
            self._set_busy(False)
            return

        try:
            self._log_msg("🔍 Fetching problem from LeetCode…")
            raw_question = LeetcodeParser().parse(url=url, language=language)

            self._log_msg("✏️  Formatting question…")
            formatted_question = self._question_formatter.format_question(raw_question)

            self._log_msg("💾 Writing file…")
            output_path = self._file_manager.write_question_to_template(
                question=formatted_question,
                language=language,
                path=app_config.questions_path_directory,
            )

            self._log_msg(f"✅ Done!\n   {output_path}")

            try:
                self._app_launcher.open(path=output_path, language=language)
            except Exception as e:
                self._log_msg(f"⚠️  Could not open file automatically: {e}")

        except Exception as e:
            self._log_msg(f"❌ Error: {e}")
        finally:
            self._set_busy(False)
```

`threading` is still imported and used by `_on_parse`, so keep that import.

- [ ] **Step 3: Remove Selenium-only code and config**

1. Delete `services/language_selector.py`: `git rm services/language_selector.py`
2. In `models/constants.py`: delete the whole `DOMLabels` class. In `Configs`, delete `CONFIG_DRIVER_USER_DATA_FIELD` and `CONFIG_DRIVER_PROFILE_NAME_FIELD`. Change `VALID_INPUT_EXAMPLE` to `"Example: python main.py -s https://leetcode.com/problems/two-sum/"`.
3. Replace the body of `models/driver_config.py` with:

```python
class AppConfig:
    """
    Represents the application's configuration settings.
    """

    def __init__(self, questions_path_directory=None):
        """
        Args:
            questions_path_directory (str, optional): Path to the questions directory. Defaults to None.
        """
        self.questions_path_directory = questions_path_directory
```

4. In `services/file_manager.py`:
   - Replace `DEFAULT_CONFIG_TEMPLATE` with:

```python
DEFAULT_CONFIG_TEMPLATE = """\
config:
  questions_home_directory: "{placeholder}"
""".format(placeholder=PLACEHOLDER_QUESTIONS_DIR)
```

   - In `_ensure_bundle_data_dir`, change `f.write(DEFAULT_CONFIG_TEMPLATE.format(data_dir=BUNDLE_DATA_DIR))` to `f.write(DEFAULT_CONFIG_TEMPLATE)`.
   - In `get_app_config`, delete the `app_config.user_data_directory = …` and `app_config.profile_name = …` statements. Existing config files that still contain `user_data_dir` / `profile_directory` keep working, because those keys are simply ignored.
5. In `resources/config.yaml`, delete the `user_data_dir` and `profile_directory` lines.

- [ ] **Step 4: Verify nothing references Selenium anymore**

Run: `grep -rnE "selenium|DOMLabels|LanguageSelector|language_selector|user_data_directory|profile_name|site_language|parser\.clean_up|_active_parser|auth_prompt" --include=*.py . | grep -v "^./tests/"`
Expected: no output. (`main.py`'s own module-level `clean_up()` exit helper is unrelated and stays.)

Run: `python -m pytest tests -v`
Expected: all pass.

- [ ] **Step 5: Update the bundle packages**

In `setup_app.py`, replace the `"packages"` list with:

```python
    "packages": [
        "requests", "certifi", "browser_cookie3", "Cryptodome", "lz4",
        "jinja2", "yaml",
        "models", "services", "utility", "errors",
    ],
```

- [ ] **Step 6: Update the docs**

- `CLAUDE.md` (and `AGENTS.md`, which has the same text): replace "it fires up a Chrome browser via Selenium, scrapes the problem" with "it fetches the problem from LeetCode's GraphQL API (using your Chrome LeetCode login for Premium problems)".
- `README.md`:
  - Prerequisites: remove "Google Chrome + ChromeDriver matching your Chrome version". Add "Google Chrome, logged into leetcode.com, for Premium problems (optional)".
  - Usage: replace steps 3–5 with:
    "3. Click **Parse Problem**. The file is created and opened.
     For Premium problems, stay logged into leetcode.com in Chrome. The first time, macOS asks to allow access to "Chrome Safe Storage"; click **Always Allow**."
  - First Launch: change "Everything else (Chrome profile, config)" to "Everything else (config)".

- [ ] **Step 7: End-to-end check with the CLI (manual)**

```bash
python main.py -s https://leetcode.com/problems/two-sum/
```

Expected: creates (or finds the existing) `<questions dir>/easy/q1/qTwoSum.swift` with a readable description comment and `func twoSum`, and opens it. No Chrome window appears.

```bash
python main.py -s "https://leetcode.com/problems/closest-binary-search-tree-value/description/?envType=company&envId=roblox"
```

Expected, logged into Chrome with Premium: creates `easy/q270/qClosestBinarySearchTreeValue.swift`. Without Premium: a one-line Premium message, no traceback.

- [ ] **Step 8: Commit**

```bash
git add -A main.py main_gui.py services models setup_app.py README.md CLAUDE.md AGENTS.md resources/config.yaml
git commit -m "Remove Selenium: CLI and GUI use the GraphQL parser"
```

---

### Task 6: Rebuild and reinstall the app

**Files:** none (build only)

- [ ] **Step 1: Build**

```bash
rm -rf build dist && python setup_app.py py2app
```

Expected: ends with `Done!` and `dist/LeetCode Formatter.app` exists.

- [ ] **Step 2: Install**

Quit the app if it's running, then:

```bash
rm -rf "/Applications/LeetCode Formatter.app" && cp -R "dist/LeetCode Formatter.app" /Applications/
```

- [ ] **Step 3: GUI check (manual)**

Open the app. Paste `https://leetcode.com/problems/two-sum/`, choose Swift and click **Parse Problem**.
Expected: the log shows Fetching → Formatting → Writing → ✅ Done. The button returns to **Parse Problem**, there's no Chrome window and no "Close Chrome" button.

Then parse the Premium URL from Task 5 Step 7. Expected: it works if you're logged into Chrome with Premium, or shows the one-line Premium message.

If the bundled app fails with `ModuleNotFoundError`, add the missing package name to `"packages"` in `setup_app.py` and rebuild.

- [ ] **Step 4: Clean up the old Selenium profile (optional, manual)**

`driver_profile/` in the repo and `~/Library/Application Support/LeetCodeFormatter/driver_profile` are no longer used. Delete them if you like; they're git-ignored.
