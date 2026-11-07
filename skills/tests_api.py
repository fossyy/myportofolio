from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from skills.models import Skill


class SkillApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_superuser(
            username="owner", email="owner@example.com", password="test-password"
        )
        self.visitor = user_model.objects.create_user(
            username="visitor", email="visitor@example.com", password="test-password"
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.skill = Skill.objects.create(name="Django", category="Backend", position=1)
        self.list_url = reverse("api:skill_list")
        self.detail_url = reverse("api:skill_detail", args=[self.skill.pk])
        self.star_url = reverse("api:skill_star", args=[self.skill.pk])
        self.payload = {"name": "Python", "category": "Backend", "position": 2}
        self.client = self.client_class()

    def test_public_list_detail_and_name_search(self):
        self.skill.starred_by.add(self.visitor)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.skill.pk)
        self.assertEqual(response.data[0]["star_count"], 1)
        self.assertEqual(response.data[0]["starred_by_names"], "visitor")
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("email", response.data[0])
        self.assertNotIn("starred_by", response.data[0])

        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["name"], self.skill.name)

        matching = self.client.get(self.list_url, {"name": "djang"})
        missing = self.client.get(self.list_url, {"name": "react"})
        self.assertEqual(len(matching.data), 1)
        self.assertEqual(missing.data, [])

    def test_owner_can_create_and_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "star_count": 99, "is_starred": True, "starred_by_names": "forged"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertTrue(Skill.objects.filter(name="Python").exists())

    def test_serializer_strips_markup_and_rejects_invalid_data(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "name": " <b>Clean skill</b> ", "category": "<i>Tools</i>"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Clean skill")
        self.assertEqual(response.data["category"], "Tools")

        invalid_name = self.client.post(
            self.list_url, {**self.payload, "name": "<b></b>"}, format="json"
        )
        invalid_position = self.client.post(
            self.list_url, {**self.payload, "position": -1}, format="json"
        )
        self.assertEqual(invalid_name.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", invalid_name.data)
        self.assertEqual(invalid_position.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("position", invalid_position.data)
        self.assertEqual(Skill.objects.count(), 2)

    def test_owner_can_put_patch_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        patched = self.client.patch(self.detail_url, {"name": "Patched skill"}, format="json")
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(patched.data["name"], "Patched skill")

        replaced = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(replaced.status_code, status.HTTP_200_OK)
        self.assertEqual(replaced.data["category"], self.payload["category"])

        deleted = self.client.delete(self.detail_url)
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deleted.content, b"")
        self.assertFalse(Skill.objects.filter(pk=self.skill.pk).exists())

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.visitor.groups.add(self.editor_group)
        self.client.force_authenticate(user=self.visitor)

        patched = self.client.patch(self.detail_url, {"name": "Editor update"}, format="json")
        created = self.client.post(self.list_url, self.payload, format="json")
        deleted = self.client.delete(self.detail_url)

        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Skill.objects.filter(pk=self.skill.pk).exists())
        self.assertFalse(Skill.objects.filter(name=self.payload["name"]).exists())
        self.assertEqual(Skill.objects.get(pk=self.skill.pk).name, "Editor update")

    def test_editor_can_replace_skill_with_put(self):
        self.visitor.groups.add(self.editor_group)
        self.client.force_authenticate(user=self.visitor)

        response = self.client.put(self.detail_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.payload["name"])
        self.assertEqual(response.data["category"], self.payload["category"])

    def test_guest_and_regular_user_cannot_write(self):
        guest_create = self.client.post(self.list_url, self.payload, format="json")
        guest_patch = self.client.patch(self.detail_url, {"name": "Guest update"}, format="json")
        guest_delete = self.client.delete(self.detail_url)
        self.assertEqual(guest_create.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(guest_patch.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(guest_delete.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.visitor)
        created = self.client.post(self.list_url, self.payload, format="json")
        patched = self.client.patch(self.detail_url, {"name": "Unauthorized update"}, format="json")
        deleted = self.client.delete(self.detail_url)
        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patched.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Skill.objects.count(), 1)
        self.assertEqual(Skill.objects.get(pk=self.skill.pk).name, "Django")

    def test_star_requires_login_and_toggles(self):
        guest = self.client.post(self.star_url)
        self.assertEqual(guest.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.skill.starred_by.exists())

        self.client.force_authenticate(user=self.visitor)
        first = self.client.post(self.star_url)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertTrue(first.data["is_starred"])
        self.assertEqual(first.data["star_count"], 1)
        self.assertTrue(self.skill.starred_by.filter(pk=self.visitor.pk).exists())

        second = self.client.post(self.star_url)
        self.assertFalse(second.data["is_starred"])
        self.assertEqual(second.data["star_count"], 0)
        self.assertFalse(self.skill.starred_by.filter(pk=self.visitor.pk).exists())
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_missing_skill_and_wrong_collection_method(self):
        self.client.force_authenticate(user=self.owner)
        missing = self.client.get(reverse("api:skill_detail", args=[99999]))
        wrong_method = self.client.delete(self.list_url)

        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(wrong_method.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_malformed_json_returns_bad_request(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.generic(
            "POST", self.list_url, b'{"name":', content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Skill.objects.count(), 1)

    def test_session_write_without_csrf_is_rejected(self):
        client = self.client_class(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))

        response = client.post(
            self.list_url, {"name": "No CSRF", "category": "Tools", "position": 0},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Skill.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = self.client_class(enforce_csrf_checks=True)
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
