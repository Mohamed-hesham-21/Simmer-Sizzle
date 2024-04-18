# Generated by Django 5.0.1 on 2024-04-17 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("RecipeFinder", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="hasstep",
            name="index",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="isAdmin",
            field=models.BooleanField(default=True),
        ),
    ]
