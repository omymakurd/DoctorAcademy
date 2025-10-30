# courses/forms.py
from django import forms
from .models import Course, CourseUnit

# ========================
# Course Form
# ========================
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Course description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# ========================
# Course Unit Form
# ========================
from django import forms
from .models import CourseUnit

class CourseUnitForm(forms.ModelForm):
    class Meta:
        model = CourseUnit
        fields = ['title', 'description', 'content_type', 'content_url', 'content_file', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Unit description'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'content_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL (if applicable)'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        content_file = cleaned_data.get('content_file')
        content_url = cleaned_data.get('content_url')

        # لو النوع محتاج ملف أو رابط
        if content_type in ['video', 'pdf', 'zoom'] and not (content_file or content_url):
            raise forms.ValidationError("You must provide either a file or a URL for this unit.")
        return cleaned_data

# ========================
# Quiz Form (optional, لو تريد تعمل إدارة الكويزات)
# ========================
# يمكنك إضافة QuizForm و QuestionForm إذا أحببت إدارة الأسئلة من الفورمز
