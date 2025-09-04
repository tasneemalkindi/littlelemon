from django import forms
from .models import ContactMessage, Reservation, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        labels = {
            'name': 'Name *',
            'email': 'Email *',
            'message': 'Message',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form_style', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form_style', 'placeholder': 'you@example.com'}),
            'message': forms.Textarea(attrs={'class': 'form_style', 'rows': 6, 'placeholder': 'How can we help?'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'date', 'time', 'party_size', 'is_shared']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'party_size': forms.Select(choices=[(i, i) for i in range(1, 11)]),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user is None:
            raise ValueError("ReservationForm requires a user")
        super().__init__(*args, **kwargs)

        self.fields['name'].widget = forms.HiddenInput()
        self.fields['email'].widget = forms.HiddenInput()
        self.fields['name'].initial = user.get_full_name() or user.username
        self.fields['email'].initial = user.email
        self.fields['is_shared'].label = "Shared table?"

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class FindSlotForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    party_size = forms.TypedChoiceField(
        choices=[(i, i) for i in range(1, 16)],
        coerce=int,
        widget=forms.Select()
    )
    is_shared = forms.BooleanField(
        required=False,
        label="Shared table?"
    )

class ReviewForm(forms.ModelForm):
    # make name optional so logged-in users don’t need to type it
    name = forms.CharField(max_length=60, required=False)

    class Meta:
        model = Review
        fields = ["name", "rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Share your experience…"}),
        }
