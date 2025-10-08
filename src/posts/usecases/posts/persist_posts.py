from posts.dto.parse_posts import ParsedPostDTO
from posts.dto.post_tag_relation import PostTagRelation
from posts.persistence.data_mappers.posts_data_mapper import PostDataMapper
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper


class PersistPosts:
    """
    Сервис для сохранения парсенных постов и связанных тегов в базу данных.

    Данный класс выполняет пакетное сохранение постов (ParsedPostDTO)
    вместе с их тегами. Он отвечает только за синхронизацию данных
    и не делает commit — это обязанность внешнего компонента (ParsePosts), который управляет жизненным циклом
    транзакции и сессии.

    ---
    Параметры:
        post_data_mapper (PostDataMapper): Маппер, отвечающий за сохранение постов в БД.
        tag_data_mapper (TagDataMapper): Маппер, отвечающий за сохранение тегов и связей пост–тег.

    ---
    Аргументы вызова (__call__):
        posts (list[ParsedPostDTO]):
            Батч постов, полученных после парсинга HTML.
        tags_dict (dict[str, int]):
            Словарь {slug: id}, содержащий все известные теги.
            Используется для связывания новых постов с уже существующими тегами.
            Обновляется на месте при добавлении новых тегов.
        exist_tag_slugs (set[str]):
            Множество slug'ов уже существующих тегов.
            Также обновляется на месте при добавлении новых тегов.

    ---
    Примечания:
        - Метод НЕ вызывает commit(), так как не является атомарной операцией.
          Commit выполняется уровнем выше (оркестратором).
    """

    def __init__(self, post_data_mapper: PostDataMapper, tag_data_mapper: TagDataMapper) -> None:
        self._post_data_mapper = post_data_mapper
        self._tag_data_mapper = tag_data_mapper

    async def __call__(self, posts: list[ParsedPostDTO], tags_dict: dict[str, int]) -> None:
        parsed_tags = list({tag for post in posts for tag in post.tags})

        new_tags = [tag for tag in parsed_tags if tag.slug not in tags_dict]

        flushed_tags = await self._tag_data_mapper.bulk_save(new_tags)

        for tag in flushed_tags:
            tags_dict[tag.slug] = tag.id

        saved_posts = await self._post_data_mapper.bulk_save(posts)

        post_tag_relations: list[PostTagRelation] = []
        for post, saved_post in zip(posts, saved_posts):
            post_tag_relations.extend(
                [PostTagRelation(post_id=saved_post.id, tag_id=tags_dict[tag.slug]) for tag in post.tags]
            )

        await self._tag_data_mapper.bulk_save_post_relations(post_tag_relations)
