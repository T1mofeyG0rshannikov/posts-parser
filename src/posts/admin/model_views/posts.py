from posts.admin.model_views.base import BaseModelView
from posts.persistence.models import PostOrm, PostTagOrm


class PostAdmin(BaseModelView, model=PostOrm):  # type: ignore
    column_list = [
        PostOrm.id,
        PostOrm.title,
        # PostOrm.description,
        PostOrm.published,
        # PostOrm.h1,
        # PostOrm.image,
        # PostOrm.content,
        # PostOrm.content2,
        PostOrm.slug,
        PostOrm.active,
    ]

    list_template = "sqladmin/list-posts.html"

    name = "Пост"
    name_plural = "Посты"


class PostTagAdmin(BaseModelView, model=PostTagOrm):  # type: ignore
    column_list = [PostTagOrm.id, PostTagOrm.name, PostTagOrm.slug, PostTagOrm.post]

    name = "Тег"
    name_plural = "Теги"
