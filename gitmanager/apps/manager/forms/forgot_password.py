from django import forms

class ForgotPasswordForm(forms.Form):
    email = forms.CharField(max_length=255)
    