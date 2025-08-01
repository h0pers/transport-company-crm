from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()

class AdminAuthenticationForm(AuthenticationForm):
    username = forms.ModelChoiceField(queryset=User.objects.all(), label=_('User'))

    def clean_username(self):
        value = self.cleaned_data['username']
        value = value.username
        return value


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        fields = ['username', 'first_name', 'last_name', 'status']
