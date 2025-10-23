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
