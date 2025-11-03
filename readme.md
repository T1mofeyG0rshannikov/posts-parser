# HTML Posts parser

Серверное приложение для массового парсинга постов из HTML и сохранения их в базу данных

## Стек
- Python 3.11, FastAPI
- SQLAlchemy, Sqladmin, PostgreSQL
- Pytest


## Руководство по использованию

### Создание администратора (консольная команда):

```bash
source your_env
cd src
python -m posts.cli.create_admin_user
```


### Создание администратора (консольная команда):

```bash
source your_env
cd src
python -m posts.sync_from_directory
```

### Описание процедуры запуска парсинга

В .env файле указывается путь к директории с html постами

далее запускается скрипт

```bash
source your_env
cd src
python -m posts.cli.parse_posts_from_directory
```

В админ панели можно загрузить посты ZIP архивом на соответствующей странице
