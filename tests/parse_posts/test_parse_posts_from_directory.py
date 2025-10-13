import pytest
from parse_posts.fixtures import * # type: ignore

from posts.dto.parse_posts import ParseUsecaseResponse


@pytest.mark.parametrize(
    "path, expected_result",
    [
        ("data/articles", ParseUsecaseResponse(skipped=0, inserted=3)),
        ("data/articles_with_repeats", ParseUsecaseResponse(skipped=1, inserted=3)),
    ],
)
async def test_parse_posts_from_directory(parse_posts_from_directory, path, expected_result):
    parse_posts_from_directory._config.DATA_DIR = path
    response = await parse_posts_from_directory()

    assert response == expected_result
