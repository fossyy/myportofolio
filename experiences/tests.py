import re

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from experiences.forms import ExperienceForm
from experiences.models import Experience


class ExperienceAjaxTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", email="owner@example.com", password="pass1234"
        )
        self.regular = User.objects.create_user(username="regular", password="pass1234")
        self.editor = User.objects.create_user(username="editor", password="pass1234")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.experience = Experience.objects.create(
            title="Backend Developer", organization="Example Co", description="Built APIs"
        )

    def test_list_page_is_a_skeleton_and_json_is_public_with_star_data(self):
        self.experience.starred_by.add(self.regular)

        page = self.client.get(reverse("experiences:list"))
        payload = self.client.get(reverse("experiences:api_list")).json()

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "experience-loading")
        self.assertNotContains(page, "Backend Developer")
        self.assertEqual(payload[0]["fields"]["star_count"], 1)
        self.assertFalse(payload[0]["fields"]["is_starred"])

        self.client.force_login(self.regular)
        user_payload = self.client.get(reverse("experiences:api_list")).json()
        self.assertTrue(user_payload[0]["fields"]["is_starred"])
        for user in (self.editor, self.owner):
            self.client.force_login(user)
            role_response = self.client.get(reverse("experiences:api_list"))
            self.assertEqual(role_response.status_code, 200)
            self.assertEqual(len(role_response.json()), 1)

    def test_title_search_and_empty_results(self):
        matching = self.client.get(reverse("experiences:api_list"), {"title": "backend"})
        missing = self.client.get(reverse("experiences:api_list"), {"title": "designer"})

        self.assertEqual([item["pk"] for item in matching.json()], [str(self.experience.pk)])
        self.assertEqual(missing.json(), [])

    def test_only_owner_can_create_through_json_endpoint(self):
        url = reverse("experiences:create_ajax")
        valid_data = {
            "title": "<b>New role</b>",
            "organization": "Studio",
            "description": "<script>alert(1)</script>Built something",
            "started_at": "2026-01-01",
            "category": "full-time",
        }

        self.assertEqual(self.client.post(url, valid_data).status_code, 403)
        for user in (self.regular, self.editor):
            self.client.force_login(user)
            self.assertEqual(self.client.post(url, valid_data).status_code, 403)

        self.client.force_login(self.owner)
        response = self.client.post(url, valid_data)

        self.assertEqual(response.status_code, 201)
        created = Experience.objects.get(pk=response.json()["pk"])
        self.assertEqual(created.title, "New role")
        self.assertEqual(created.description, "alert(1)Built something")

    def test_invalid_create_returns_json_field_errors(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("experiences:create_ajax"), {
            "title": "",
            "organization": "Studio",
            "description": "Description",
            "started_at": "not-a-date",
            "category": "full-time",
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

    def test_any_authenticated_role_can_toggle_star(self):
        response = self.client.post(reverse(
            "experiences:toggle_star", args=[self.experience.pk]
        ))
        self.assertEqual(response.status_code, 403)

        url = reverse("experiences:toggle_star", args=[self.experience.pk])
        for user in (self.regular, self.editor, self.owner):
            self.client.force_login(user)
            self.assertTrue(self.client.post(url).json()["starred"])
            self.assertFalse(self.client.post(url).json()["starred"])

    def test_ajax_create_accepts_the_rendered_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        page = csrf_client.get(reverse("experiences:list"))
        csrf_token = re.search(r'data-csrf-token="([^"]+)"', page.content.decode()).group(1)

        response = csrf_client.post(
            reverse("experiences:create_ajax"),
            {
                "title": "Secure request",
                "organization": "Studio",
                "description": "Valid post",
                "started_at": "2026-01-01",
                "category": "full-time",
            },
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 201)


class ExperienceFormSanitizationTests(TestCase):
    def test_text_fields_strip_html_tags(self):
        form = ExperienceForm(data={
            "title": "<b>Engineer</b>",
            "organization": "<i>Example</i>",
            "description": "<script>alert(1)</script>Built APIs",
            "project": "<em>Portal</em>",
            "technologies": "<strong>Django</strong>, Python",
            "category": "full-time",
            "started_at": "2026-01-01",
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["title"], "Engineer")
        self.assertEqual(form.cleaned_data["description"], "alert(1)Built APIs")
