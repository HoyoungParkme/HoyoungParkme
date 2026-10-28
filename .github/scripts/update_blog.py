"""티스토리 RSS에서 기술 글만 골라 README의 블로그 목록 칸을 갈아 끼운다."""
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

RSS_URL = "https://hypark.tistory.com/rss"
EXCLUDED_CATEGORIES = {"자격증"}  # README에 띄우지 않을 카테고리
MAX_POSTS = 5
README_PATH = "README.md"
START_MARK = "<!-- BLOG-POST-LIST:START -->"
END_MARK = "<!-- BLOG-POST-LIST:END -->"


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
            "url": item.findtext("link"),
            "date": parsedate_to_datetime(item.findtext("pubDate")).strftime("%Y.%m.%d"),
        })
    return posts[:MAX_POSTS]


def to_markdown(posts):
    # 한 줄 예: `2026.06.01` [글 제목](링크)<br>
    return "\n".join(f"`{post['date']}` [{post['title']}]({post['url']})<br>" for post in posts)


def main():
    with open(README_PATH, encoding="utf-8") as file:
        readme = file.read()

    new_block = f"{START_MARK}\n{to_markdown(fetch_tech_posts())}\n{END_MARK}"
    old_block_pattern = re.escape(START_MARK) + ".*?" + re.escape(END_MARK)
    updated = re.sub(old_block_pattern, lambda _: new_block, readme, flags=re.DOTALL)

    with open(README_PATH, "w", encoding="utf-8") as file:
        file.write(updated)


if __name__ == "__main__":
    main()
