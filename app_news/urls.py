from django.urls import path
from app_news import views


urlpatterns = [
    path('', views.HomeView.as_view()),
    path('logout/', views.logout_view),
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('search/', views.SearchView.as_view()),
    path('search-history/', views.SearchHistoryView.as_view()),
    path('hot-keywords/', views.HotKeywordsView.as_view()),
]

