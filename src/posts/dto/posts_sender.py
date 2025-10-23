from dataclasses import dataclass


@dataclass
class PostsSenderResponse:
    success_sended_posts_ids: list[int]
    error_sended_posts_ids: list[int]
