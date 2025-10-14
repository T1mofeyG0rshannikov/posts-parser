import pytz
from markupsafe import Markup

from posts.admin.model_views.base import BaseModelView
from posts.persistence.models import ErrorLogOrm


class ErrorLogAdmin(BaseModelView, model=ErrorLogOrm):
    column_list = [
        ErrorLogOrm.title,
        ErrorLogOrm.message,
        ErrorLogOrm.created_at,
    ]

    name = "Ошибка"
    name_plural = "Ошибки"

    column_formatters = {
        ErrorLogOrm.message: lambda m, a: Markup(f"<pre>{m.message}</pre>" if m.message else ""),
        ErrorLogOrm.created_at: lambda log, _: log.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d.%m.%Y %H:%M:%S"
        ),
    }

    column_default_sort = ("id", "desc")
