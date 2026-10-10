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
    def __init__(self, responses=None, error=None):
        self.responses = list(responses or [])
        self.error = error
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]


class RecordingLoader:
    def __init__(self, result=None):
        self.result = result
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.result


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


def make_parser(response=None, error=None, cookies=None, responses=None):
    if responses is None:
        responses = [response or FakeResponse(payload=question_payload())]
    http = FakeHttp(responses, error)
    loader = RecordingLoader(cookies)
    return LeetcodeParser(cookie_loader=loader, http=http), http, loader


def session_jar():
    jar = RequestsCookieJar()
    jar.set("LEETCODE_SESSION", "session-value", domain=".leetcode.com", path="/")
    jar.set("csrftoken", "csrf-value", domain=".leetcode.com", path="/")
    return jar


def test_parses_question_fields():
    parser, _, _ = make_parser()
    question = parser.parse(URL, Language.SWIFT)
    assert question.url == URL
    assert question.title == "1. Two Sum"
    assert question.difficulty == "Easy"
    assert question.description == "Find two numbers."
    assert question.code == "class Solution {\n}"


def test_picks_python3_snippet_for_python():
    parser, _, _ = make_parser()
    assert parser.parse(URL, Language.PYTHON).code == "class Solution:\n    pass"


def locked():
    return FakeResponse(payload=question_payload(isPaidOnly=True, content=None, codeSnippets=None))


def test_free_problem_never_loads_cookies():
    parser, http, loader = make_parser(cookies=session_jar())
    parser.parse(URL, Language.SWIFT)
    assert loader.calls == 0
    assert len(http.calls) == 1
    url, kwargs = http.calls[0]
    assert url == GRAPHQL_URL
    assert kwargs["json"]["variables"] == {"titleSlug": "two-sum"}
    assert kwargs["cookies"] is None
    assert "x-csrftoken" not in kwargs["headers"]


def test_premium_retries_with_chrome_cookies_and_csrf_header():
    jar = session_jar()
    parser, http, loader = make_parser(responses=[locked(), FakeResponse(payload=question_payload(isPaidOnly=True))], cookies=jar)
    question = parser.parse(URL, Language.SWIFT)
    assert question.title == "1. Two Sum"
    assert loader.calls == 1
    assert len(http.calls) == 2
    assert http.calls[0][1]["cookies"] is None
    _, kwargs = http.calls[1]
    assert kwargs["cookies"] is jar
    assert kwargs["headers"]["x-csrftoken"] == "csrf-value"


def test_unknown_problem():
    parser, _, loader = make_parser(FakeResponse(payload={"data": {"question": None}}), cookies=session_jar())
    with pytest.raises(LeetcodeAPIException, match="No LeetCode problem found for 'two-sum'"):
        parser.parse(URL, Language.SWIFT)
    assert loader.calls == 0


def test_premium_without_cookies_asks_to_log_in():
    parser, http, loader = make_parser(locked(), cookies=None)
    with pytest.raises(LeetcodeAPIException, match="no LeetCode login could be read from Chrome"):
        parser.parse(URL, Language.SWIFT)
    assert loader.calls == 1
    assert len(http.calls) == 1


def test_premium_with_cookies_but_no_access():
    parser, http, _ = make_parser(locked(), cookies=session_jar())
    with pytest.raises(LeetcodeAPIException, match="doesn't have access"):
        parser.parse(URL, Language.SWIFT)
    assert len(http.calls) == 2


def test_missing_language_snippet():
    only_sql = question_payload(codeSnippets=[{"langSlug": "mysql", "code": "SELECT 1"}])
    parser, _, _ = make_parser(FakeResponse(payload=only_sql))
    with pytest.raises(LeetcodeAPIException, match="no Swift starter code"):
        parser.parse(URL, Language.SWIFT)


def test_http_error():
    parser, _, _ = make_parser(FakeResponse(status_code=403))
    with pytest.raises(LeetcodeAPIException, match="HTTP 403"):
        parser.parse(URL, Language.SWIFT)


def test_network_error():
    parser, _, _ = make_parser(error=requests.ConnectionError("offline"))
    with pytest.raises(LeetcodeAPIException, match="Could not reach LeetCode. Check your internet connection."):
        parser.parse(URL, Language.SWIFT)


def test_timeout():
    parser, _, _ = make_parser(error=requests.Timeout("slow"))
    with pytest.raises(LeetcodeAPIException, match="took too long to respond"):
        parser.parse(URL, Language.SWIFT)


def test_other_request_error():
    parser, _, _ = make_parser(error=requests.RequestException("weird"))
    with pytest.raises(LeetcodeAPIException, match="Could not reach LeetCode: weird"):
        parser.parse(URL, Language.SWIFT)


def test_non_json_response():
    parser, _, _ = make_parser(FakeResponse(json_error=ValueError("not json")))
    with pytest.raises(LeetcodeAPIException, match="unexpected response"):
        parser.parse(URL, Language.SWIFT)


def test_graphql_errors():
    parser, _, _ = make_parser(FakeResponse(payload={"errors": [{"message": "boom"}]}))
    with pytest.raises(LeetcodeAPIException, match="LeetCode API error: boom"):
        parser.parse(URL, Language.SWIFT)


def test_invalid_url_is_rejected_before_any_request():
    parser, http, _ = make_parser()
    with pytest.raises(InvalidInputException):
        parser.parse("https://leetcode.com/problemset/", Language.SWIFT)
    assert http.calls == []
