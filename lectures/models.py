from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

# ========================
# Lecture Categories
# ========================
class LectureCategory(models.Model):
    CATEGORY_TYPES = [
        ('basic', 'Basic Sciences'),
        ('clinical', 'Clinical Medicine'),
    ]
    name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category_type})"


# ========================
# Basic Sciences
# ========================
class BasicSystem(models.Model):
    category = models.ForeignKey(LectureCategory, on_delete=models.CASCADE, related_name='basic_systems')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('category', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.category.name}"


class Discipline(models.Model):
    system = models.ForeignKey(BasicSystem, on_delete=models.CASCADE, related_name='disciplines')
    DISCIPLINE_CHOICES = [
        ('anatomy','Anatomy'),
        ('embryology','Embryology'),
        ('histology','Histology'),
        ('physiology','Physiology'),
        ('pathology','Pathology'),
        ('pharmacology','Pharmacology'),
    ]
    name = models.CharField(max_length=20, choices=DISCIPLINE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('system', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.system.name} - {self.get_name_display()}"


# ========================
# Clinical Sciences
# ========================
class ClinicalSystem(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ========================
# Module
# ========================
class Module(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
    ]

    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modules')
    title = models.CharField(max_length=255, default="Untitled Module")
    basic_system = models.ForeignKey(BasicSystem, on_delete=models.CASCADE, related_name='modules', null=True, blank=True)
    clinical_system = models.ForeignKey(ClinicalSystem, on_delete=models.CASCADE, related_name='modules', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='modules/thumbnails/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_featured = models.BooleanField(default=False)

    instructor_share = models.DecimalField(max_digits=5, decimal_places=2, default=50.0)
    platform_share = models.DecimalField(max_digits=5, decimal_places=2, default=50.0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # optional: total duration in minutes or hours
    total_duration_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        system_name = self.basic_system.name if self.basic_system else (self.clinical_system.name if self.clinical_system else "No System")
        return f"{self.title} ({system_name})"


# ========================
# Lectures (Basic + Clinical)
# ========================
class LectureBase(models.Model):
    LECTURE_TYPE_CHOICES = [('recorded','Recorded Video'),('zoom','Live Zoom')]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='%(class)ss', null=True, blank=True)
    title = models.CharField(max_length=255)
    lecture_type = models.CharField(max_length=20, choices=LECTURE_TYPE_CHOICES, default='recorded')
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    # common instructor and revenue split
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)ss')
    instructor_share = models.DecimalField(max_digits=5, decimal_places=2, default=50.0)

    resources = models.FileField(upload_to='lectures/resources/', blank=True, null=True)  # pdf/slides etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['order']


class BasicLecture(LectureBase):
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='basic_lectures')
    video_file = models.FileField(upload_to='lectures/videos/', blank=True, null=True)
    # streaming: store video id / storage path rather than direct public url
    video_storage_id = models.CharField(max_length=255, blank=True, null=True)

    # Zoom fields (for live sessions)
    zoom_link = models.URLField(blank=True, null=True)
    zoom_meeting_id = models.CharField(max_length=100, blank=True, null=True)
    zoom_start_time = models.DateTimeField(blank=True, null=True)
    zoom_duration = models.IntegerField(blank=True, null=True)  # minutes
    zoom_join_url = models.URLField(blank=True, null=True)
    zoom_start_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.discipline.get_name_display()}"


class ClinicalLecture(LectureBase):
    video_url = models.URLField(blank=True, null=True)
    zoom_link = models.URLField(blank=True, null=True)
    zoom_meeting_id = models.CharField(max_length=100, blank=True, null=True)
    zoom_start_time = models.DateTimeField(blank=True, null=True)
    zoom_duration = models.IntegerField(blank=True, null=True)  # minutes
    zoom_join_url = models.URLField(blank=True, null=True)
    zoom_start_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title


