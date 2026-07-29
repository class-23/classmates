"""回填slug数据"""
from django.db import migrations


def backfill_notebook_slug(apps, schema_editor):
    Notebook = apps.get_model('core', 'Notebook')
    for notebook in Notebook.objects.all():
        if not notebook.title_slug:
            notebook.title_slug = notebook.title
            counter = 1
            base_slug = notebook.title
            while Notebook.objects.filter(title_slug=notebook.title_slug).exclude(pk=notebook.pk).exists():
                counter += 1
                notebook.title_slug = f'{base_slug}-{counter}'
            notebook.save()


def backfill_student_slug(apps, schema_editor):
    Student = apps.get_model('core', 'Student')
    for student in Student.objects.all():
        if not student.name_slug:
            student.name_slug = student.name
            counter = 1
            base_slug = student.name
            while Student.objects.filter(
                notebook_id=student.notebook_id, name_slug=student.name_slug
            ).exclude(pk=student.pk).exists():
                counter += 1
                student.name_slug = f'{base_slug}-{counter}'
            student.save()


def reverse_backfill(apps, schema_editor):
    Notebook = apps.get_model('core', 'Notebook')
    Student = apps.get_model('core', 'Student')
    Notebook.objects.all().update(title_slug=None)
    Student.objects.all().update(name_slug=None)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_slug_fields'),
    ]

    operations = [
        migrations.RunPython(backfill_notebook_slug, reverse_backfill),
        migrations.RunPython(backfill_student_slug, reverse_backfill),
    ]
