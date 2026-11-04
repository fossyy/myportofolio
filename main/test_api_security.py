from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import Project


class ProjectApiSecurityTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Public project", description="Public description")
        self.regular_user = get_user_model().objects.create_user(
            username="regular", password="password"
        )

    def test_public_project_json_excludes_star_relationship(self):
        self.project.starred_by.add(self.regular_user)
        response = self.client.get(reverse("projects:api_detail", args=[self.project.pk]))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], self.project.title)
        self.assertEqual(data["star_count"], 1)
        self.assertEqual(data["starred_by_names"], "regular")
        self.assertNotIn("starred_by", data)
        self.assertNotIn("password", data)

    def test_project_collection_rejects_delete(self):
        response = self.client.delete(reverse("projects:api_list"))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_authenticated_users_can_toggle_star_only_with_post(self):
        star_url = reverse("projects:api_star", args=[self.project.pk])

        guest_response = self.client.post(star_url)
        self.assertEqual(guest_response.status_code, 403)
        self.assertFalse(self.project.starred_by.exists())

        self.client.force_login(self.regular_user)
        self.assertEqual(self.client.get(star_url).status_code, 405)
        response = self.client.post(star_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_starred"])
        self.assertTrue(self.project.starred_by.filter(pk=self.regular_user.pk).exists())

        response = self.client.post(star_url)
        self.assertFalse(response.json()["is_starred"])
        self.assertFalse(self.project.starred_by.filter(pk=self.regular_user.pk).exists())
