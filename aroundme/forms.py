import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class SignupForm(forms.Form):
    username = forms.CharField(label='username', max_length=30)
    email_id = forms.EmailField(label='email')
    password_input = forms.CharField(label='input-password', widget=forms.PasswordInput())
    password_confirm = forms.CharField(label='confirm-password', widget=forms.PasswordInput())


    def clean_password_confirm(self):
        if 'password_input' in self.cleaned_data:
            password_input = self.cleaned_data['password_input']
            password_confirm = self.cleaned_data['password_confirm']
            if password_input == password_confirm:
                return password_confirm
        raise forms.ValidationError('Validation error : password not matching')

    # This email will be the identifier of the member
    def clean_email_id(self):
        email_id = self.cleaned_data['email_id']

        try :
            if User.objects.get(email=email_id):
                raise forms.ValidationError('This email is already in use')
        except ObjectDoesNotExist:
            return email_id

    def clean_username(self):
        username = self.cleaned_data['username']

        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('username should include alphabet, number and underline only')

        return username


class AddEventForm(forms.Form):
    description = forms.CharField(label='description')
    place = forms.CharField(max_length=100, required=False)
    datetime_start = forms.DateTimeField()
    datetime_finish = forms.DateTimeField()