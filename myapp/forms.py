# forms.py
from django import forms
from .models import BookRecommendation, Login

class BookRecommendationForm(forms.ModelForm):
    class Meta:
        model = BookRecommendation
        fields = ['genre','book_title', 'author', 'description']

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Hide password input
    confirm_password = forms.CharField(widget=forms.PasswordInput)  # Confirm password field

    class Meta:
        model = Login
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Check if passwords match
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

from django import forms
from .models import PredefinedQuestion

class PredefinedQuestionForm(forms.ModelForm):
    class Meta:
        model = PredefinedQuestion
        fields = ['text']
from django import forms
from .models import Review

from django import forms

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']