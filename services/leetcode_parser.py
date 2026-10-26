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
    """Fetches question data from LeetCode's GraphQL API."""

    def __init__(self, cookie_loader: Callable[[], CookieJar | None] = load_leetcode_cookies, http=requests):
        """
        Args:
            cookie_loader (callable, optional): Returns leetcode.com cookies for Premium access, or None.
            http (optional): Object with a requests-compatible post().
        """
        self._cookie_loader = cookie_loader
        self._http = http

    def parse(self, url: str, language: Language) -> Question:
        """
        Fetches a LeetCode problem.

        Args:
            url (str): The LeetCode problem URL.
            language (Language): The language whose starter code to use.

        Returns:
            Question: The populated question.

        Raises:
            InvalidInputException: If the URL is not a LeetCode problem URL.
            LeetcodeAPIException: If the problem can't be fetched or is locked.
        """
        slug = extract_slug(url)
        cookies = None
        data = self._fetch_question(slug, None)

        # Only touch Chrome's cookies (and the Keychain) when the problem is Premium and locked
        if data is not None and data.get("isPaidOnly") and data.get("content") is None:
            cookies = self._cookie_loader()
            if cookies is not None:
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
        """Runs the GraphQL query; returns the "question" object, or None if there is no such problem."""
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
        except requests.Timeout:
            raise LeetcodeAPIException("LeetCode took too long to respond. Try again in a moment.")
        except requests.ConnectionError:
            raise LeetcodeAPIException("Could not reach LeetCode. Check your internet connection.")
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
                f"'{title}' is a Premium problem and no LeetCode login could be read from Chrome. "
                "Make sure you're logged into leetcode.com in Chrome, that this app has Full Disk Access "
                "(System Settings → Privacy & Security → Full Disk Access), and that you allowed access to "
                "\"Chrome Safe Storage\" when macOS asked, then try again."
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
