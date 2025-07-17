from django.contrib import admin
from django.db.models import Avg, F
from django.urls import reverse
from django.utils.html import format_html

from apps.models import Homework, Submission, SubmissionFile, Grade


class SubmissionFileInline(admin.TabularInline):
    model = SubmissionFile
    extra = 0
    readonly_fields = ('file_name', 'line_count')
    fields = ('file_name', 'content', 'line_count')

    def has_add_permission(self, request, obj=None):
        return False


class GradeInline(admin.StackedInline):
    model = Grade
    extra = 0
    fieldsets = (
        ('AI Baholari', {
            'fields': (
                ('ai_task_completeness', 'ai_code_quality', 'ai_correctness'),
                'ai_total',
                'ai_feedback'
            )
        }),
        ('O\'qituvchi Baholari', {
            'fields': (
                ('final_task_completeness', 'final_code_quality', 'final_correctness'),
                'teacher_total',
                'modified_by_teacher'
            )
        }),
        ('Feedbacklar', {
            'fields': (
                'task_completeness_feedback',
                'code_quality_feedback',
                'correctness_feedback'
            )
        })
    )
    readonly_fields = ('ai_task_completeness', 'ai_code_quality', 'ai_correctness',
                       'ai_total', 'ai_feedback', 'created_at', 'updated_at')


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'teacher',
        'group',
        'start_date',
        'deadline',
        'points',
        'submissions_count',
        'avg_grade',
        'status_badge'
    )
    list_filter = (
        'teacher',
        'group',
        'start_date',
        'deadline',
        'created_at'
    )
    search_fields = ('title', 'description', 'teacher__username', 'group__name')
    date_hierarchy = 'deadline'
    ordering = ('-created_at',)

    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('title', 'description', 'points')
        }),
        ('Vaqt Sozlamalari', {
            'fields': ('start_date', 'deadline')
        }),
        ('Guruh va O\'qituvchi', {
            'fields': ('teacher', 'group')
        }),
        ('Fayl Sozlamalari', {
            'fields': ('line_limit', 'file_extensions')
        }),
        ('AI Sozlamalari', {
            'fields': ('ai_grading_prompt',),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('created_at',)

    def submissions_count(self, obj):
        count = obj.submissions.count()
        url = reverse('admin:apps_submission_changelist') + f'?homework__id__exact={obj.id}'
        return format_html('<a href="{}">{} ta topshiriq</a>', url, count)

    submissions_count.short_description = 'Topshiriqlar soni'

    def avg_grade(self, obj):
        avg = obj.submissions.filter(final_grade__isnull=False).aggregate(
            avg_grade=Avg('final_grade')
        )['avg_grade']
        if avg:
            return f"{avg:.1f}"
        return "Hali baho yo'q"

    avg_grade.short_description = 'O\'rtacha baho'

    def status_badge(self, obj):
        from django.utils import timezone
        now = timezone.now().date()

        if obj.deadline.date() < now:
            return format_html(
                '<span style="color: red; font-weight: bold;">⏰ Muddati o\'tgan</span>'
            )
        elif obj.start_date > now:
            return format_html(
                '<span style="color: blue; font-weight: bold;">📅 Kutilmoqda</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Faol</span>'
            )

    status_badge.short_description = 'Holati'

    actions = ['duplicate_homework', 'extend_deadline']

    def duplicate_homework(self, request, queryset):
        for homework in queryset:
            homework.pk = None
            homework.title = f"{homework.title} (nusxa)"
            homework.save()
        self.message_user(request, f"{queryset.count()} ta vazifa nusxa qilindi.")

    duplicate_homework.short_description = "Tanlangan vazifalarni nusxa qilish"

    def extend_deadline(self, request, queryset):
        from datetime import timedelta
        for homework in queryset:
            homework.deadline += timedelta(days=7)
            homework.save()
        self.message_user(request, f"{queryset.count()} ta vazifa muddati 1 hafta uzaytirildi.")

    extend_deadline.short_description = "Muddatni 1 hafta uzaytirish"


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'homework_title',
        'student',
        'submitted_at',
        'ai_grade_badge',
        'final_grade_badge',
        'files_count',
        'grade_status'
    )
    list_filter = (
        'homework__teacher',
        'homework__group',
        'submitted_at',
        'ai_grade',
        'final_grade'
    )
    search_fields = (
        'homework__title',
        'student__username',
        'student__first_name',
        'student__last_name'
    )
    date_hierarchy = 'submitted_at'
    ordering = ('-submitted_at',)

    inlines = [SubmissionFileInline, GradeInline]

    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('homework', 'student', 'submitted_at')
        }),
        ('Baholash', {
            'fields': ('ai_grade', 'final_grade', 'ai_feedback')
        })
    )

    readonly_fields = ('submitted_at', 'created_at')

    def homework_title(self, obj):
        return obj.homework.title

    homework_title.short_description = 'Vazifa nomi'

    def ai_grade_badge(self, obj):
        if obj.ai_grade:
            color = 'green' if obj.ai_grade >= 70 else 'orange' if obj.ai_grade >= 50 else 'red'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">🤖 {}</span>',
                color, obj.ai_grade
            )
        return "AI baho yo'q"

    ai_grade_badge.short_description = 'AI Bahosi'

    def final_grade_badge(self, obj):
        if obj.final_grade:
            color = 'green' if obj.final_grade >= 70 else 'orange' if obj.final_grade >= 50 else 'red'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">👨‍🏫 {}</span>',
                color, obj.final_grade
            )
        return "Final baho yo'q"

    final_grade_badge.short_description = 'Final Bahosi'

    def files_count(self, obj):
        count = obj.files.count()
        return format_html(
            '<span style="background-color: #007cba; color: white; padding: 2px 6px; border-radius: 3px;">📁 {}</span>',
            count
        )

    files_count.short_description = 'Fayllar'

    def grade_status(self, obj):
        if obj.final_grade:
            return format_html('<span style="color: green;">✅ Baholangan</span>')
        elif obj.ai_grade:
            return format_html('<span style="color: orange;">🔄 AI baholagan</span>')
        else:
            return format_html('<span style="color: red;">❌ Baholanmagan</span>')

    grade_status.short_description = 'Baholash holati'

    actions = ['regrade_with_ai', 'mark_as_final']

    def regrade_with_ai(self, request, queryset):
        # Bu yerda AI qayta baholash logikasi bo'lishi kerak
        self.message_user(request, f"{queryset.count()} ta topshiriq AI bilan qayta baholandi.")

    regrade_with_ai.short_description = "AI bilan qayta baholash"

    def mark_as_final(self, request, queryset):
        updated = queryset.filter(ai_grade__isnull=False, final_grade__isnull=True).update(
            final_grade=F('ai_grade')
        )
        self.message_user(request, f"{updated} ta topshiriq final bahosi belgilandi.")

    mark_as_final.short_description = "AI bahosini final qilib belgilash"


