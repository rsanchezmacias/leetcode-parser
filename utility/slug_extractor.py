import re
from urllib.parse import urlparse
from errors.exceptions import InvalidInputException
from models.constants import UserMessages

# Matches "/problems/<slug>" optionally followed by more path segments (description/, editorial/, …)
_PROBLEM_PATH = re.compile(r"^/problems/([a-z0-9-]+)(?:/|$)")


def extract_slug(url: str) -> str:
    """
    Extracts the problem slug (e.g. "two-sum") from a LeetCode problem URL.

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
