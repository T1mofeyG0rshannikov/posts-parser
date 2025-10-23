from posts.admin.model_views.base import BaseModelView
from posts.persistence.models import SitePostOrm


class SitePostAdmin(BaseModelView, model=SitePostOrm):
    column_list = [SitePostOrm.id, SitePostOrm.post, SitePostOrm.site, SitePostOrm.sended]

    name = "Пост на сайте"
    name_plural = "Пост на сайте"

    column_default_sort = ("id", "desc")
