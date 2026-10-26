import re
from html.parser import HTMLParser

# Tags that start and end their own paragraph
BLOCK_TAGS = {"p", "div", "pre", "ul", "ol", "table", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"}


class _TextExtractor(HTMLParser):
    """Collects text from description HTML, collapsing whitespace outside <pre> blocks."""

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
    """Converts a LeetCode description from HTML to plain text."""
    extractor = _TextExtractor()
    extractor.feed(html)
    extractor.close()

    text = "".join(extractor.parts).replace("\xa0", " ")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip("\n")
