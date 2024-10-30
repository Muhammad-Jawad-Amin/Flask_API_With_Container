import json
import unittest
from app import app


class APITestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client for the Flask app."""
        self.client = app.test_client()
        self.client.testing = True

    def test_get_all_records(self):
        """Test retrieving all records."""
        response = self.client.get("/getallrecords")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)

    def test_get_record_by_id(self):
        """Test retrieving a specific record by ID."""
        response = self.client.get("/getrecord/0")
        if response.status_code == 200:
            data = response.get_json()
            self.assertEqual(data["status"], "success")
            self.assertIn("data", data)
        else:
            self.assertEqual(response.status_code, 404)

    def test_post_record(self):
        """Test adding a new record."""
        new_record = {"Longitude": -179.1, "Latitude": 68.0, "PM2.5_Level": 2.8}
        response = self.client.post(
            "/addrecord", data=json.dumps(new_record), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("id", data["data"])

    def test_put_record(self):
        """Test updating an existing record by ID."""
        update_data = {"PM2.5_Level": 3.1}
        response = self.client.put(
            "/updaterecord/0",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        if response.status_code == 200:
            data = response.get_json()
            self.assertEqual(data["status"], "success")
            self.assertIn("data", data)
            self.assertEqual(data["data"]["PM2.5_Level"], 3.1)
        else:
            self.assertEqual(response.status_code, 404)

    def test_delete_record(self):
        """Test deleting a specific record by ID."""
        response = self.client.delete("/deleterecord/0")
        if response.status_code == 200:
            data = response.get_json()
            self.assertEqual(data["status"], "success")
            self.assertIn("data", data)
        else:
            self.assertEqual(response.status_code, 404)

    def test_filter_records(self):
        """Test filtering records by latitude and longitude."""
        response = self.client.get("/records/filter?lat=68.0&long=-179.1")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)

    def test_get_stats(self):
        """Test retrieving statistics on PM2.5 levels."""
        response = self.client.get("/records/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("count", data["data"])
        self.assertIn("average_PM2.5", data["data"])
        self.assertIn("max_PM2.5", data["data"])
        self.assertIn("min_PM2.5", data["data"])


if __name__ == "__main__":
    unittest.main()
