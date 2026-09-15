from django import forms


class AdminTokenApprovalForm(forms.Form):

    token = forms.CharField(
        label="Admin Token",
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "off",
            }
        ),
    )