import datetime
from django.views import View
from django.db.models import Count
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin

from app_news.forms import RegistrationForm, LoginForm
from app_news.models import News, UserSearchPhrase, save_to_local_db, SearchPhrase


def logout_view(request):
    logout(request)
    return redirect('/login/')


@method_decorator(never_cache, name="dispatch")
class RegisterView(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'register.html', context={'form': RegistrationForm()})

    def post(self, request, *args, **kwargs):
        reg_form = RegistrationForm(request.POST)
        context = {'form': reg_form, 'errors': [], 'status': 'error'}

        if reg_form.is_valid():
            reg_form.cleaned_data.pop('confirm')
            pwd = reg_form.cleaned_data.pop('password')
            user = User.objects.create(**reg_form.cleaned_data)
            user.set_password(pwd)
            user.save()
            if user.id:
                context['status'] = 'ok'
        else:
            context['errors'] = reg_form.errors

        return render(request, 'register.html', context=context)


@method_decorator(never_cache, name="dispatch")
class LoginView(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'login.html', context={'form': LoginForm()})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('/')
        return render(request, 'login.html', context={'form': LoginForm(), 'error': 'Invalid username and/or password!'})


@method_decorator(never_cache, name="dispatch")
class HomeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')

    def post(self, request, *args, **kwargs):
        return render(request, 'home.html')


class SaveToLocalView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            pass
        return render(request, 'search.html')


class SearchView(View):

    def get(self, request, *args, **kwargs):

        context = {
            'error': '',
            'newly_created_count': 0,
            'data': [],
            'keyword': request.GET.get('keyword', ''),
            'from_date': request.GET.get('from_date', ''),
            'to_date': request.GET.get('to_date', ''),
            'page_size': 10,
            'sel_page_range': [10, 20, 30, 40, 50, 100]
        }
        try:
            current_page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 50))
            keyword = request.GET.get('keyword', '').lower()
            from_date = request.GET.get('from_date', '')
            to_date = request.GET.get('to_date', '')

            if not keyword:
                raise ValueError('Keyword cannot be blank!')

            # save user-search-phrase
            search_phrase, f = SearchPhrase.objects.get_or_create(keyword=keyword)

            if search_phrase:
                user_search_phrase, f = UserSearchPhrase.objects.get_or_create(user=request.user, search_phrase=search_phrase)
                user_search_phrase.search_count += 1
                user_search_phrase.save()

            # save data from api to local db
            save_to_local_db(keyword=keyword)

            # fetching data as per the conds from our local db using pagination mechanism
            cond = {'search_phrase__keyword': keyword}

            if from_date:
                cond['publishedAt__date__gte'] = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()

            if to_date:
                cond['publishedAt__date__lte'] = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()

            # get total news count
            news_count = News.objects.filter(**cond).count()

            # calculating from & to index values
            current_page = current_page - 1
            from_index = current_page * page_size
            to_index = (current_page * page_size) + page_size

            # fetching news data from our local db using slicing for pagination
            news = News.objects.filter(**cond)[from_index: to_index]

            # here calculating the total-pages count based on news_count & page_size
            if news_count and page_size > 0:
                total_pages = news_count // page_size
                total_pages = total_pages + 1 if (news_count % page_size) > 0 else total_pages
                context['total_pages_range'] = range(1, total_pages+1)
                context['total_pages'] = total_pages

            context.update({
                'data': news, 'keyword': keyword, 'page_size': page_size,
                'from_date': from_date, 'to_date': to_date,
                'total_results': news_count, 'page': current_page+1
            })
        except Exception as e:
            context['error'] = str(e)

        return render(request, 'search.html', context=context)


class SearchHistoryView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        if request.user.is_staff:
            context['data'] = UserSearchPhrase.objects.values('user__username', 'search_phrase__keyword', 'search_count').order_by('user__username', '-search_count')
        else:
            context['data'] = UserSearchPhrase.objects.values('user__username', 'search_phrase__keyword', 'search_count').filter(user=request.user).order_by('-id')

        return render(request, 'search_history.html', context=context)


class HotKeywordsView(View):

    def get(self, request, *args, **kwargs):
        d = UserSearchPhrase.objects.values('search_phrase__keyword').annotate(user_count=Count('user')).order_by('-user_count')
        context = {'data': d}
        return render(request, 'hot_keywords.html', context=context)




