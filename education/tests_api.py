from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import Education


class EducationApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_superuser(
            username="owner", email="owner@example.com", password="test-password"
        )
        self.visitor = user_model.objects.create_user(
            username="visitor", email="visitor@example.com", password="test-password"
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.education = Education.objects.create(
            qualification="Bachelor of Information Systems",
            institution="Universitas Indonesia",
            start_year=2024,
        )
        self.list_url = reverse("api:education_list")
        self.detail_url = reverse("api:education_detail", args=[self.education.pk])
        self.star_url = reverse("api:education_star", args=[self.education.pk])
        self.payload = {
            "qualification": "Master degree",
            "institution": "Other campus",
            "start_year": 2028,
            "end_year": 2030,
        }
        self.client = self.client_class()

    def test_public_list_detail_and_qualification_search(self):
        self.education.starred_by.add(self.visitor)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.education.pk)
        self.assertEqual(response.data[0]["period"], "2024 — Present")
        self.assertEqual(response.data[0]["star_count"], 1)
        self.assertEqual(response.data[0]["starred_by_names"], "visitor")
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("email", response.data[0])
        self.assertNotIn("starred_by", response.data[0])

        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["qualification"], self.education.qualification)

        matching = self.client.get(self.list_url, {"qualification": "bachelor"})
        missing = self.client.get(self.list_url, {"qualification": "doctoral"})
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
                "period": "forged",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertNotEqual(response.data["period"], "forged")
        self.assertTrue(Education.objects.filter(qualification="Master degree").exists())

    def test_serializer_strips_markup_and_rejects_invalid_data(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                "qualification": " <b>Clean degree</b> ",
                "institution": "<i>Clean campus</i>",
                "start_year": 2026,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["qualification"], "Clean degree")
        self.assertEqual(response.data["institution"], "Clean campus")

        invalid_qualification = self.client.post(
            self.list_url,
            {**self.payload, "qualification": "<b></b>"},
            format="json",
        )
        reversed_years = self.client.post(
            self.list_url,
            {**self.payload, "start_year": 2030, "end_year": 2028},
            format="json",
        )
        invalid_year = self.client.post(
            self.list_url,
            {**self.payload, "start_year": 99999},
            format="json",
        )
        self.assertEqual(invalid_qualification.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("qualification", invalid_qualification.data)
        self.assertEqual(reversed_years.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_year", reversed_years.data)
        self.assertEqual(invalid_year.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_year", invalid_year.data)
        self.assertEqual(Education.objects.count(), 2)

    def test_validator_checks_reversed_years_on_partial_update(self):
        self.education.end_year = 2026
        self.education.save()
        self.client.force_authenticate(user=self.owner)

        rejected = self.client.patch(self.detail_url, {"start_year": 2030}, format="json")
        self.assertEqual(rejected.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_year", rejected.data)
        self.education.refresh_from_db()
        self.assertEqual(self.education.start_year, 2024)

        accepted = self.client.patch(self.detail_url, {"start_year": 2025}, format="json")
        self.assertEqual(accepted.status_code, status.HTTP_200_OK)

    def test_owner_can_put_patch_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        patched = self.client.patch(
            self.detail_url, {"qualification": "Patched degree"}, format="json"
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(patched.data["qualification"], "Patched degree")

        replaced = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(replaced.status_code, status.HTTP_200_OK)
        self.assertEqual(replaced.data["institution"], self.payload["institution"])

        deleted = self.client.delete(self.detail_url)
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deleted.content, b"")
        self.assertFalse(Education.objects.filter(pk=self.education.pk).exists())

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.visitor.groups.add(self.editor_group)
        self.client.force_authenticate(user=self.visitor)

        patched = self.client.patch(
            self.detail_url, {"qualification": "Editor update"}, format="json"
        )
        created = self.client.post(self.list_url, self.payload, format="json")
        deleted = self.client.delete(self.detail_url)

        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Education.objects.filter(pk=self.education.pk).exists())
        self.assertFalse(
            Education.objects.filter(qualification=self.payload["qualification"]).exists()
        )
        self.assertEqual(
            Education.objects.get(pk=self.education.pk).qualification, "Editor update"
        )

    def test_editor_can_replace_education_with_put(self):
        self.visitor.groups.add(self.editor_group)
        self.client.force_authenticate(user=self.visitor)

        response = self.client.put(self.detail_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["qualification"], self.payload["qualification"])
        self.assertEqual(response.data["institution"], self.payload["institution"])

    def test_guest_and_regular_user_cannot_write(self):
        guest_create = self.client.post(self.list_url, self.payload, format="json")
        guest_patch = self.client.patch(
            self.detail_url, {"qualification": "Guest update"}, format="json"
        )
        guest_delete = self.client.delete(self.detail_url)
        self.assertEqual(guest_create.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(guest_patch.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(guest_delete.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.visitor)
        created = self.client.post(self.list_url, self.payload, format="json")
        patched = self.client.patch(
            self.detail_url, {"qualification": "Unauthorized update"}, format="json"
        )
        deleted = self.client.delete(self.detail_url)
        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patched.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Education.objects.count(), 1)
        self.assertEqual(
            Education.objects.get(pk=self.education.pk).qualification,
            "Bachelor of Information Systems",
        )

    def test_star_requires_login_and_toggles(self):
        guest = self.client.post(self.star_url)
        self.assertEqual(guest.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.education.starred_by.exists())

        self.client.force_authenticate(user=self.visitor)
        first = self.client.post(self.star_url)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertTrue(first.data["is_starred"])
        self.assertEqual(first.data["star_count"], 1)
        self.assertTrue(
            self.education.starred_by.filter(pk=self.visitor.pk).exists()
        )

        second = self.client.post(self.star_url)
        self.assertFalse(second.data["is_starred"])
        self.assertEqual(second.data["star_count"], 0)
        self.assertFalse(
            self.education.starred_by.filter(pk=self.visitor.pk).exists()
        )
        self.assertEqual(
            self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_missing_education_and_wrong_collection_method(self):
        self.client.force_authenticate(user=self.owner)
        missing = self.client.get(reverse("api:education_detail", args=[99999]))
        wrong_method = self.client.delete(self.list_url)

        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(wrong_method.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_malformed_json_returns_bad_request(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.generic(
            "POST", self.list_url, b'{"qualification":', content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Education.objects.count(), 1)

    def test_session_write_without_csrf_is_rejected(self):
        client = self.client_class(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))

        response = client.post(
            self.list_url,
            {"qualification": "No CSRF", "institution": "Campus", "start_year": 2026},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), 1)

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
