# Generated by Django 3.2.5 on 2021-07-22 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("actions", "0004_auto_20210720_1540"),
    ]

    operations = [
        migrations.AlterField(
            model_name="version",
            name="date",
            field=models.DateTimeField(),
        ),
    ]
