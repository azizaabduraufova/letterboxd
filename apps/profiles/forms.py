from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Profile
from apps.films.models import Film, Review


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

    def clean_favorite_films(self):
        films = self.cleaned_data.get('favorite_films')
        if films and films.count() > 4:
            raise forms.ValidationError("You can select at most 4 favorite films.")
        return films


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']  # Fields that can be edited by the user
        widgets = {
            'rating': forms.NumberInput(attrs={
                'placeholder': 'Enter rating (e.g., 8.5)',
                'step': '0.1',
                'min': '0',
                'max': '10'
            }),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Write your review here...',
                'rows': 5
            }),
        }
        labels = {
            'rating': 'Your Rating',
            'comment': 'Your Comment',
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')

        if rating is not None:
            if rating < 0 or rating > 10:
                raise forms.ValidationError("The rating must be between 0 and 10.")

        return rating
