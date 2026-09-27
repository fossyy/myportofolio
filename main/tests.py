from datetime import date
from django.contrib.auth import get_user_model

from django.test import TestCase
from django.urls import reverse

from experiences.models import Experience
from projects.models import Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="PBP Teaching Assistant",
            organization="Universitas Indonesia",
            description="Help students understand web development.",
            project="PBP Support",
            technologies="Django, Python",
            category="part-time",
            started_at=date(2024, 8, 1),
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Bagas Aulia Rezki")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("experiences:list")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/a-page-that-does-not-exist/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "PBP Teaching Assistant")
        self.assertEqual(self.experience.category, "part-time")
        self.assertEqual(self.experience.period, "Aug 2024 — Present")
        self.assertEqual(self.experience.tags, ["Django", "Python"])
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("experiences:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.organization)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, self.experience.project)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Ongoing")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("experiences:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No experience has been added yet.")

    def test_completed_experience(self):
        self.experience.ended_at = date(2025, 4, 30)
        self.experience.save()
        response = self.client.get(reverse("experiences:list"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(self.experience.period, "Aug 2024 — Apr 2025")
        self.assertContains(response, "Completed")
        self.assertNotContains(response, "Ongoing")


class ProjectPageTest(TestCase):
    def test_projects_url_uses_shared_templates(self):
        response = self.client.get(reverse("projects:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")
        self.assertTemplateUsed(response, "components/navbar.html")
        self.assertTemplateUsed(response, "components/footer.html")

    def test_all_projects_appear_with_database_content(self):
        projects = [
            Project.objects.create(
                title="Research dashboard",
                description="Visualizes research results.",
                source_url="https://example.com/dashboard/source",
                live_url="https://example.com/dashboard/live",
            ),
            Project.objects.create(
                title="Campus directory",
                description="Helps students find campus facilities.",
            ),
        ]
        response = self.client.get(reverse("projects:list"))

        self.assertQuerySetEqual(response.context["project_list"], projects)
        for project in projects:
            with self.subTest(project=project.title):
                self.assertContains(response, project.title)
                self.assertContains(response, project.description)
        self.assertContains(response, f'href="{projects[0].source_url}"')
        self.assertContains(response, f'href="{projects[0].live_url}"')
        self.assertNotContains(response, "No projects have been added yet.")

    def test_empty_projects_page(self):
        self.assertFalse(Project.objects.exists())
        response = self.client.get(reverse("projects:list"))

        self.assertContains(response, "No projects have been added yet.")
        self.assertNotContains(response, 'class="project-row"')

    def test_optional_links_are_rendered_independently(self):
        project = Project.objects.create(title="Optional links", description="Test project")
        for source_url, live_url in [
            ("", ""),
            ("https://example.com/source", ""),
            ("", "https://example.com/live"),
        ]:
            with self.subTest(source_url=source_url, live_url=live_url):
                project.source_url = source_url
                project.live_url = live_url
                project.save()
                response = self.client.get(reverse("projects:list"))
                self.assertContains(response, "[ inspect_source ]", count=int(bool(source_url)))
                self.assertContains(response, "[ view_live ]", count=int(bool(live_url)))
                self.assertNotContains(response, 'href=""')

    def test_project_text_is_escaped(self):
        Project.objects.create(title="<script>alert(1)</script>", description="<b>Plain text</b>")
        response = self.client.get(reverse("projects:list"))

        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertContains(response, "&lt;b&gt;Plain text&lt;/b&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_shared_navigation_and_homepage_removal(self):
        project = Project.objects.create(title="Only on projects page", description="Database content")
        for route in ["main:show_main", "experiences:list", "projects:list"]:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertContains(response, f'href="{reverse("projects:list")}"')
                self.assertTemplateUsed(response, "components/navbar.html")
                self.assertTemplateUsed(response, "components/footer.html")
        home = self.client.get(reverse("main:show_main"))
        self.assertNotContains(home, project.title)
        self.assertNotContains(home, 'id="projects"')

    def test_project_api_filters_by_title(self):
        Project.objects.create(title="Research dashboard", description="Research")
        Project.objects.create(title="Campus directory", description="Campus")

        response = self.client.get(reverse("projects:api_list"), {"title": "research"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["fields"]["title"], "Research dashboard")
        self.assertEqual(len(response.json()), 1)

    def test_project_api_get_and_delete_by_title(self):
        project = Project.objects.create(title="Delete me", description="Temporary")
        detail_url = reverse("projects:api_detail", args=[project.title])

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["pk"], project.pk)
        self.assertNotIn("starred_by", response.json()[0]["fields"])

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(pk=project.pk).exists())

        regular_user = get_user_model().objects.create_user(username="regular", password="pass")
        self.client.force_login(regular_user)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=project.pk).exists())

        owner = get_user_model().objects.create_superuser(username="owner", password="pass")
        self.client.force_login(owner)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_project_mutations_require_owner_access(self):
        create_url = reverse("projects:create")
        delete_project = Project.objects.create(title="Protected project", description="Temporary")
        delete_url = reverse("projects:delete", args=[delete_project.pk])

        guest_response = self.client.post(create_url, {})
        self.assertEqual(guest_response.status_code, 302)
        self.assertIn(reverse("main:login"), guest_response.url)
        self.assertEqual(self.client.post(delete_url).status_code, 302)

        regular_user = get_user_model().objects.create_user(username="regular", password="pass")
        self.client.force_login(regular_user)
        self.assertEqual(self.client.post(create_url, {}).status_code, 403)
        self.assertEqual(self.client.post(delete_url).status_code, 403)

        owner = get_user_model().objects.create_superuser(username="owner", password="pass")
        self.client.force_login(owner)
        create_response = self.client.post(create_url, {
            "title": "Authorized project",
            "description": "Created by the portfolio owner",
        })
        self.assertRedirects(create_response, reverse("projects:list"))
        self.assertTrue(Project.objects.filter(title="Authorized project").exists())

        delete_response = self.client.post(delete_url)
        self.assertRedirects(delete_response, reverse("projects:list"))
        self.assertFalse(Project.objects.filter(pk=delete_project.pk).exists())

    def test_projects_page_has_delete_button(self):
        project = Project.objects.create(title="Removable project", description="Temporary")

        response = self.client.get(reverse("projects:list"))
        self.assertNotContains(response, f'action="{reverse("projects:delete", args=[project.pk])}"')
        self.assertNotContains(response, "[ delete_project ]")

        self.client.force_login(get_user_model().objects.create_superuser(username="owner", password="pass"))
        response = self.client.get(reverse("projects:list"))
        self.assertContains(response, f'action="{reverse("projects:delete", args=[project.pk])}"')
        self.assertContains(response, "[ delete_project ]")

    def test_delete_project_button_removes_project(self):
        project = Project.objects.create(title="Remove from page", description="Temporary")
        owner = get_user_model().objects.create_superuser(username="owner", password="pass")
        self.client.force_login(owner)

        response = self.client.post(
            reverse("projects:delete", args=[project.pk]),
        )

        self.assertRedirects(response, reverse("projects:list"))
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())
