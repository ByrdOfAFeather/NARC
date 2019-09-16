from django.test import TestCase
import requests


class TestMobilePost(TestCase):
	def test_authentication(self):
		data = {"24095915": {"average_time_between_questions": 1000, "time_taken": 5, "page_leaves": 0.0,
		                     "name": "Test Student",
		                     "id": "24095915"},
		        "24120424": {"average_time_between_questions": 2000.0, "time_taken": 5, "page_leaves": 1.0,
		                     "name": "Tester Baxter", "id": "24120424"},
		        "24125413": {"average_time_between_questions": 4250.0, "time_taken": 23, "page_leaves": 3.0,
		                     "name": "Sora Ultimate", "id": "24125413"},
		        "24125422": {"average_time_between_questions": 2750.0, "time_taken": 34, "page_leaves": 4.0,
		                     "name": "Rico",
		                     "id": "24125422"}, "secret": "", "encryption_key": "", "storage": ""}
		url = "http://127.0.0.1:8000/api/post_mobile/"
		import json
		send = json.dumps(data)
		token = "a352db9c6e45a270ad9c05ac5a5fdc03a75b7dfd"
		response = requests.post(url, {"data": send}, headers={"Authorization": f"Token {token}"})

