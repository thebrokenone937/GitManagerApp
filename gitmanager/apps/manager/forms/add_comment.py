from django import forms

class AddCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)
    