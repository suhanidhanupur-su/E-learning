from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class ProfileUpdateForm(forms.Form):
    full_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    profile_photo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not full_name:
            raise ValidationError('Full name is required.')
        return full_name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError('Email is required.')
        if self.user and get_user_model().objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise ValidationError('Email is already in use.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '').strip()
        if not phone_number.isdigit():
            raise ValidationError('Phone number must contain only digits.')
        return phone_number

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if not photo:
            return photo
        if photo.content_type not in {'image/jpeg', 'image/png', 'image/webp', 'image/jpg'}:
            raise ValidationError('Please upload a valid image file (JPG, JPEG, PNG, WEBP).')
        return photo


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '').strip()
        if not phone_number.isdigit():
            raise ValidationError('Phone number must contain only digits.')
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        names = self.cleaned_data['full_name'].strip().split(maxsplit=1)
        user.first_name = names[0] if names else ''
        user.last_name = names[1] if len(names) > 1 else ''
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = self.cleaned_data['full_name'].strip()
            profile.phone_number = self.cleaned_data['phone_number']
            profile.save()
        return user