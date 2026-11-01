import unittest

from fastapi.testclient import TestClient

from main import app, connect


class CardRenameTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        response = self.client.post('/cards', json={'title': 'Initial task'})
        self.assertEqual(response.status_code, 200)
        self.card = response.json()
        self.addCleanup(self.remove_test_card)

    def remove_test_card(self):
        with connect() as connection:
            connection.execute('DELETE FROM cards WHERE id = %s', (self.card['id'],))

    def test_rename_card_and_read_list(self):
        response = self.client.patch(
            f"/cards/{self.card['id']}", json={'title': 'Updated task'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'id': self.card['id'],
                'title': 'Updated task',
                'description': None,
            },
        )
        cards = self.client.get('/cards').json()
        self.assertIn(response.json(), cards)
        self.assertNotIn(self.card, cards)

    def test_rename_is_saved_in_postgresql(self):
        response = self.client.patch(
            f"/cards/{self.card['id']}", json={'title': 'Saved title'}
        )
        self.assertEqual(response.status_code, 200)
        with connect() as connection:
            row = connection.execute(
                'SELECT title FROM cards WHERE id = %s', (self.card['id'],)
            ).fetchone()
        self.assertEqual(row[0], 'Saved title')

    def test_missing_card_returns_404(self):
        response = self.client.patch('/cards/2147483647', json={'title': 'Missing task'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Card not found'})

    def test_invalid_titles_are_rejected_without_changing_card(self):
        for title in ('', '   ', 'x' * 201, None, 42):
            with self.subTest(title=title):
                response = self.client.patch(
                    f"/cards/{self.card['id']}", json={'title': title}
                )
                self.assertEqual(response.status_code, 422)
        self.assertIn(self.card, self.client.get('/cards').json())

    def test_existing_health_create_and_list_still_work(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok', 'project': 'KanbanBoard'})
        self.assertIn(self.card, self.client.get('/cards').json())

    def test_description_is_saved_and_preserved_after_rename(self):
        description = 'Description for Lab8'
        response = self.client.post(
            '/cards',
            json={'title': 'Description task', 'description': description},
        )
        self.assertEqual(response.status_code, 200)
        card = response.json()

        def cleanup():
            with connect() as connection:
                connection.execute(
                    'DELETE FROM cards WHERE id = %s', (card['id'],)
                )

        self.addCleanup(cleanup)
        self.assertEqual(card['description'], description)
        self.assertIn(card, self.client.get('/cards').json())

        with connect() as connection:
            row = connection.execute(
                'SELECT description FROM cards WHERE id = %s',
                (card['id'],),
            ).fetchone()
        self.assertEqual(row[0], description)

        response = self.client.patch(
            f"/cards/{card['id']}", json={'title': 'Renamed description task'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['description'], description)
        self.assertIn(response.json(), self.client.get('/cards').json())
if __name__ == '__main__':
    unittest.main()
