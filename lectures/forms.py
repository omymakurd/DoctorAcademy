# lectures/forms.py
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
        fields = [
            'title',              # ✅ أضف هذا
            'basic_system',
            'clinical_system',
            'thumbnail',
            'description',
            'price',
            'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


# =======================
# الحقول الخاصة بـ Zoom
# =======================
_ZOOM_FIELDS = [
    'zoom_link',
    'zoom_meeting_id',
    'zoom_start_time',
    'zoom_duration',
    'zoom_join_url',
    'zoom_start_url',
]


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
        fields = [
            'module',
            'discipline',
            'title',
            'lecture_type',
            'video_file',
            'description',
            * _ZOOM_FIELDS,  # نضيف حقول الزووم هنا لتكون في الفورم ولكن مخفية
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'zoom_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # فلترة الموديولات للمحاضر الحالي فقط
        if user and getattr(user, 'is_authenticated', False):
            self.fields['module'].queryset = Module.objects.filter(
                basic_system__isnull=False, instructor=user
            )

        # إعداد discipline ليكون فارغ مبدئيًا ويتحدث حسب الموديول
        self.fields['discipline'].queryset = Discipline.objects.none()

        if 'module' in self.data:
            try:
                module_id = int(self.data.get('module'))
                module = Module.objects.get(id=module_id)
                if module.basic_system:
                    self.fields['discipline'].queryset = Discipline.objects.filter(system=module.basic_system)
            except (ValueError, TypeError, Module.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.module:
            # عند التعديل، نملأ الـ disciplines حسب الموديول الحالي
            if self.instance.module.basic_system:
                self.fields['discipline'].queryset = Discipline.objects.filter(
                    system=self.instance.module.basic_system
                )

        # إخفاء حقول الزووم من الواجهة (تبقى موجودة للبرمجة فقط)
  

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
        fields = [
            'module',
            'title',
            'lecture_type',
            'video_url',
            'description',
            * _ZOOM_FIELDS,
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'zoom_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # فلترة الموديولات الخاصة بالمستخدم
        if user and getattr(user, 'is_authenticated', False):
            self.fields['module'].queryset = Module.objects.filter(
                clinical_system__isnull=False, instructor=user
            )

        
