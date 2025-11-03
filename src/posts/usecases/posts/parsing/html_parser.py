# import random
import re
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup, Comment

from posts.dto.parse_posts import ParsedPostDTO, ParsedPostTagDTO


@dataclass
class ParseHtmlResponse:
    success: bool
    data: ParsedPostDTO | int
    error_message: str | None = None


def remove_comments(soup: BeautifulSoup):
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()


def parse_html(html: str) -> ParseHtmlResponse:
    post_id = "Неизвестный id (не получилосб извлечь из-за ошибки)"
    try:
        soup = BeautifulSoup(html, "lxml")
        remove_comments(soup)
        print_button = soup.select_one("#poteme + hr + a")
        match = re.search(r'href="([^"]*)"', str(print_button))

        print_button_href = match.group(1)  # type: ignore

        post_id = int(print_button_href.split("/")[2].split("-")[0])

        title = soup.title.string
        image = soup.select_one('link[rel="image_src"]')["href"]
        h1 = soup.find("h1").text
        description = soup.find("meta", attrs={"name": "description"})["content"]
        tags_elems = soup.find_all("a", class_="article-tag")

        tags = [
            ParsedPostTagDTO(slug=tag_element["href"].split("/")[-1].lower(), name=tag_element.text)
            for tag_element in tags_elems
        ]

        try:
            date = datetime.strptime(soup.select_one("i.icon-calendar + a")["href"].split("/")[-1], "%Y-%m-%d")
        except Exception as e:
            date = None

        content = str(soup.select_one("#content"))

        img_wrap = soup.select_one(".img_wrap")
        parent = img_wrap.parent
        img_wrap.decompose()

        content = "".join(str(x) for x in parent.contents)
        content = content.strip()

        content2 = str(soup)

        # post_id = random.randrange(1, 10_000_000)
        slug = re.sub(r"^\d+-", "", print_button_href.split("/")[2])

        return ParseHtmlResponse(
            success=True,
            data=ParsedPostDTO(
                title=title,
                h1=h1,
                image=image,
                description=description,
                tags=tags,
                content=content,
                content2=content2,
                id=post_id,
                slug=slug,
                published=date,
                active=True,
            ),
        )
    except Exception as e:
        type, value, tb = sys.exc_info()
        traceback_str = "".join(traceback.format_exception(type, value, tb))

        return ParseHtmlResponse(success=False, data=post_id, error_message=traceback_str)
