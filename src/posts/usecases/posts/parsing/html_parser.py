# import random
import re
from datetime import datetime

from bs4 import BeautifulSoup

from posts.usecases.posts.parsing.dto import ParsedPostDTO, ParsedPostTagDTO


def parse_html(html: str) -> ParsedPostDTO:
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.string
    image = soup.select_one('link[rel="image_src"]')["href"]
    h1 = soup.find("h1").text
    description = soup.find("meta", attrs={"name": "description"})["content"]
    tags_elems = soup.select_one("#poteme").find_all("a")

    tags = [
        ParsedPostTagDTO(slug=tag_element["href"].split("/")[-1].split("-")[1], name=tag_element.text)
        for tag_element in tags_elems
    ]

    content = str(soup.select_one("#content"))

    print_button = soup.select_one("#poteme + hr + a")
    match = re.search(r'href="([^"]*)"', str(print_button))
    print_button_href = match.group(1)  # type: ignore

    post_id = int(print_button_href.split("/")[2].split("-")[0])
    # post_id = random.randrange(1, 10_000_000)
    slug = print_button_href.split("/")[2].split("-")[1]

    date = datetime.strptime(soup.select_one("i.icon-calendar + a")["href"].split("/")[-1], "%Y-%M-%d")

    return ParsedPostDTO(
        title=title,
        h1=h1,
        image=image,
        description=description,
        tags=tags,
        content=content,
        content2=content,
        id=post_id,
        slug=slug,
        published=date,
        active=True,
    )
