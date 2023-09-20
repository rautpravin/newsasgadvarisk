from django.contrib import admin

from app_news.models import SearchPhrase, UserSearchPhrase, Source, News

admin.site.register(SearchPhrase)
admin.site.register(UserSearchPhrase)
admin.site.register(Source)
admin.site.register(News)
