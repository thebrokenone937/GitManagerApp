from django import forms

class AddRepositoryForm(forms.Form):
    name = forms.CharField(max_length=100)
    git_url = forms.CharField(max_length=255)
    