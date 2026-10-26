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
