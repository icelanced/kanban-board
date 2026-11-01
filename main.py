import os

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="KanbanBoard")


class Card(BaseModel):
    title: str
    description: str | None = Field(default=None, max_length=2000)

class CardUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200, pattern=r"\S")


def connect():
    return psycopg.connect(os.environ["DATABASE_URL"])


@app.get("/health")
def health():
    return {"status": "ok", "project": "KanbanBoard"}


@app.post("/cards")
def create_card(card: Card):
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cards "
            "(id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, "
            "title TEXT NOT NULL, description TEXT)"
        )
        row = conn.execute(
            "INSERT INTO cards (title, description) "
            "VALUES (%s, %s) RETURNING id, title, description",
            (card.title, card.description),
        ).fetchone()
    return {"id": row[0], "title": row[1], "description": row[2]}


@app.get("/cards")
def list_cards():
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cards "
            "(id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, "
            "title TEXT NOT NULL, description TEXT)"
        )
        rows = conn.execute(
            "SELECT id, title, description FROM cards ORDER BY id"
        ).fetchall()
    return [
        {"id": row[0], "title": row[1], "description": row[2]}
        for row in rows
    ]


@app.patch("/cards/{card_id}")
def rename_card(card_id: int, card: CardUpdate):
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cards "
            "(id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, title TEXT NOT NULL)"
        )
        row = conn.execute(
            "UPDATE cards SET title = %s WHERE id = %s "
            "RETURNING id, title, description",
            (card.title, card_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Card not found")
    return {"id": row[0], "title": row[1], "description": row[2]}
