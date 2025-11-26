from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Event, Category

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False  # will be activated via email
        if commit:
            user.save()
        return user

class EventForm(forms.ModelForm):
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type":"datetime-local"}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type":"datetime-local"}))

    class Meta:
        model = Event
        fields = ("title", "description", "category", "start_time", "end_time", "image")