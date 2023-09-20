# Generated by Django 4.2.5 on 2023-09-19 18:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchPhrase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=500, verbose_name='phrase')),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_id', models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='source id')),
                ('source_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='source name')),
            ],
        ),
        migrations.CreateModel(
            name='UserSearchPhrase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_phrase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_search_phrases', to='app_news.searchphrase')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_search_phrases', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=200, verbose_name='author')),
                ('title', models.CharField(max_length=1000, verbose_name='title')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('news_url', models.URLField(default=None, null=True, verbose_name='news url')),
                ('image_url', models.URLField(default=None, null=True, verbose_name='image url')),
                ('publishedAt', models.DateTimeField(verbose_name='published at')),
                ('content', models.TextField(verbose_name='content')),
                ('search_phrase', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='news', to='app_news.searchphrase')),
                ('source', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='news', to='app_news.source')),
            ],
        ),
    ]
