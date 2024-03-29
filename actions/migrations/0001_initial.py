# Generated by Django 3.2.5 on 2021-07-13 08:20

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Action",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.CharField(max_length=200)),
                ("type", models.CharField(max_length=50)),
                ("pub_date", models.DateTimeField(verbose_name="date published")),
            ],
        ),
    ]
