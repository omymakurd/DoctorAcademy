from django import forms
from .models import BasicLecture, ClinicalLecture, Discipline, ClinicalSystem , BasicSystem



class BasicLectureForm(forms.ModelForm):
    system = forms.ModelChoiceField(
        queryset=BasicSystem.objects.all(),
        required=True,
        label="System"
    )

    class Meta:
        model = BasicLecture
        fields = ['system', 'discipline', 'title', 'lecture_type', 'video_file', 'zoom_link', 'description', 'price']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['discipline'].queryset = Discipline.objects.none()

        if 'system' in self.data:
            try:
                system_id = int(self.data.get('system'))
                self.fields['discipline'].queryset = Discipline.objects.filter(system_id=system_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['discipline'].queryset = self.instance.system.disciplines.all()

class ClinicalLectureForm(forms.ModelForm):
    class Meta:
        model = ClinicalLecture
        fields = ['system', 'title', 'lecture_type', 'zoom_link', 'description', 'price']  # ⬅️ شلنا video_url
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['system'].queryset = ClinicalSystem.objects.all()
