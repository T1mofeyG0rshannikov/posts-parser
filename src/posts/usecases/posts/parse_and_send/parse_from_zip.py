from zipfile import ZipFile

from posts.usecases.posts.parse_and_send.base import ParsePostsAndSendToSites
from posts.usecases.posts.parsing.parsers.zip_parser import ParsePostsFromZIP
from posts.usecases.posts.send_to_site.usecase import SendPostsToSites


class ParsePostsFromZIPAndSendToSites(ParsePostsAndSendToSites):
    def __init__(self, parse_posts: ParsePostsFromZIP, send_posts: SendPostsToSites):
        super().__init__(parse_posts=parse_posts, send_posts=send_posts)

    async def __call__(self, zip_file: ZipFile):
        parse_response = await self._parse_posts(zip_file)
        print("Отправляем посты на сайты...")
        await self._send_posts()
        print("Все посты отправлены...")

        return parse_response
