from dataclasses import dataclass


@dataclass
class PostTagRelation:
    post_id: int
    tag_id: int
