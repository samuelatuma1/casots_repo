from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _

User=get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
                user = authenticate(username=username, password=password)
                if not user:
                    raise forms.ValidationError("This user does not exists")
                if not user.check_password(password):
                    raise forms.ValidationError("Incorrect password")
                if not user.is_active:
                    raise forms.ValidationError("This user is not active")
        return super(UserLoginForm, self).clean(*args, **kwargs)


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name= forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model=User
        fields =('username',
                 'email',
                 'first_name',
                 'last_name',
                 'password1',
                 'password2')
        

    def save(self,commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user_last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
        return user
    
class ContactForm(forms.Form):
    first_name= forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email_address = forms.EmailField(max_length=150)
    message = forms.CharField(widget=forms.Textarea)