# Generated by Django 3.2.5 on 2021-08-04 12:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("actions", "0006_alter_version_action"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="action",
            name="name",
        ),
    ]
