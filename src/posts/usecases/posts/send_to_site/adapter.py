from posts.dto.post import PostWithTags, Tag
from posts.dto.wordpress_post import WordpressPostDTO


class WordpressPostAdapter:
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
            publish=post.published.isoformat(),
            h1=post.h1,
            slug=WordpressPostDTO.generate_slug(post),
        )
