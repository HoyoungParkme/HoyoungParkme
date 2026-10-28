"""티스토리 RSS에서 기술 글만 골라 어두운 터미널 패널(blog.svg)로 그린다."""
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from xml.sax.saxutils import escape

RSS_URL = "https://hypark.tistory.com/rss"
EXCLUDED_CATEGORIES = {"자격증"}  # 패널에 띄우지 않을 카테고리
MAX_POSTS = 5
MAX_TITLE_LENGTH = 60             # 이보다 긴 제목은 … 으로 줄인다
OUTPUT_PATH = "blog.svg"

ROW_START_Y = 76
ROW_GAP = 28


def fetch_tech_posts():
    request = urllib.request.Request(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        rss = ET.fromstring(response.read())

    posts = []
    for item in rss.findall("./channel/item"):
        categories = {category.text for category in item.findall("category")}
        if categories & EXCLUDED_CATEGORIES:
            continue  # 자격증 글은 건너뛴다
        posts.append({
            "title": item.findtext("title"),
            "date": parsedate_to_datetime(item.findtext("pubDate")).strftime("%Y.%m.%d"),
        })
    return posts[:MAX_POSTS]


def shorten(title):
    return title if len(title) <= MAX_TITLE_LENGTH else title[:MAX_TITLE_LENGTH] + "…"


def to_svg(posts):
    height = ROW_START_Y + ROW_GAP * (len(posts) - 1) + 30

    # 글 한 줄 = 노란 날짜 + 제목
    rows = []
    for index, post in enumerate(posts):
        y = ROW_START_Y + ROW_GAP * index
        rows.append(
            f'<text x="32" y="{y}" class="sans body">'
            f'<tspan class="mono date">{post["date"]}</tspan>  {escape(shorten(post["title"]))}</text>'
        )
    row_lines = "\n".join(rows)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="840" height="{height}" viewBox="0 0 840 {height}" role="img" aria-labelledby="title">
<title id="title">~/git log --blog — 최근 블로그 글</title>
<style>
.mono {{ font-family: 'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, 'DejaVu Sans Mono', monospace; }}
.sans {{ font-family: Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', sans-serif; }}
.body {{ fill: #e9e1f2; font-size: 14px; }}
.head {{ fill: #f5f0fa; font-size: 17px; font-weight: 700; }}
.tilde {{ fill: #ff4f9a; }}
.date {{ fill: #e3b341; font-size: 12px; }}
.hint {{ fill: #8c7d99; font-size: 12px; }}
</style>
<rect x="0.5" y="0.5" width="839" height="{height - 1}" rx="10" fill="#150d1c" stroke="#2a1d33"/>
<text x="32" y="40" class="mono head"><tspan class="tilde">~/</tspan>git log --blog</text>
<text x="808" y="40" text-anchor="end" class="mono hint">hypark.tistory.com →</text>
{row_lines}
</svg>
'''


def main():
    svg = to_svg(fetch_tech_posts())
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        file.write(svg)


if __name__ == "__main__":
    main()
