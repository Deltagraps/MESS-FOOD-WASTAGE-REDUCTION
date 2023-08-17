from django import forms
from django.contrib.auth.forms import UserCreationForm

from server.models import Student

class RegistrationForm(UserCreationForm):

    rollNumber = forms.CharField(max_length=10, help_text='Roll Number daalo bhai')
    mobileNumber = forms.CharField(max_length=10, help_text='Hello Mobil enumber')

    class Meta:
        model = Student
        fields = ('rollNumber', 'name', 'mobileNumber', 'password1', 'password2')

    def clean_rollNumber(self):
        rollNumber = self.cleaned_data['rollNumber']
        try:
            Student.objects.get(rollNumber = rollNumber).exists()
        except Exception as e:
            return rollNumber
        raise forms.ValidationError(f'Roll Number {rollNumber} is already in use')

        