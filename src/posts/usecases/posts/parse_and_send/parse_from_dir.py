from posts.usecases.posts.parse_and_send.base import ParsePostsAndSendToSites
from posts.usecases.posts.parsing.parsers.directory_parser import (
    ParsePostsFromDirectory,
)
from posts.usecases.posts.send_to_site.usecase import SendPostsToSites


class ParsePostsFromDirctoryAndSendToSites(ParsePostsAndSendToSites):
    def __init__(self, parse_posts: ParsePostsFromDirectory, send_posts: SendPostsToSites):
        super().__init__(parse_posts=parse_posts, send_posts=send_posts)
