import unittest

from pydantic import ValidationError

from main import CardUpdate, health


class HealthUnitTests(unittest.TestCase):
    def test_health_returns_expected_status(self):
        self.assertEqual(
            health(),
            {"status": "ok", "project": "KanbanBoard"},
        )


class CardUpdateUnitTests(unittest.TestCase):
    def test_valid_title_is_preserved(self):
        card = CardUpdate(title="Новая задача")
        self.assertEqual(card.title, "Новая задача")

    def test_title_length_boundaries_are_accepted(self):
        for title in ("x", "x" * 200):
            with self.subTest(length=len(title)):
                self.assertEqual(CardUpdate(title=title).title, title)

    def test_invalid_titles_are_rejected(self):
        for title in ("", "   ", "\t\n", "x" * 201, None, 42):
            with self.subTest(title=title):
                with self.assertRaises(ValidationError):
                    CardUpdate(title=title)

    def test_missing_title_is_rejected(self):
        with self.assertRaises(ValidationError):
            CardUpdate()


if __name__ == "__main__":
    unittest.main()
