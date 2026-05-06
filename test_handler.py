import json
import unittest
from unittest.mock import MagicMock, patch


# Mock boto3 before importing handler
import sys
sys.modules["boto3"] = MagicMock()

from src.handler import lambda_handler, create_task, get_all_tasks, delete_task


def make_event(method, body=None, path_params=None):
    return {
        "httpMethod": method,
        "pathParameters": path_params,
        "body": json.dumps(body) if body else None,
    }


class TestCreateTask(unittest.TestCase):

    @patch("src.handler.get_table")
    def test_create_task_success(self, mock_get_table):
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table

        body = {"title": "Buy groceries", "description": "Milk and eggs"}
        result = create_task(body)

        self.assertEqual(result["statusCode"], 201)
        data = json.loads(result["body"])
        self.assertEqual(data["title"], "Buy groceries")
        self.assertEqual(data["status"], "pending")
        self.assertIn("id", data)

    @patch("src.handler.get_table")
    def test_create_task_missing_title(self, mock_get_table):
        result = create_task({"description": "No title here"})
        self.assertEqual(result["statusCode"], 400)
        data = json.loads(result["body"])
        self.assertIn("error", data)


class TestGetAllTasks(unittest.TestCase):

    @patch("src.handler.get_table")
    def test_get_all_tasks(self, mock_get_table):
        mock_table = MagicMock()
        mock_table.scan.return_value = {
            "Items": [
                {"id": "123", "title": "Task 1", "status": "pending"},
                {"id": "456", "title": "Task 2", "status": "done"},
            ]
        }
        mock_get_table.return_value = mock_table

        result = get_all_tasks()
        self.assertEqual(result["statusCode"], 200)
        data = json.loads(result["body"])
        self.assertEqual(len(data["tasks"]), 2)


class TestDeleteTask(unittest.TestCase):

    @patch("src.handler.get_table")
    def test_delete_existing_task(self, mock_get_table):
        mock_table = MagicMock()
        mock_table.get_item.return_value = {"Item": {"id": "123", "title": "Task"}}
        mock_get_table.return_value = mock_table

        result = delete_task("123")
        self.assertEqual(result["statusCode"], 200)

    @patch("src.handler.get_table")
    def test_delete_nonexistent_task(self, mock_get_table):
        mock_table = MagicMock()
        mock_table.get_item.return_value = {}
        mock_get_table.return_value = mock_table

        result = delete_task("nonexistent-id")
        self.assertEqual(result["statusCode"], 404)


class TestLambdaHandler(unittest.TestCase):

    @patch("src.handler.get_table")
    def test_invalid_route(self, mock_get_table):
        event = make_event("PATCH")
        result = lambda_handler(event, {})
        self.assertEqual(result["statusCode"], 400)


if __name__ == "__main__":
    unittest.main()
