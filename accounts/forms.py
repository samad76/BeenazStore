from django import forms
from .models import Accounts, userProfile


class RegistrationForm(forms.ModelForm):
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))
    class Meta:
        model = Accounts
        fields = ['first_name', 'last_name','phone_number', 'email', 'password', 'confirm_password']

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}),
            'confirm_password': forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
    




class UserForm(forms.ModelForm):
    class Meta:
        model = Accounts
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'    




class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)   
    class Meta:
        model = userProfile
        fields = ('address_line_1','address_line_2', 'city','province','country' ,'profile_picture',)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'            