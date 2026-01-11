from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from uuid import uuid4


User = get_user_model()


class UmsAPITests(APITestCase):
	def setUp(self):
		# create a superuser to authenticate requests requiring IsSuperUser
		self.superuser = User.objects.create_superuser(
			username="admin",
			email="admin@example.com",
			password="adminpass",
		)
		self.client.force_authenticate(self.superuser)

	def test_register_creates_user(self):
		url = "/api/ums/register/"
		data = {
			"username": "newuser",
			"email": "newuser@example.com",
			"password": "pass1234",
			"role": "MEMBER",
		}
		resp = self.client.post(url, data, format="json")
		self.assertEqual(resp.status_code, 201)
		self.assertIn("user_id", resp.data)
		# user exists in DB
		self.assertTrue(User.objects.filter(id=resp.data["user_id"]).exists())

	def test_delete_user_success(self):
		target = User.objects.create_user(username="t1", password="pw", email="t1@example.com")
		url = f"/api/ums/delete/{target.id}/"
		resp = self.client.delete(url)
		self.assertEqual(resp.status_code, 200)
		self.assertFalse(User.objects.filter(id=target.id).exists())

	def test_delete_self_forbidden(self):
		url = f"/api/ums/delete/{self.superuser.id}/"
		resp = self.client.delete(url)
		self.assertEqual(resp.status_code, 403)
		self.assertIn("error", resp.data)

	def test_delete_nonexistent_returns_404(self):
		random_id = uuid4()
		url = f"/api/ums/delete/{random_id}/"
		resp = self.client.delete(url)
		self.assertEqual(resp.status_code, 404)

	def test_cannot_delete_superuser(self):
		other_super = User.objects.create_superuser(username="su2", email="su2@example.com", password="pw2")
		url = f"/api/ums/delete/{other_super.id}/"
		resp = self.client.delete(url)
		self.assertEqual(resp.status_code, 403)

	def test_list_users_pagination(self):
		# create multiple users to exercise pagination and ordering
		created = []
		for i in range(15):
			u = User.objects.create_user(username=f"u{i}", password="pw", email=f"u{i}@ex.com")
			created.append(u)

		url = "/api/ums/users/?page=1&page_size=10"
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertIn("count", resp.data)
		self.assertIn("total_pages", resp.data)
		self.assertIn("current_page", resp.data)
		self.assertIn("results", resp.data)
		self.assertEqual(resp.data["count"], User.objects.count())
		self.assertEqual(resp.data["current_page"], 1)
		self.assertEqual(len(resp.data["results"]), 10)
