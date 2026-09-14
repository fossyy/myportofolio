from datetime import date

from django.test import TestCase
from django.urls import reverse

from main.models import Experience, Project


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
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

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
        response = self.client.get(reverse("main:show_experience"))

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
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No experience has been added yet.")

    def test_completed_experience(self):
        self.experience.ended_at = date(2025, 4, 30)
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(self.experience.period, "Aug 2024 — Apr 2025")
        self.assertContains(response, "Completed")
        self.assertNotContains(response, "Ongoing")


class ProjectPageTest(TestCase):
    def test_projects_url_uses_shared_templates(self):
        response = self.client.get(reverse("main:show_projects"))

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
        response = self.client.get(reverse("main:show_projects"))

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
        response = self.client.get(reverse("main:show_projects"))

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
                response = self.client.get(reverse("main:show_projects"))
                self.assertContains(response, "[ inspect_source ]", count=int(bool(source_url)))
                self.assertContains(response, "[ view_live ]", count=int(bool(live_url)))
                self.assertNotContains(response, 'href=""')

    def test_project_text_is_escaped(self):
        Project.objects.create(title="<script>alert(1)</script>", description="<b>Plain text</b>")
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertContains(response, "&lt;b&gt;Plain text&lt;/b&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_shared_navigation_and_homepage_removal(self):
        project = Project.objects.create(title="Only on projects page", description="Database content")
        for route in ["main:show_main", "main:show_experience", "main:show_projects"]:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertContains(response, f'href="{reverse("main:show_projects")}"')
                self.assertTemplateUsed(response, "components/navbar.html")
                self.assertTemplateUsed(response, "components/footer.html")
        home = self.client.get(reverse("main:show_main"))
        self.assertNotContains(home, project.title)
        self.assertNotContains(home, 'id="projects"')
