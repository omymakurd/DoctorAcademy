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
    video_file = forms.FileField(required=False, label="Upload Video") 

    class Meta:
        model = ClinicalLecture
        fields = [
            'module',
            'title',
            'video_file',
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
        module_instance = kwargs.pop('module_instance', None)
        super().__init__(*args, **kwargs)

        # فلترة الموديولات الخاصة بالمستخدم
        if user and getattr(user, 'is_authenticated', False):
            self.fields['module'].queryset = Module.objects.filter(
                clinical_system__isnull=False, instructor=user
            )

        # إذا تم تمرير module_instance، نخفي الحقل أو نجعله غير مطلوب
        if module_instance:
            self.fields['module'].initial = module_instance
            self.fields['module'].widget = forms.HiddenInput()
            self.fields['module'].required = False
# lectures/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Quiz, Question, Choice

# فورم الكويز نفسه
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'lecture_type', 'basic_lecture', 'clinical_lecture', 'time_limit_minutes', 'shuffle_questions']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'time_limit_minutes': forms.NumberInput(attrs={'class':'form-control'}),
            'shuffle_questions': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

# فورم السؤال
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class':'form-control', 'rows':2}),
        }

# فورم الاختيار
class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class':'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

# inline formsets
QuestionFormSet = inlineformset_factory(
    Quiz, Question, form=QuestionForm,
    extra=1, can_delete=True
)

ChoiceFormSet = inlineformset_factory(
    Question, Choice, form=ChoiceForm,
    extra=4, can_delete=True
)
