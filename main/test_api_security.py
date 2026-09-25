from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from main.models import Project


class ProjectApiSecurityTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Public project", description="Public description")
        self.regular_user = get_user_model().objects.create_user(
            username="regular", password="password"
        )

    def test_public_project_json_excludes_star_relationship(self):
        self.project.starred_by.add(self.regular_user)
        response = self.client.get(reverse("main:project_api", args=[self.project.title]))

        self.assertEqual(response.status_code, 200)
        fields = response.json()[0]["fields"]
        self.assertEqual(fields["title"], self.project.title)
        self.assertNotIn("starred_by", fields)
        self.assertNotIn("password", fields)

    def test_project_collection_rejects_delete(self):
        response = self.client.delete(reverse("main:projects_api"))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_authenticated_users_can_toggle_star_only_with_post(self):
        star_url = reverse("main:toggle_star", args=[self.project.pk])

        guest_response = self.client.post(star_url)
        self.assertEqual(guest_response.status_code, 302)
        self.assertFalse(self.project.starred_by.exists())

        self.client.force_login(self.regular_user)
        self.assertEqual(self.client.get(star_url).status_code, 405)
        response = self.client.post(star_url)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(self.project.starred_by.filter(pk=self.regular_user.pk).exists())

        self.client.post(star_url)
        self.assertFalse(self.project.starred_by.filter(pk=self.regular_user.pk).exists())
