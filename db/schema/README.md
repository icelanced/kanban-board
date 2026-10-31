# KanbanBoard database schema

schema.sql will contain the current PostgreSQL application schema.
Export it with pg_dump --schema-only --no-owner --no-privileges.
Update this snapshot whenever the application schema changes.

Migration history is stored separately from this schema snapshot.
