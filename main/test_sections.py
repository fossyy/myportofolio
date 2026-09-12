from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from main.models import Skill


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
