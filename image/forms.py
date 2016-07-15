from django import forms
from django.contrib.auth.models import User

from .models import Album, Pic


class AlbumForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = ['album_title', 'album_cover']


class PicForm(forms.ModelForm):

    class Meta:
        model = Pic
        fields = ['pic_title', 'pic_caption','pic_file']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
