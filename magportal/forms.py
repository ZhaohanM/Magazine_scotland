from django import forms
from django.contrib.auth.models import User
from django.http import request
from django.template.defaultfilters import default_if_none
from magportal.models import UserProfile, Magazine, Category
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import widgets

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username','password',)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ()     
    
class EditUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['password'].required = False

    class Meta:
        model = User
        fields = ('username', 'password',)
        labels = {
            'username': 'New username',
            'password': 'New password',
        }
        help_texts = {
            'username': '',
        }
        widgets = {
            'password': forms.PasswordInput(),
            'password': forms.TextInput(attrs={'placeholder': 'Leave blank to remain unchanged','size' : 40}),
            'username': forms.TextInput(attrs={'placeholder': 'Leave blank to remain unchanged','size' : 40}),
        }
        
class MagazineForm(forms.ModelForm):
    Description = forms.CharField(widget=forms.Textarea)
    URL = forms.URLField()
    Discount = forms.CharField(widget=forms.Textarea)
    Categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all())
    
    class Meta:
        model = Magazine
        fields = {'Name', 'Description', 'URL', 'Image', 'Categories', 'Discount'}

        

        
