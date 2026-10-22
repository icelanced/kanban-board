# KanbanBoard

Учебный проект по дисциплине «Автоматизация процессов жизненного цикла
программных средств» (Московский Политех, группа 241-327).

Разрабатываем веб-сервис управления задачами по методологии Канбан:
доски с колонками, карточки задач с drag-and-drop, WIP-лимиты,
исполнители, метки, комментарии и история перемещений карточек
для расчёта lead time и cycle time.

## Команда

- Ночной Максим Сергеевич
- Пахалюк Илья Николаевич
- Сапрыкин Пётр Иванович

## Документация

- [Техническое задание — лабораторная работа №1](docs/official/lab01-tech-spec.pdf)
- [Рабочий план проекта](docs/working/plan.md)
- [Правила ведения документации](docs/README.md)

## Текущее состояние

Выполнены практические части лабораторных работ №2 и №3:

- Созданы виртуальные машины для стендов test, stage и prod.
- Подготовлен прототип API на Python и FastAPI.
- Добавлен Dockerfile для сборки образа приложения.
- Настроен запуск API и PostgreSQL через Docker Compose.
- Реализованы создание и чтение карточек в PostgreSQL.
- Проверено сохранение данных после удаления и повторного создания контейнеров.

Прототип поддерживает создание, просмотр и переименование карточек.
Доски, колонки, drag-and-drop, WIP-лимиты и остальные функции
из технического задания будут реализованы в следующих лабораторных работах.

## Стек

В текущем прототипе используются:

- Python 3.14 и FastAPI;
- PostgreSQL 17;
- Psycopg для подключения к БД;
- Docker и Docker Compose.

По техническому заданию также запланированы SQLAlchemy,
Alembic для миграций и клиентская часть на TypeScript и React.

## Структура репозитория

```text
kanban-board/
├── main.py                — прототип API
├── requirements.txt       — зависимости Python
├── Dockerfile             — сборка образа приложения
├── docker-compose.yaml    — запуск API и PostgreSQL
├── .gitignore             — исключения для Git
├── README.md              — описание проекта и инструкция запуска
└── docs/
    ├── README.md          — правила ведения документации
    ├── official/          — официальные документы
    └── working/           — рабочий план и заметки
```

## Запуск через Docker Compose

Для запуска нужны Docker Engine и Docker Compose.

В корне проекта создайте файл `.env`:

```dotenv
POSTGRES_DB=kanban
POSTGRES_USER=kanban
POSTGRES_PASSWORD=укажите_свой_пароль
```

Для пароля используйте латинские буквы и цифры.
Файл `.env` исключён из Git и не должен попадать в репозиторий.

Соберите образы и запустите сервисы:

```bash
docker compose up -d --build
```

В Linux при необходимости добавляйте `sudo` перед командами Docker.

Проверьте состояние сервисов:

```bash
docker compose ps
```

API доступен по адресу `http://localhost:8002`.
Интерактивная документация API: `http://localhost:8002/docs`.

## Маршруты API

| Метод | Маршрут | Назначение |
|---|---|---|
| GET | `/health` | Проверка работы API |
| POST | `/cards` | Создание карточки в PostgreSQL |
| GET | `/cards` | Получение списка карточек |
| PATCH | `/cards/{card_id}` | Переименование карточки |

Примеры запросов для терминала Linux:

```bash
curl http://localhost:8002/health

curl -X POST http://localhost:8002/cards \
  -H "Content-Type: application/json" \
  -d '{"title":"Первая задача"}'

curl http://localhost:8002/cards
```

## Остановка и сохранение данных

Остановить сервисы и удалить контейнеры:

```bash
docker compose down
```

Запустить их снова:

```bash
docker compose up -d
```

Данные PostgreSQL хранятся в постоянном томе `postgres_data`
и сохраняются после выполнения `docker compose down`.

Команда `docker compose down -v` удаляет том вместе с данными БД.

## Просмотр логов

Вывод всех сервисов:

```bash
docker compose logs -f
```

Вывод только API:

```bash
docker compose logs -f api
```

Ctrl+C завершает просмотр логов, контейнеры продолжают работать.

## Лабораторная работа 5

Добавили переименование карточки: `PATCH /cards/{card_id}` принимает новое
название и сохраняет его в PostgreSQL. Если карточки нет, вернётся 404.
Пустое название, строка из пробелов и название длиннее 200 символов
не принимаются: вернётся 422.

```bash
curl -X PATCH http://localhost:8002/cards/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Обновлённая задача"}'
```

Изменения делаем в feature-ветке от dev. После успешной сборки создаём
pull request в dev и просим другого участника команды проверить код.
После согласования и слияния TeamCity собирает dev, публикует образ
в Docker Hub и запускает его на stage через SSH Exec.

TeamCity Server и агент работают в Docker на исходной VirtualBox-ВМ
kanban-test (192.168.56.11), приложение и PostgreSQL — на kanban-stage
(192.168.56.12). Сеть между стендами — kanban-lab.

В `/home/student/kanban-stage` находятся `compose.yaml` (копия
`stage.compose.yaml`) и `.env`:

```dotenv
POSTGRES_DB=kanban
POSTGRES_USER=kanban
POSTGRES_PASSWORD=123Qwerty
KANBAN_IMAGE=petruccio2006/kanban-board:dev
```

Для ручного запуска на stage:

```bash
cd /home/student/kanban-stage
docker compose pull
docker compose up -d --wait
curl http://localhost:8005/health
curl http://localhost:8005/cards
```

При автоматическом развёртывании TeamCity записывает в `KANBAN_IMAGE`
уникальный тег текущей сборки вместо общего dev. Данные базы хранятся
в именованном томе и сохраняются при обновлении API.

Для запуска тестов нужен доступ к PostgreSQL. Из папки проекта скопируем
тесты в работающий контейнер API и запустим их. Для проекта stage:

```bash
docker cp tests kanban-stage-api-1:/app/tests
docker exec kanban-stage-api-1 python -m unittest discover -s /app/tests -v
```

В CI тесты так же копируются в отдельный тестовый контейнер API;
для каждого запуска используется своя временная база.

Пять тестов проверяют переименование, чтение обновлённой карточки, запись
в PostgreSQL, ответы 404 и 422, а также прежние методы health/create/list.
Тестовые карточки удаляются после каждого теста.
