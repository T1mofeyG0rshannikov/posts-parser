from datetime import date, datetime, timedelta, timezone

from posts.dto.post import PostWithTags, Tag
from posts.dto.wordpress_post import WordpressPostDTO


class WordpressPostAdapter:
    @staticmethod
    def date_to_iso_format(d: date, hour=12, minute=0, second=0, tz_offset=3):
        """Преобразует date в ISO формат с указанным временем и временной зоной"""
        tz = timezone(timedelta(hours=tz_offset))
        dt = datetime.combine(d, datetime.min.time().replace(hour=hour, minute=minute, second=second), tzinfo=tz)
        return dt.isoformat()

    def execute(self, post: PostWithTags, wp_tags: list[Tag], featured_media: int) -> WordpressPostDTO:
        wp_tags_dict = {wp_tag.slug: wp_tag.id for wp_tag in wp_tags}
        tags = [wp_tags_dict[tag.slug.lower()] for tag in post.tags if tag.slug.lower() in wp_tags_dict]
        return WordpressPostDTO(
            title=post.title,
            content=post.content,
            featured_media=featured_media,
            description=post.description,
            image_name=f"{post.id}.jpg",
            tags=tags,
            date=self.date_to_iso_format(post.published),
            h1=post.h1,
            slug=WordpressPostDTO.generate_slug(post),
        )
