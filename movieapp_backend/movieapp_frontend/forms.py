from django import forms
from django.forms import TextInput
from django.utils.translation import ugettext as _
from movie_app.models import Profile
from django.core.exceptions import ValidationError
import re
PASSWORD_REGEX = re.compile(r'^.{3,20}$')

def validate_password(password):
    if not PASSWORD_REGEX.match(password):
        raise ValidationError(_(
            'Password must be between 3 and 20 characters.'
            )
        )
class ChangeNameForm(forms.ModelForm):
    # new_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Insert your name'}))

    class Meta:
        model = Profile
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'placeholder': 'Insert your name',
                                     'id': 'change_name_input'}),
        }
        labels = {
            'name': '',
        }

class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(required=True, validators=[validate_password],
                                   widget=forms.PasswordInput(attrs={'placeholder': 'New Password',
                                                                     'id': 'change_password_input'
                                                                     }))
    verify_new_password = forms.CharField(required=True, validators=[validate_password],
                                          widget=forms.PasswordInput(attrs={'placeholder': 'New Password',
                                                                            'id': 'verify_password_input'}))

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        new_password = cleaned_data.get("new_password")
        verify_new_password = cleaned_data.get("verify_new_password")

        if new_password != verify_new_password:
            raise forms.ValidationError("Passwords don't match")

