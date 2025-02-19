from django import forms
from django.core.mail import send_mail
from django.conf import settings

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 4}))

    def send_email(self):
        """Send an email to the admin with the message details."""
        subject = f"New Contact Form Submission from {self.cleaned_data['name']}"
        message = f"Sender: {self.cleaned_data['name']} ({self.cleaned_data['email']})\n\n{self.cleaned_data['message']}"
        admin_email = settings.ADMIN_EMAIL  # Set this in your settings
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])
