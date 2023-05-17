from django import forms
from .models import Student, Semester, CalculateGp

class CalculateGpForm(forms.ModelForm):
    class Meta:
        model = CalculateGp
        fields = ['course_code', 'course_title', 'course_unit', 'course_grade']
        
class DESKeyForm(forms.Form):
    key = forms.CharField(label='Key', max_length=8, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
class RSAKeyPairForm(forms.Form):
    public_key = forms.CharField(widget=forms.Textarea)
    private_key = forms.CharField(widget=forms.Textarea)