# ========================
# Interactive Notes
# ========================
class InteractiveNote(models.Model):
    lecture_type_choices = [
        ('basic', 'BasicLecture'),
        ('clinical', 'ClinicalLecture'),
    ]
    lecture_type = models.CharField(max_length=10, choices=lecture_type_choices)
    basic_lecture = models.ForeignKey(BasicLecture, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    clinical_lecture = models.ForeignKey(ClinicalLecture, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.lecture_type == 'basic' and self.basic_lecture:
            return f"Note by {self.student.username} on {self.basic_lecture.title}"
        elif self.lecture_type == 'clinical' and self.clinical_lecture:
            return f"Note by {self.student.username} on {self.clinical_lecture.title}"
        return f"Note by {self.student.username}"


# ========================
# Quiz / Question / Choice
# ========================
class Quiz(models.Model):
    lecture_type_choices = [
        ('basic', 'BasicLecture'),
        ('clinical', 'ClinicalLecture'),
    ]
    lecture_type = models.CharField(max_length=10, choices=lecture_type_choices)
    basic_lecture = models.ForeignKey(BasicLecture, on_delete=models.CASCADE, null=True, blank=True, related_name='quizzes')
    clinical_lecture = models.ForeignKey(ClinicalLecture, on_delete=models.CASCADE, null=True, blank=True, related_name='quizzes')
    title = models.CharField(max_length=255)
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)  # optional
    shuffle_questions = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    # for multi-choice; keep correct_answer optional and prefer choices' is_correct
    correct_answer = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text[:80]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


# ========================
# Lecture Progress + Module Enrollment + Module Progress
# ========================
class LectureProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lecture_progress')
    basic_lecture = models.ForeignKey(BasicLecture, on_delete=models.CASCADE, null=True, blank=True)
    clinical_lecture = models.ForeignKey(ClinicalLecture, on_delete=models.CASCADE, null=True, blank=True)
    status_choices = [('in_progress','In Progress'),('completed','Completed')]
    status = models.CharField(max_length=20, choices=status_choices, default='in_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (
            ('student', 'basic_lecture'),
            ('student', 'clinical_lecture'),
        )

    def update_status(self):
        lecture = self.basic_lecture or self.clinical_lecture
        quizzes = lecture.quizzes.all()
        passed_quizzes = all(
            quiz.attempts.filter(student=self.student, completed=True, score__gte=50).exists()
            for quiz in quizzes
        )
        if passed_quizzes:
            self.status = 'completed'
            self.completed_at = timezone.now()
        else:
            self.status = 'in_progress'
        self.save()

    def __str__(self):
        lecture_name = self.basic_lecture.title if self.basic_lecture else (self.clinical_lecture.title if self.clinical_lecture else "No Lecture")
        return f"{self.student.username} - {lecture_name} - {self.status}"

class ModuleEnrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_enrollments')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='enrollments')
    purchased_price = models.DecimalField(max_digits=8, decimal_places=2)
    access_expires_at = models.DateTimeField(null=True, blank=True)  # for timed access (optional)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'module')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.module.title}"


class ModuleProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progress')
    completed_basic_lectures = models.ManyToManyField(BasicLecture, blank=True, related_name='+')
    completed_clinical_lectures = models.ManyToManyField(ClinicalLecture, blank=True, related_name='+')
    progress_percentage = models.FloatField(default=0.0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'module')

    def recalc_progress(self):
        total = 0
        completed = 0
        # count total lectures in module
        total = self.module.basic_lectures.count() + self.module.clinical_lectures.count()
        completed = self.completed_basic_lectures.count() + self.completed_clinical_lectures.count()
        self.progress_percentage = (completed / total * 100) if total else 0.0
        self.save()

    def __str__(self):
        return f"{self.student.username} - {self.module.title} - {self.progress_percentage:.2f}%"


# ========================
# Video Access Token (for secure streaming)
# ========================
class VideoAccessToken(models.Model):
    lecture = models.ForeignKey(BasicLecture, on_delete=models.CASCADE, related_name='access_tokens')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"Token for {self.user} - {self.lecture.title}"


# ========================
# Reviews & Ratings
# ========================
class LectureReview(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lecture_reviews')
    basic_lecture = models.ForeignKey(BasicLecture, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    clinical_lecture = models.ForeignKey(ClinicalLecture, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5)  # 1..5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        target = self.basic_lecture.title if self.basic_lecture else (self.clinical_lecture.title if self.clinical_lecture else "Unknown")
        return f"{self.student.username} - {target} ({self.rating})"


# ========================
# Certificates
# ========================
class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='certificates')
    certificate_file = models.FileField(upload_to='certificates/')
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'module')

    def __str__(self):
        return f"Certificate: {self.student.username} - {self.module.title}"


# ========================
# Earnings & Payments (simplified)
# ========================
class InstructorEarning(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="earnings")
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.instructor.username} - {self.amount} ({'paid' if self.is_paid else 'unpaid'})"


class PaymentMethod(models.Model):
    METHOD_CHOICES = [
        ("stripe", "Stripe"),
        ("paypal", "PayPal"),
        ("paymob", "Paymob"),
        ("paytabs", "PayTabs"),
        ("tabby", "Tabby / Tamara"),
        ("vodafone_cash", "Vodafone Cash"),
    ]

    name = models.CharField(max_length=50, choices=METHOD_CHOICES, unique=True)
    active = models.BooleanField(default=True)
    config = models.JSONField(blank=True, null=True)  # store gateway config like keys, webhook urls, etc.

    def __str__(self):
        return self.get_name_display()


class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    payment = models.OneToOneField(
    'payments.Payment',
    on_delete=models.CASCADE,
    related_name='transaction',
    null=True, blank=True
)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reference_id = models.CharField(max_length=255, blank=True, null=True)
    meta = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} - {self.status}"
class QuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.PositiveIntegerField(default=1)
    score = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'quiz', 'attempt_number')

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} Attempt #{self.attempt_number}"

    def mark_submitted(self):
        self.submitted_at = timezone.now()
        self.completed = True
        self.calculate_score()
        self.save()

    def calculate_score(self):
        total_questions = self.quiz.questions.count()
        correct_answers = self.answers.filter(selected_choice__is_correct=True).count()
        self.score = (correct_answers / total_questions * 100) if total_questions else 0

    @property
    def passed(self):
        return self.score >= 50  # أو اجعلها quiz.pass_percentage


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('attempt', 'question')

    @property
    def is_correct(self):
        return self.selected_choice.is_correct if self.selected_choice else False

    def __str__(self):
        return f"{self.attempt} - Q:{self.question.id}"