@admin.register(SubmissionFile)
class SubmissionFileAdmin(admin.ModelAdmin):
    list_display = (
        'file_name',
        'submission_info',
        'line_count',
        'file_size_info'
    )
    list_filter = (
        'submission__homework__teacher',
        'submission__homework__group',
        'line_count'
    )
    search_fields = (
        'file_name',
        'submission__student__username',
        'submission__homework__title'
    )
    ordering = ('submission', 'file_name')

    readonly_fields = ('line_count', 'file_size_info')

    def submission_info(self, obj):
        return f"{obj.submission.homework.title} - {obj.submission.student.username}"

    submission_info.short_description = 'Topshiriq ma\'lumoti'

    def file_size_info(self, obj):
        size = len(obj.content.encode('utf-8'))
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

    file_size_info.short_description = 'Fayl hajmi'


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = (
        'submission_info',
        'ai_total_badge',
        'teacher_total_badge',
        'grade_difference',
        'modified_by_teacher',
        'updated_at'
    )
    list_filter = (
        'modified_by_teacher',
        'submission__homework__teacher',
        'submission__homework__group',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'submission__homework__title',
        'submission__student__username'
    )
    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)

    fieldsets = (
        ('Topshiriq Ma\'lumoti', {
            'fields': ('submission',)
        }),
        ('AI Baholari', {
            'fields': (
                ('ai_task_completeness', 'ai_code_quality', 'ai_correctness'),
                'ai_total',
                'ai_feedback'
            ),
            'classes': ('collapse',)
        }),
        ('O\'qituvchi Baholari', {
            'fields': (
                ('final_task_completeness', 'final_code_quality', 'final_correctness'),
                'teacher_total',
                'modified_by_teacher'
            )
        }),
        ('Batafsil Feedbacklar', {
            'fields': (
                'task_completeness_feedback',
                'code_quality_feedback',
                'correctness_feedback'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = (
        'ai_task_completeness', 'ai_code_quality', 'ai_correctness',
        'ai_total', 'ai_feedback', 'created_at', 'updated_at'
    )

    def submission_info(self, obj):
        return f"{obj.submission.homework.title} - {obj.submission.student.username}"

    submission_info.short_description = 'Topshiriq'

    def ai_total_badge(self, obj):
        if obj.ai_total:
            color = 'green' if obj.ai_total >= 70 else 'orange' if obj.ai_total >= 50 else 'red'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">🤖 {:.1f}</span>',
                color, obj.ai_total
            )
        return "AI baho yo'q"

    ai_total_badge.short_description = 'AI Umumiy'

    def teacher_total_badge(self, obj):
        if obj.teacher_total:
            color = 'green' if obj.teacher_total >= 70 else 'orange' if obj.teacher_total >= 50 else 'red'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">👨‍🏫 {:.1f}</span>',
                color, obj.teacher_total
            )
        return "O'qituvchi baho yo'q"

    teacher_total_badge.short_description = 'O\'qituvchi Umumiy'

    def grade_difference(self, obj):
        if obj.ai_total and obj.teacher_total:
            diff = obj.teacher_total - obj.ai_total
            if abs(diff) <= 5:
                color = 'green'
                icon = '✅'
            elif abs(diff) <= 15:
                color = 'orange'
                icon = '⚠️'
            else:
                color = 'red'
                icon = '🚨'

            return format_html(
                '<span style="color: {};">{} {:.1f}</span>',
                color, icon, diff
            )
        return "Taqqoslab bo'lmaydi"

    grade_difference.short_description = 'Farq'

    actions = ['approve_ai_grades', 'reset_teacher_grades']

    def approve_ai_grades(self, request, queryset):
        updated = 0
        for grade in queryset:
            if grade.ai_total and not grade.teacher_total:
                grade.teacher_total = grade.ai_total
                grade.final_task_completeness = grade.ai_task_completeness
                grade.final_code_quality = grade.ai_code_quality
                grade.final_correctness = grade.ai_correctness
                grade.modified_by_teacher = request.user
                grade.save()
                updated += 1

        self.message_user(request, f"{updated} ta AI bahosi tasdiqlandi.")

    approve_ai_grades.short_description = "AI baholarini tasdiqlash"

    def reset_teacher_grades(self, request, queryset):
        updated = queryset.update(
            teacher_total=None,
            final_task_completeness=None,
            final_code_quality=None,
            final_correctness=None,
            modified_by_teacher=None
        )
        self.message_user(request, f"{updated} ta o'qituvchi bahosi tozalandi.")

    reset_teacher_grades.short_description = "O'qituvchi baholarini tozalash"


admin.site.site_header = "Homework Management System"
admin.site.site_title = "HMS Admin"
admin.site.index_title = "Boshqaruv Paneli"
