from django import forms
from .models import Student, Semester, CalculateGp

class CalculateGpForm(forms.ModelForm):
    class Meta:
        model = CalculateGp
        fields = ['course_code', 'course_title', 'course_unit', 'course_grade']
