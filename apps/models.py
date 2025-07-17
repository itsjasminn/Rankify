from django.db.models import ForeignKey, CASCADE, TextField, DateTimeField, SET_NULL, TextChoices
from django.db.models import Model, IntegerField, DateField,DecimalField,CharField,FileField


class Homework(Model):
    class FileType(TextChoices):
        PYTHON = ".py", "Python"
        JAVASCRIPT = ".js", "JavaScript"
        TYPESCRIPT = ".ts", "TypeScript"
        HTML = ".html", "HTML"
        CSS = ".css", "CSS"
        JSON = ".json", "JSON"
        YAML = ".yaml", "YAML"
        YML = ".yml", "YML"
        MARKDOWN = ".md", "Markdown"
        TXT = ".txt", "Text"
        JAVA = ".java", "Java"
        C = ".c", "C"
        CPP = ".cpp", "C++"
        CS = ".cs", "C#"
        GO = ".go", "Go"
        PHP = ".php", "PHP"
        RUBY = ".rb", "Ruby"
        RUST = ".rs", "Rust"

    title = CharField(max_length=255)
    description = TextField()
    points = IntegerField()
    start_date = DateField()
    deadline = DateTimeField()
    line_limit = IntegerField()
    teacher = ForeignKey('auth_apps.User', on_delete=CASCADE, related_name='homeworks')
    group = ForeignKey('auth_apps.Group', on_delete=CASCADE, related_name='homeworks')
    file_extensions = CharField(max_length=255,choices=FileType,default=FileType.TXT)
    ai_grading_prompt = TextField()
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Submission(Model):
    homework = ForeignKey('apps.Homework', on_delete=CASCADE, related_name='submissions')
    student = ForeignKey('auth_apps.User', on_delete=CASCADE, related_name='submissions')
    submitted_at = DateTimeField(auto_now_add=True)
    ai_grade = IntegerField()
    final_grade = IntegerField()
    ai_feedback = TextField()
    created_at = DateTimeField(auto_now_add=True)


class SubmissionFile(Model):
    submission = ForeignKey('apps.Submission', on_delete=CASCADE, related_name='files')
    file_name = CharField(max_length=255)
    content = FileField()
    line_count = IntegerField()


class Grade(Model):
    submission = ForeignKey('apps.Submission', on_delete=CASCADE, related_name='grades')
    # AI baholari
    ai_task_completeness = DecimalField(max_digits=5, decimal_places=2)
    ai_code_quality = DecimalField(max_digits=5, decimal_places=2)
    ai_correctness = DecimalField(max_digits=5, decimal_places=2)
    ai_total = DecimalField(max_digits=5, decimal_places=2)
    # Final baho (o'qituvchi tomonidan tahrirlangan)
    final_task_completeness = DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_code_quality = DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_correctness = DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_total = DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # Fikrlar (feedbacklar)
    ai_feedback = TextField(null=True, blank=True)
    task_completeness_feedback = TextField(null=True, blank=True)
    code_quality_feedback = TextField(null=True, blank=True)
    correctness_feedback = TextField(null=True, blank=True)
    # Tahrirlagan o‘qituvchi
    modified_by_teacher = ForeignKey('auth_apps.User', on_delete=SET_NULL, null=True, blank=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Grade for submission {self.submission_id}"
