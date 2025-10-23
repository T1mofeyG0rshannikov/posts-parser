import io
from pathlib import Path
from zipfile import ZipFile

import pytest
from parse_posts.fixtures import *  # type: ignore

from posts.dto.parse_posts import ParseUsecaseResponse


def get_unique_new_posts_zip_data() -> ZipFile:
    dir_path = Path(__file__).parent.parent / "data" / "articles"
    zip_bytes = io.BytesIO()

    with ZipFile(zip_bytes, "w") as zip_file:
        for file_path in dir_path.glob("*.html"):
            zip_file.write(file_path, arcname=file_path.name)

    zip_bytes.seek(0)
    return ZipFile(zip_bytes)


def get_new_posts_with_invalid_zip_data() -> ZipFile:
    dir_path = Path(__file__).parent.parent / "data" / "articles_with_invalid"
    zip_bytes = io.BytesIO()

    with ZipFile(zip_bytes, "w") as zip_file:
        for file_path in dir_path.glob("*.html"):
            zip_file.write(file_path, arcname=file_path.name)

    zip_bytes.seek(0)
    return ZipFile(zip_bytes)


def get_new_posts_with_repeat_zip_data() -> ZipFile:
    dir_path = Path(__file__).parent.parent / "data" / "articles"
    files = list(dir_path.glob("*.html"))

    zip_bytes = io.BytesIO()
    with ZipFile(zip_bytes, "w") as zip_file:
        zip_file.write(files[0], arcname="0.html")
        zip_file.write(files[1], arcname="1.html")
        zip_file.write(files[1], arcname="2.html")

    zip_bytes.seek(0)
    return ZipFile(zip_bytes)


@pytest.mark.parametrize(
    "zip_data, expected_result",
    [
        (get_unique_new_posts_zip_data(), ParseUsecaseResponse(skipped=0, inserted=3, invalid=0)),
        (get_new_posts_with_repeat_zip_data(), ParseUsecaseResponse(skipped=1, inserted=2, invalid=0)),
        (get_new_posts_with_invalid_zip_data(), ParseUsecaseResponse(skipped=0, inserted=2, invalid=1)),
    ],
)
async def test_parse_posts_from_zip(parse_posts_from_zip, zip_data, expected_result):
    response = await parse_posts_from_zip(zip_data)

    assert response == expected_result
