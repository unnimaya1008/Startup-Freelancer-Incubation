from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from .models import MentorProfile

class MentorSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'MENTOR'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user

class MentorProfileForm(forms.ModelForm):
    class Meta:
        model = MentorProfile
        fields = ('profile_image','expertise_area', 'experience_years', 'linkedin_profile')
        widgets = {
            'expertise_area': forms.TextInput(attrs={'placeholder': 'e.g. SaaS, Fintech, Growth'}),
            'experience_years': forms.NumberInput(attrs={'min': 0}),
            'linkedin_profile': forms.URLInput(),
        }
