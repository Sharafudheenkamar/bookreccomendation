# Generated by Django 5.1.6 on 2025-02-15 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_review_genre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='genre',
        ),
        migrations.AddField(
            model_name='bookrecommendation',
            name='genre',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
