from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    ACCOUNT_TYPES = [
        ('student', 'Student (I want to rent)'),
        ('landlord', 'Landlord (I have property)'),
    ]
    
    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPES, 
        widget=forms.RadioSelect(attrs={'class': 'radio-input'}),
        label="I am joining as a:",
        initial='student'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'account_type')

    def save(self, commit=True):
        user = super().save(commit=False)
        account_type = self.cleaned_data.get('account_type')
        if account_type == 'student':
            user.is_student = True
            user.is_landlord = False
        elif account_type == 'landlord':
            user.is_landlord = True
            user.is_student = False
        
        if commit:
            user.save()
        return user