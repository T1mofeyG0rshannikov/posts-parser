from fastapi import FastAPI

from posts.admin.admin import CustomAdmin
from posts.admin.model_views.error_log import ErrorLogAdmin
from posts.admin.model_views.post import PostAdmin
from posts.admin.model_views.site import SiteAdmin
from posts.admin.model_views.site_post import SitePostAdmin
from posts.admin.model_views.tag import TagAdmin
from posts.di import get_sync_container


def init_admin(app: FastAPI) -> None:
    container = get_sync_container(app)
    admin = container.get(CustomAdmin)
    admin.add_view(PostAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(ErrorLogAdmin)
    admin.add_view(SiteAdmin)
    admin.add_view(SitePostAdmin)
