from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from projects.models import Project


class ProjectApiTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_superuser(
            username="owner", email="owner@example.com", password="test-password"
        )
        self.visitor = user_model.objects.create_user(
            username="visitor", email="visitor@example.com", password="test-password"
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.project = Project.objects.create(
            title="Portfolio API", description="A project description."
        )
        self.list_url = reverse("projects:api_list")
        self.detail_url = reverse("projects:api_detail", args=[self.project.pk])
        self.star_url = reverse("projects:api_star", args=[self.project.pk])
        self.payload = {
            "title": "New project",
            "description": "A new project description.",
            "source_url": "https://example.com/source",
            "live_url": "https://example.com/live",
        }
        self.client = APIClient()

    def test_public_list_detail_and_title_search(self):
        self.project.starred_by.add(self.visitor)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.project.pk)
        self.assertEqual(response.data[0]["star_count"], 1)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("email", response.data[0])
        self.assertNotIn("starred_by", response.data[0])

        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["title"], self.project.title)

        matching = self.client.get(self.list_url, {"title": "portfolio"})
        missing = self.client.get(self.list_url, {"title": "unmatched"})
        self.assertEqual(len(matching.data), 1)
        self.assertEqual(missing.data, [])

    def test_owner_can_create_and_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 99,
                "is_starred": True,
                "starred_by_names": "forged",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertTrue(Project.objects.filter(title="New project").exists())

    def test_serializer_strips_markup_and_rejects_invalid_data(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "title": " <b>Clean title</b> ", "description": "<i>Text</i>"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Clean title")
        self.assertEqual(response.data["description"], "Text")

        invalid_title = self.client.post(
            self.list_url, {**self.payload, "title": "<b></b>"}, format="json"
        )
        invalid_url = self.client.post(
            self.list_url, {**self.payload, "source_url": "not a URL"}, format="json"
        )
        self.assertEqual(invalid_title.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", invalid_title.data)
        self.assertEqual(invalid_url.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("source_url", invalid_url.data)

    def test_owner_can_put_patch_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        patched = self.client.patch(
            self.detail_url, {"title": "Patched title"}, format="json"
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(patched.data["title"], "Patched title")

        replaced = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(replaced.status_code, status.HTTP_200_OK)
        self.assertEqual(replaced.data["source_url"], self.payload["source_url"])

        deleted = self.client.delete(self.detail_url)
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deleted.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.visitor.groups.add(self.editor_group)
        self.client.force_authenticate(user=self.visitor)

        patched = self.client.patch(
            self.detail_url, {"title": "Editor update"}, format="json"
        )
        created = self.client.post(self.list_url, self.payload, format="json")
        deleted = self.client.delete(self.detail_url)

        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_editor_can_replace_project_with_put(self):
        self.visitor.groups.add(self.editor_group)
        self.client.force_authenticate(user=self.visitor)

        response = self.client.put(self.detail_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.payload["title"])
        self.assertEqual(response.data["description"], self.payload["description"])

    def test_detail_rejects_unsupported_post_method(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.detail_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Project.objects.count(), 1)

    def test_malformed_json_returns_bad_request(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.generic(
            "POST", self.list_url, b'{"title":', content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Project.objects.count(), 1)

    def test_guest_and_regular_user_cannot_manage_projects(self):
        guest_create = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(guest_create.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.visitor)
        created = self.client.post(self.list_url, self.payload, format="json")
        patched = self.client.patch(
            self.detail_url, {"title": "Unauthorized update"}, format="json"
        )
        deleted = self.client.delete(self.detail_url)
        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patched.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)

    def test_star_requires_login_and_toggles(self):
        guest = self.client.post(self.star_url)
        self.assertEqual(guest.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.visitor)
        first = self.client.post(self.star_url)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertTrue(first.data["is_starred"])
        self.assertEqual(first.data["star_count"], 1)

        second = self.client.post(self.star_url)
        self.assertFalse(second.data["is_starred"])
        self.assertEqual(second.data["star_count"], 0)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_missing_project_and_wrong_collection_method(self):
        self.client.force_authenticate(user=self.owner)
        missing = self.client.get(reverse("projects:api_detail", args=[99999]))
        wrong_method = self.client.delete(self.list_url)

        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(wrong_method.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))

        response = client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        csrf_token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
