from django import forms
from .models import CaseStudy

class CaseStudyForm(forms.ModelForm):
    class Meta:
        model = CaseStudy
        exclude = ['discipline', 'basic_lecture', 'clinical_lecture', 'created_by']  # exclude created_by

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # جعل بعض الحقول غير إلزامية لتوفير المرونة
        optional_fields = ['video', 'video_url', 'attachment', 'symptoms', 'analysis', 'description', 'title']
        for field in optional_fields:
            if field in self.fields:
                self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        # التحقق من أن هناك محتوى على الأقل
        if not any([
            cleaned_data.get('video'),
            cleaned_data.get('video_url'),
            cleaned_data.get('attachment'),
            cleaned_data.get('symptoms'),
            cleaned_data.get('analysis'),
            cleaned_data.get('title')
        ]):
            raise forms.ValidationError("Please provide some content — text, video, or file.")
        return cleaned_data
        
from django import forms
from .models import CaseStudyNew

class CaseStudyNewForm(forms.ModelForm):
    LEVEL_CHOICES = [
        ('Year 1', 'Year 1'),
        ('Year 2', 'Year 2'),
        ('Year 3', 'Year 3'),
        ('Intern', 'Intern'),
        ('Resident', 'Resident'),
    ]

    target_level = forms.ChoiceField(choices=LEVEL_CHOICES, label="Level")
    is_paid = forms.BooleanField(required=False, label="Is Paid?")
    price = forms.DecimalField(required=False, max_digits=8, decimal_places=2, label="Price (USD)")

    class Meta:
        model = CaseStudyNew
        fields = [
            'title', 'discipline', 'target_level', 'description',
            'learning_objectives', 'pdf_file', 'image_file', 'thumbnail',
            'is_paid', 'price', 'session_date', 'session_time'
            # 🔥 تم حذف zoom_link
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'discipline': forms.Select(attrs={'class': 'form-select'}),
            'target_level': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'learning_objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pdf_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'session_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
