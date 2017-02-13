from django import forms
from django.forms import TextInput, FileInput
from django.utils.translation import ugettext as _
from movie_app.models import Profile
from django.core.exceptions import ValidationError

import re

PASSWORD_REGEX = re.compile(r'^.{3,20}$')
ALLOWED_EXTENSIONS = ['image/jpeg', 'image/gif', 'image/png']


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
                                     'id': 'change_name_input',
                                     'class': 'form-control'}),
        }
        labels = {
            'name': '',
        }


class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(required=True, validators=[validate_password],
                                   widget=forms.PasswordInput(attrs={'placeholder': 'New Password',
                                                                     'id': 'change_password_input',
                                                                     'class': 'form-control'
                                                                     }))
    verify_new_password = forms.CharField(required=True, validators=[validate_password],
                                          widget=forms.PasswordInput(attrs={'placeholder': 'Verfy New Password',
                                                                            'id': 'verify_password_input',
                                                                            'class': 'form-control'
                                                                            }))

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        new_password = cleaned_data.get("new_password")
        verify_new_password = cleaned_data.get("verify_new_password")

        if new_password != verify_new_password:
            raise forms.ValidationError("Passwords don't match")


class ChangeAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        labels = {
            'avatar': _('Choose an image:'),
        }
        widgets = {
            'avatar': FileInput(attrs={'id': 'select_avatar_button'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar', False)
        if avatar:
            if avatar._size > 4 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 4mb )")
            from django.core.files.images import get_image_dimensions
            w, h = get_image_dimensions(avatar)
            if w > 500 or h > 500:
                raise ValidationError("Image file too big (max 500px)")
            if avatar.content_type not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(u'Only *.gif, *.jpg and *.png images are allowed.')
            return avatar
        else:
            raise ValidationError("Couldn't read uploaded image")

    def __init__(self, *args, **kwargs):
        super(ChangeAvatarForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True
