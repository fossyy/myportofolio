from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from main.models import Education, Skill


class SkillPageTest(TestCase):
    def test_empty_page_and_template(self):
        response = self.client.get(reverse("main:show_skills"))
        self.assertContains(response, "No skills have been added yet.")
        self.assertTemplateUsed(response, "skills.html")
        self.assertTemplateUsed(response, "components/navbar.html")
        self.assertTemplateUsed(response, "components/footer.html")

    def test_grouped_database_content(self):
        Skill.objects.create(name="Second skill", category="Backend", position=2)
        Skill.objects.create(name="First skill", category="Backend", position=1)
        Skill.objects.create(name="Browser skill", category="Frontend")
        response = self.client.get(reverse("main:show_skills"))
        for text in ["First skill", "Second skill", "Browser skill", "Backend", "Frontend"]:
            self.assertContains(response, text, count=1)
        html = response.content.decode()
        self.assertLess(html.index("First skill"), html.index("Second skill"))
        self.assertNotContains(response, "No skills have been added yet.")
        home = self.client.get(reverse("main:show_main"))
        self.assertNotContains(home, 'id="skills"')
        self.assertContains(home, f'href="{reverse("main:show_skills")}"')

    def test_admin_can_add_change_and_delete_skill(self):
        self.client.force_login(get_user_model().objects.create_superuser(username="skill-admin", password=None))
        fields = {"name": "Admin skill", "category": "Tools", "position": 0, "_save": "Save"}
        self.assertEqual(self.client.post(reverse("admin:main_skill_add"), fields).status_code, 302)
        skill = Skill.objects.get()
        self.assertContains(self.client.get(reverse("admin:main_skill_changelist")), "Admin skill")
        fields["name"] = "Updated skill"
        self.assertEqual(self.client.post(reverse("admin:main_skill_change", args=[skill.pk]), fields).status_code, 302)
        skill.refresh_from_db()
        self.assertEqual(str(skill), "Updated skill")
        self.assertEqual(self.client.post(reverse("admin:main_skill_delete", args=[skill.pk]), {"post": "yes"}).status_code, 302)
        self.assertFalse(Skill.objects.exists())


class EducationPageTest(TestCase):
    def test_empty_page_and_template(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, "No education has been added yet.")
        self.assertTemplateUsed(response, "education.html")
        self.assertTemplateUsed(response, "components/navbar.html")
        self.assertTemplateUsed(response, "components/footer.html")

    def test_records_and_periods(self):
        Education.objects.create(qualification="Current degree", institution="Test university", start_year=2025)
        Education.objects.create(qualification="Previous diploma", institution="Test school", start_year=2021, end_year=2024)
        response = self.client.get(reverse("main:show_education"))
        for text in ["Current degree", "Test university", "2025 — Present", "Previous diploma", "Test school", "2021 — 2024"]:
            self.assertContains(response, text)
        html = response.content.decode()
        self.assertLess(html.index("Current degree"), html.index("Previous diploma"))
        self.assertNotContains(response, "No education has been added yet.")
        home = self.client.get(reverse("main:show_main"))
        self.assertNotContains(home, 'id="education"')
        self.assertContains(home, f'href="{reverse("main:show_education")}"')

    def test_reversed_years_are_invalid(self):
        with self.assertRaises(ValidationError):
            Education(qualification="Degree", institution="School", start_year=2025, end_year=2024).full_clean()

    def test_admin_can_add_change_and_delete_education(self):
        self.client.force_login(get_user_model().objects.create_superuser(username="education-admin", password=None))
        fields = {"qualification": "Admin degree", "institution": "School", "start_year": 2025, "end_year": "", "_save": "Save"}
        self.assertEqual(self.client.post(reverse("admin:main_education_add"), fields).status_code, 302)
        education = Education.objects.get()
        self.assertContains(self.client.get(reverse("admin:main_education_changelist")), "Admin degree")
        fields["qualification"] = "Updated degree"
        self.assertEqual(self.client.post(reverse("admin:main_education_change", args=[education.pk]), fields).status_code, 302)
        education.refresh_from_db()
        self.assertEqual(str(education), "Updated degree")
        self.assertEqual(self.client.post(reverse("admin:main_education_delete", args=[education.pk]), {"post": "yes"}).status_code, 302)
        self.assertFalse(Education.objects.exists())


class SectionNavigationTest(TestCase):
    def test_bio_buttons_and_section_numbering(self):
        response = self.client.get(reverse("main:show_main"))
        html = response.content.decode()
        actions = html.split('aria-label="Portfolio sections">', 1)[1].split("</nav>", 1)[0]
        self.assertLess(html.index('class="portfolio-hero__copy"'), html.index('aria-label="Portfolio sections"'))
        self.assertEqual(actions.count('class="terminal-action"'), 5)
        for number, section in enumerate(["skills", "experience", "projects", "education", "contact"], 1):
            with self.subTest(section=section):
                href = "#contact" if section == "contact" else reverse(f"main:show_{section}")
                self.assertIn(f'href="{href}"', actions)
                self.assertIn(f'prompt">{number:02d}</span>', actions)
                page = response if section == "contact" else self.client.get(href)
                self.assertContains(page, f'class="section-number">{number:02d}</span>')
        self.assertContains(response, 'id="contact"')
        self.assertNotContains(response, 'id="skills"')
        self.assertNotContains(response, 'id="education"')
        self.assertNotContains(response, "scroll to inspect")
        self.assertNotContains(response, 'href="#projects"')
