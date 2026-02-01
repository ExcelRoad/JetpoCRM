from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# Login Form using user model

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'input-field'})
        self.fields['password'].widget.attrs.update({'class': 'input-field'})

# Register Form using user model
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'input-field'})
        self.fields['last_name'].widget.attrs.update({'class': 'input-field'})
        self.fields['email'].widget.attrs.update({'class': 'input-field'})
        self.fields['password1'].widget.attrs.update({'class': 'input-field'})
        self.fields['password2'].widget.attrs.update({'class': 'input-field'})
