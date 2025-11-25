from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Profile
from apps.films.models import Film

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    # Optional: validate email uniqueness
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use.")
        return email


class SignInForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)




class UserProfileForm(forms.ModelForm):
    favorite_films = forms.ModelMultipleChoiceField(
        queryset=Film.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'multi-select'})
    )
    watchlist = forms.ModelMultipleChoiceField(
        queryset=Film.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'multi-select'})
    )

    class Meta:
        model = Profile
        fields = ['location', 'website', 'bio', 'avatar', 'favorite_films', 'watchlist']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'location': forms.TextInput(),
            'website': forms.URLInput(),
        }