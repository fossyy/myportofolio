from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from main.models import Education, Experience, Project, Skill


class PortfolioRoleAccessTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Project", description="Before")
        self.experience = Experience.objects.create(
            title="Experience",
            organization="Organization",
            description="Before",
            started_at=date(2024, 1, 1),
        )
        self.skill = Skill.objects.create(name="Skill", category="Backend")
        self.education = Education.objects.create(
            qualification="Degree", institution="University", start_year=2020
        )
        self.records = [
            ("project", self.project, reverse("main:update_project", args=[self.project.pk])),
            ("experience", self.experience, reverse("main:update_experience", args=[self.experience.pk])),
            ("skill", self.skill, reverse("main:update_skill", args=[self.skill.pk])),
            ("education", self.education, reverse("main:update_education", args=[self.education.pk])),
        ]
        self.editor_group = Group.objects.create(name="Editor")

    def editor(self):
        user = get_user_model().objects.create_user(username="editor", password="password")
        user.groups.add(self.editor_group)
        return user

    def test_guests_are_redirected_from_update_and_owner_actions(self):
        create_urls = [
            reverse("main:create_project"),
            reverse("main:create_experience"),
            reverse("main:create_skill"),
            reverse("main:create_education"),
        ]
        for url in create_urls:
            with self.subTest(create_url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("main:login"), response.url)

        for _, record, update_url in self.records:
            with self.subTest(update_url=update_url):
                response = self.client.get(update_url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("main:login"), response.url)

        for url_name, record, _ in self.records:
            delete_url = reverse(f"main:delete_{url_name}", args=[record.pk])
            with self.subTest(delete_url=delete_url):
                response = self.client.post(delete_url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(record.__class__.objects.filter(pk=record.pk).exists())

    def test_regular_users_cannot_change_portfolio_data(self):
        user = get_user_model().objects.create_user(username="regular", password="password")
        self.client.force_login(user)
        for _, record, update_url in self.records:
            with self.subTest(update_url=update_url):
                self.assertEqual(self.client.get(update_url).status_code, 403)

        create_urls = [
            reverse("main:create_project"),
            reverse("main:create_experience"),
            reverse("main:create_skill"),
            reverse("main:create_education"),
        ]
        for url in create_urls:
            with self.subTest(create_url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

        for section, record, _ in self.records:
            delete_url = reverse(f"main:delete_{section}", args=[record.pk])
            with self.subTest(delete_url=delete_url):
                self.assertEqual(self.client.post(delete_url).status_code, 403)

    def test_editor_can_update_all_portfolio_sections(self):
        self.client.force_login(self.editor())
        update_payloads = [
            {"title": "Updated project", "description": "After", "source_url": "", "live_url": ""},
            {
                "title": "Updated experience",
                "organization": "New organization",
                "description": "After",
                "project": "",
                "technologies": "Django",
                "category": "full-time",
                "thumbnail": "",
                "started_at": "2024-01-01",
                "ended_at": "",
            },
            {"name": "Updated skill", "category": "Tools", "position": 1},
            {
                "qualification": "Updated degree",
                "institution": "New university",
                "start_year": 2021,
                "end_year": "",
            },
        ]

        for (section, record, update_url), payload in zip(self.records, update_payloads):
            with self.subTest(section=section):
                response = self.client.post(update_url, payload)
                show_name = {
                    "project": "show_projects",
                    "experience": "show_experience",
                    "skill": "show_skills",
                    "education": "show_education",
                }[section]
                self.assertRedirects(response, reverse(f"main:{show_name}"))
                record.refresh_from_db()
                self.assertIn("Updated", str(record))

    def test_editor_cannot_create_or_delete_portfolio_data(self):
        user = self.editor()
        self.client.force_login(user)
        create_urls = [
            reverse("main:create_project"),
            reverse("main:create_experience"),
            reverse("main:create_skill"),
            reverse("main:create_education"),
        ]
        for url in create_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

        for section, record, _ in self.records:
            delete_url = reverse(f"main:delete_{section}", args=[record.pk])
            with self.subTest(delete_url=delete_url):
                self.assertEqual(self.client.post(delete_url).status_code, 403)
                self.assertTrue(record.__class__.objects.filter(pk=record.pk).exists())

    def test_public_pages_show_edit_links_only_to_editors_and_owner(self):
        page_urls = [
            ("project", reverse("main:show_projects"), reverse("main:update_project", args=[self.project.pk])),
            ("experience", reverse("main:show_experience"), reverse("main:update_experience", args=[self.experience.pk])),
            ("skill", reverse("main:show_skills"), reverse("main:update_skill", args=[self.skill.pk])),
            ("education", reverse("main:show_education"), reverse("main:update_education", args=[self.education.pk])),
        ]
        for _, page_url, edit_url in page_urls:
            with self.subTest(page_url=page_url):
                self.assertNotContains(self.client.get(page_url), edit_url)

        self.client.force_login(self.editor())
        for _, page_url, edit_url in page_urls:
            with self.subTest(page_url=page_url):
                self.assertContains(self.client.get(page_url), edit_url)
