from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        user = User.objects.values('id').filter(username=cleaned_data.get('username'))
        if user:
            self.add_error(field='username', error='Username already taken by someone!')
        p = cleaned_data.get('password')
        c = cleaned_data.get('confirm')
        if p != c:
            self.add_error(field='confirm', error='Password and Confirm should be same!')


