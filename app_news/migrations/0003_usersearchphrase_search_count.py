# Generated by Django 4.2.5 on 2023-09-20 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_news', '0002_alter_news_author_alter_news_content_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersearchphrase',
            name='search_count',
            field=models.PositiveIntegerField(default=1, verbose_name='search count'),
        ),
    ]
