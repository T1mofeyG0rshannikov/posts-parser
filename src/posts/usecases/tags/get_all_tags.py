from posts.dto.post import Tag
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper


class FilterTags:
    def __init__(self, tag_data_mapper: TagDataMapper) -> None:
        self._data_mapper = tag_data_mapper

    async def __call__(self, search: str) -> list[Tag]:
        return await self._data_mapper.filter_by_search(search)
