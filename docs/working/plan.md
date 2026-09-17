# Рабочий план

Внутренний документ команды. Правим по ходу работы; официальная версия
требований — в `docs/official/lab01-tech-spec.pdf`.

## 1. Статус

- [x] Лаб. №1 — техническое задание
- [ ] Каркас серверной части (FastAPI) и подключение к PostgreSQL
- [ ] Модели SQLAlchemy и первая миграция Alembic
- [ ] Регистрация и авторизация (ФКД-001)
- [ ] Доски, участники, колонки, WIP-лимиты (ФКД-002, ФКД-003)
- [ ] Карточки задач и перемещение (ФКЗ-001 … ФКЗ-003)
- [ ] Исполнители, метки, фильтры, комментарии (ФКЗ-004 … ФКЗ-006)
- [ ] Сроки и архив (ФКЗ-007)
- [ ] История перемещений, метрики, журнал действий (ФХД-002 … ФХД-004)
- [ ] Клиентская часть на React с drag-and-drop (ТПО-004, ТПО-005)

Порядок пунктов сверим с методичками по лабораторным, когда получим их все.

## 2. Архитектура

Клиент-сервер (ТСФ-002):

```
Браузер (React + TypeScript)
        │  HTTP(S), REST API, JWT
        ▼
FastAPI (src/kanban_board)
  ├── api/      — роуты
  ├── services/ — бизнес-логика (WIP-лимиты, перемещения, права)
  └── db/       — модели SQLAlchemy
        │
        ▼
PostgreSQL (схема версионируется через Alembic)
```

Перемещение карточки — одна транзакция (ТН-001): меняем колонку и
позицию карточки, сдвигаем позиции соседей и пишем запись в историю.

## 3. Черновая схема БД

| Таблица | Основные поля |
| --- | --- |
| `users` | id, email, password_hash, name, created_at |
| `refresh_tokens` | id, user_id, token_hash, expires_at |
| `boards` | id, title, owner_id, created_at |
| `board_members` | board_id, user_id, role (owner / member) |
| `columns` | id, board_id, title, position, wip_limit (nullable) |
| `cards` | id, board_id, column_id, title, description, priority, due_date, position, assignee_id, created_by, archived_at |
| `labels` | id, board_id, name, color |
| `card_labels` | card_id, label_id |
| `comments` | id, card_id, author_id, text, created_at |
| `card_moves` | id, card_id, from_column_id, to_column_id, moved_by, moved_at |
| `audit_log` | id, board_id, user_id, action, entity, entity_id, created_at |

`card_moves` только дополняется (ФХД-002), из неё считаются lead time и
cycle time (ФХД-003).

## 4. Открытые вопросы

- WIP-лимит: только предупреждать (как в ТЗ, ФКД-003) или ещё и запрещать перемещение?
- Какие колонки считать «в работе» для cycle time: задавать флагом на колонке?
- Где развернуть сервер и PostgreSQL для демонстрации.
- Распределение зон ответственности между участниками (ТОО-001).
