from posts.usecases.posts.parsing.parsers.base import ParsePosts
from posts.usecases.posts.send_to_site.usecase import SendPostsToSites


class ParsePostsAndSendToSites:
    def __init__(self, parse_posts: ParsePosts, send_posts: SendPostsToSites):
        self._parse_posts = parse_posts
        self._send_posts = send_posts

    async def __call__(self):
        parse_response = await self._parse_posts()
        print("Отправляем посты на сайты...")
        await self._send_posts()
        print("Все посты отправлены...")

        return parse_response
