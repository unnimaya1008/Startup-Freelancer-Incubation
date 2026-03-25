from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from .models import StartupProfile, Employee
from projects.models import Project
from mentors.models import MentorshipSession, MentorRating
from freelancer.models import FreelancerProfile, FreelancerRating
from .models import EmployeeRating


class FreelancerRatingForm(forms.ModelForm):
    class Meta:
        model = FreelancerRating
        fields = ['timeliness_rating', 'quality_rating', 'communication_rating', 'feedback']
        widgets = {
            'timeliness_rating': forms.Select(attrs={'class': 'form-select'}),
            'quality_rating': forms.Select(attrs={'class': 'form-select'}),
            'communication_rating': forms.Select(attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your feedback...'}),
        }


class EmployeeRatingForm(forms.ModelForm):
    class Meta:
        model = EmployeeRating
        fields = ['timeliness_rating', 'quality_rating', 'communication_rating', 'feedback']
        widgets = {
            'timeliness_rating': forms.Select(attrs={'class': 'form-select'}),
            'quality_rating': forms.Select(attrs={'class': 'form-select'}),
            'communication_rating': forms.Select(attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your feedback...'}),
        }

class StartupSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'STARTUP'
        if commit:
            user.save()
        return user

class StartupProfileForm(forms.ModelForm):
    logo = forms.ImageField(required=False)
    class Meta:
        model = StartupProfile
        fields = ['startup_name', 'description', 'website', 'founded_date', 'industry', 'logo']
        
        

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'domain', 'requirements_file',
            'start_date', 'end_date', 'status',
            'required_experience', 'assigned_to_freelancers', 'employees_assigned'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project details...'}),
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project domain'}),
            'requirements_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'required_experience': forms.Select(attrs={'class': 'form-select'}),
            'employees_assigned': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 6}),
        }

    def __init__(self, *args, **kwargs):
        startup = kwargs.pop('startup', None)
        super().__init__(*args, **kwargs)
        if startup:
            self.fields['employees_assigned'].queryset = Employee.objects.filter(startup=startup)
        else:
            self.fields['employees_assigned'].queryset = Employee.objects.none()


            

# forms.py
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'name', 'role', 'email', 'phone_number', 'profile_picture',
            'linkedin_profile', 'github_profile', 'skills', 'date_of_joining', 'is_active'
        ]

        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Python, Django, React'}),
            'role': forms.TextInput(attrs={'placeholder': 'e.g., Developer, Designer'}),
            'date_of_joining': forms.DateInput(
                attrs={'type': 'date'}  # ✅ This ensures the HTML5 date picker appears
            ),
        }


        
        

# -----------------------------
# MENTORSHIP FORM
# -----------------------------
class MentorshipSessionForm(forms.ModelForm):
    class Meta:
        model = MentorshipSession
        fields = ['mentor', 'topic', 'session_date', 'notes']
        widgets = {
            'session_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add objectives or notes for mentor'}),
        }

    def __init__(self, *args, **kwargs):
        # Pop custom argument to disable all fields if needed
        disable_all = kwargs.pop('disable_all', False)
        mentor_queryset = kwargs.pop('mentor_queryset', None)
        super().__init__(*args, **kwargs)
        if mentor_queryset is not None:
            self.fields['mentor'].queryset = mentor_queryset
        if disable_all:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = 'disabled'


class MentorRatingForm(forms.ModelForm):
    class Meta:
        model = MentorRating
        fields = [
            'communication_rating',
            'knowledge_delivery_rating',
            'interaction_rating',
            'understanding_quality_rating',
            'feedback'
        ]
        widgets = {
            'communication_rating': forms.Select(attrs={'class': 'form-select'}),
            'knowledge_delivery_rating': forms.Select(attrs={'class': 'form-select'}),
            'interaction_rating': forms.Select(attrs={'class': 'form-select'}),
            'understanding_quality_rating': forms.Select(attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your feedback...'}),
        }


# -----------------------------
# MILESTONE TODO LIST FORM
# -----------------------------
class MilestoneSetupForm(forms.Form):
    milestones = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'Enter one milestone per line'
        }),
        help_text="One milestone per line. Example: Design wireframes"
    )

