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


@pytest.mark.parametrize("url", [
    "leetcode.com/problems/two-sum/",
    "www.leetcode.com/problems/two-sum/",
])
def test_validate_url_accepts_scheme_less_and_www(url):
    assert URLValidator().validate_url(url) is True
