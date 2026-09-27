from django.db import migrations


CONTENT_TYPES = {
    "education": "education",
    "experience": "experiences",
    "project": "projects",
    "skill": "skills",
}


def move_content_types(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    database = schema_editor.connection.alias
    for model_name, app_label in CONTENT_TYPES.items():
        ContentType.objects.using(database).filter(
            app_label="main", model=model_name
        ).update(app_label=app_label)


def restore_content_types(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    database = schema_editor.connection.alias
    for model_name, app_label in CONTENT_TYPES.items():
        ContentType.objects.using(database).filter(
            app_label=app_label, model=model_name
        ).update(app_label="main")


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("main", "0006_project_starred_by"),
        ("projects", "0001_initial"),
        ("experiences", "0001_initial"),
        ("skills", "0001_initial"),
        ("education", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="Education"),
                migrations.DeleteModel(name="Experience"),
                migrations.RemoveField(model_name="project", name="starred_by"),
                migrations.DeleteModel(name="Skill"),
                migrations.DeleteModel(name="Project"),
            ],
        ),
        migrations.RunPython(move_content_types, restore_content_types),
    ]
