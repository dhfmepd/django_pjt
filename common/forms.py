from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from common.models import File

class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")

    class Meta:
        model = User
        fields = ("username", "email")

class FileForm(forms.Form):
    file_data = forms.FileField(label='Select a file', help_text='Max. 42 MB')
