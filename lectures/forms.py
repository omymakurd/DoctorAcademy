from django import forms
from .models import (
    Module,
    BasicSystem,
    ClinicalSystem,
    BasicLecture,
    ClinicalLecture,
    Discipline
)

# =======================
# Module Form
# =======================
class ModuleForm(forms.ModelForm):
    basic_system = forms.ModelChoiceField(
        queryset=BasicSystem.objects.all(),
        required=False,
        label="Basic System"
    )
    clinical_system = forms.ModelChoiceField(
        queryset=ClinicalSystem.objects.all(),
        required=False,
        label="Clinical System"
    )

    class Meta:
        model = Module
        fields = ['basic_system', 'clinical_system', 'thumbnail', 'description', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        basic = cleaned_data.get('basic_system')
        clinical = cleaned_data.get('clinical_system')

        if not basic and not clinical:
            raise forms.ValidationError("You must select either a Basic System or a Clinical System.")
        if basic and clinical:
            raise forms.ValidationError("You can select only one system type: Basic or Clinical.")

        return cleaned_data



# =======================
# Basic Lecture Form
# =======================
class BasicLectureForm(forms.ModelForm):
    module = forms.ModelChoiceField(
        queryset=Module.objects.filter(basic_system__isnull=False),
        required=True,
        label="Module"
    )

    class Meta:
        model = BasicLecture
        fields = ['module', 'discipline', 'title', 'lecture_type', 'video_file', 'zoom_link', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # إفراغ الـ discipline بالبداية
        self.fields['discipline'].queryset = Discipline.objects.none()

        # فلترة الموديولات حسب المستخدم
        if user and user.is_authenticated:
            self.fields['module'].queryset = Module.objects.filter(basic_system__isnull=False, instructor=user)

        # تحديث الـ discipline عند اختيار الموديول
        if 'module' in self.data:
            try:
                module_id = int(self.data.get('module'))
                module = Module.objects.get(id=module_id)
                if module.basic_system:
                    self.fields['discipline'].queryset = Discipline.objects.filter(system=module.basic_system)
            except (ValueError, TypeError, Module.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.module:
            self.fields['discipline'].queryset = Discipline.objects.filter(system=self.instance.module.basic_system)


# =======================
# Clinical Lecture Form
# =======================
class ClinicalLectureForm(forms.ModelForm):
    module = forms.ModelChoiceField(
        queryset=Module.objects.filter(clinical_system__isnull=False),
        required=True,
        label="Module"
    )

    class Meta:
        model = ClinicalLecture
        fields = ['module', 'title', 'lecture_type', 'video_url', 'zoom_link', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields['module'].queryset = Module.objects.filter(clinical_system__isnull=False, instructor=user)
        else:
            self.fields['module'].queryset = Module.objects.filter(clinical_system__isnull=False)
