from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from .models import FreelancerProfile ,Milestone
from projects.models import Project , ProjectProposal

class FreelancerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if hasattr(user, 'role'):
            user.role = 'FREELANCER'
        if commit:
            user.save()
        return user




class FreelancerProfileForm(forms.ModelForm):
    class Meta:
        model = FreelancerProfile
        fields = [
            'domain',
            'experience_years',
            'contact_number',
            'bio',
            'hourly_rate',
            'availability',
            'profile_picture',
            'resume',
        ]
        widgets = {
            'domain': forms.TextInput(attrs={'placeholder': 'e.g., Web Development'}),
            'experience_years': forms.Select(),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a short bio...'}),
            'availability': forms.Select(),
        }





# class SkillForm(forms.ModelForm):
#     class Meta:
#         model = Skill
#         fields = ['name', 'proficiency', 'image']  # ✅ Added image field
#         widgets = {
#             'proficiency': forms.Select(choices=[
#                 ('BEGINNER', 'Beginner'),
#                 ('INTERMEDIATE', 'Intermediate'),
#                 ('EXPERT', 'Expert')
#             ])
#         }

#     # Optional: Add a custom label or help text
#     image = forms.ImageField(required=False, label="Skill Icon", help_text="Upload an optional image for this skill")



# class CertificationForm(forms.ModelForm):
#     class Meta:
#         model = Certification
#         fields = ['title', 'issuer', 'issue_date', 'certificate_url', 'certificate_file', 'certificate_image']
#         widgets = {
#             'issue_date': forms.DateInput(attrs={'type': 'date'}),
#         }





# class PortfolioForm(forms.ModelForm):
#     class Meta:
#         model = PortfolioItem
#         fields = ['title', 'description', 'file', 'preview_image', 'live_link']
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
#             'preview_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
#             'live_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter live project URL'}),
#         }






class ProposalForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=forms.ClearableFileInput(),
        required=False,
        help_text="Upload supporting documents (optional)"
    )

    class Meta:
        model = ProjectProposal
        fields = [ 'proposal_text', 'expected_payment', 'expected_timeline', 'attachments']
        widgets = {
            'proposal_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your proposal...'}),
            'expected_timeline': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Estimated days to complete'}),
        }

    def __init__(self, *args, **kwargs):
        freelancer = kwargs.pop('freelancer', None)
        super().__init__(*args, **kwargs)
        if freelancer:
            self.fields['project'].queryset = Project.objects.filter(status='OPEN').exclude(
                proposals__freelancer=freelancer
            )



class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'due_date', 'progress', 'status', 'remarks']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }
