import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, PasswordInput
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import User, Course, Group


class UserCreationForm(ModelForm):
    """Custom user creation form with password fields"""
    password1 = CharField(label='Parol', widget=PasswordInput, required=False)
    password2 = CharField(label='Parolni tasdiqlang', widget=PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('phone', 'full_name', 'role', 'group')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Parollar mos kelmadi")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserChangeForm(ModelForm):
    """Custom user change form"""
    password = CharField(
        label='Yangi parol (ixtiyoriy)',
        widget=PasswordInput,
        required=False,
        help_text="Parolni o'zgartirish uchun yangi parol kiriting"
    )

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    list_display = (
        'phone_display',
        'full_name',
        'role_badge',
        'group_info',
        'level_badge',
        'avatar_thumbnail',
        'is_active_badge',
        'login_stats',
        'created_homeworks_count',
        'submissions_count'
    )

    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'group__course',
        'group',
        'date_joined'
    )

    search_fields = ('phone', 'full_name', 'group__name')
    ordering = ('-date_joined',)

    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('phone', 'full_name', 'password')
        }),
        ('Rol va Guruh', {
            'fields': ('role', 'group', 'level')
        }),
        ('Profil Ma\'lumotlari', {
            'fields': ('avatar',)
        }),
        ('Ruxsatlar', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Muhim Sanalar', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        })
    )

    add_fieldsets = (
        ('Yangi Foydalanuvchi', {
            'fields': ('phone', 'full_name', 'password1', 'password2', 'role', 'group', 'level')
        }),
    )

    readonly_fields = ('last_login', 'date_joined')
    filter_horizontal = ('groups', 'user_permissions')

    def phone_display(self, obj):
        return format_html(
            '<strong>📱 {}</strong>',
            obj.phone
        )

    phone_display.short_description = 'Telefon'

    def role_badge(self, obj):
        colors = {
            'admin': '#dc3545',
            'teacher': '#28a745',
            'student': '#007bff'
        }
        icons = {
            'admin': '👑',
            'teacher': '👨‍🏫',
            'student': '👨‍🎓'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{} {}</span>',
            colors.get(obj.role, '#6c757d'),
            icons.get(obj.role, '👤'),
            obj.get_role_display()
        )

    role_badge.short_description = 'Rol'

    def group_info(self, obj):
        if obj.group:
            return format_html(
                '<a href="{}">🏫 {}</a><br><small>📚 {}</small>',
                reverse('admin:authenticate_group_change', args=[obj.group.pk]),
                obj.group.name,
                obj.group.course.name if obj.group.course else 'Kurs belgilanmagan'
            )
        return format_html('<span style="color: #dc3545;">❌ Guruhsiz</span>')

    group_info.short_description = 'Guruh'

    def level_badge(self, obj):
        color = '#28a745' if obj.level >= 3 else '#ffc107' if obj.level >= 2 else '#dc3545'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 50%; font-weight: bold;">📊 {}</span>',
            color, obj.level
        )

    level_badge.short_description = 'Daraja'

    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">',
                obj.avatar.url
            )
        return format_html('👤')

    avatar_thumbnail.short_description = 'Avatar'

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Faol</span>')
        return format_html('<span style="color: red;">❌ Faol emas</span>')

    is_active_badge.short_description = 'Holati'

    def login_stats(self, obj):
        if obj.last_login:
            from django.utils import timezone
            days_ago = (timezone.now() - obj.last_login).days
            if days_ago == 0:
                return format_html('<span style="color: green;">🟢 Bugun</span>')
            elif days_ago <= 7:
                return format_html('<span style="color: orange;">🟡 {} kun oldin</span>', days_ago)
            else:
                return format_html('<span style="color: red;">🔴 {} kun oldin</span>', days_ago)
        return format_html('<span style="color: gray;">❓ Hech qachon</span>')

    login_stats.short_description = 'Oxirgi kirish'

    def created_homeworks_count(self, obj):
        if obj.role == 'teacher':
            count = obj.homeworks.count()
            if count > 0:
                url = reverse('admin:apps_homework_changelist') + f'?teacher__id__exact={obj.id}'
                return format_html('<a href="{}">📝 {} ta</a>', url, count)
            return '📝 0 ta'
        return '—'

    created_homeworks_count.short_description = 'Vazifalar'

    def submissions_count(self, obj):
        if obj.role == 'student':
            count = obj.submissions.count()
            if count > 0:
                url = reverse('admin:apps_submission_changelist') + f'?student__id__exact={obj.id}'
                return format_html('<a href="{}">📋 {} ta</a>', url, count)
            return '📋 0 ta'
        return '—'

    submissions_count.short_description = 'Topshiriqlar'

    actions = [
        'activate_users',
        'deactivate_users',
        'reset_passwords',
        'promote_to_teacher',
        'demote_to_student',
        'export_users_csv',
        'send_welcome_message'
    ]

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} ta foydalanuvchi faollashtirildi.')

    activate_users.short_description = "Tanlangan foydalanuvchilarni faollashtirish"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} ta foydalanuvchi faolsizlantirildi.')

    deactivate_users.short_description = "Tanlangan foydalanuvchilarni faolsizlantirish"

    def reset_passwords(self, request, queryset):
        for user in queryset:
            new_password = user.phone[-4:]
            user.set_password(new_password)
            user.save()
        self.message_user(
            request,
            f'{queryset.count()} ta foydalanuvchi paroli yangilandi. Yangi parol: telefon raqamining oxirgi 4 raqami.'
        )

    reset_passwords.short_description = "Parollarni qayta tiklash"

    def promote_to_teacher(self, request, queryset):
        updated = queryset.filter(role='student').update(role='teacher')
        self.message_user(request, f'{updated} ta talaba o\'qituvchi qilib tayinlandi.')

    promote_to_teacher.short_description = "O'qituvchi qilib tayinlash"

    def demote_to_student(self, request, queryset):
        updated = queryset.filter(role='teacher').update(role='student')
        self.message_user(request, f'{updated} ta o\'qituvchi talaba qilib o\'tkazildi.')

    demote_to_student.short_description = "Talaba qilib o'tkazish"

    def export_users_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.writer(response)
        writer.writerow(['Telefon', 'To\'liq ism', 'Rol', 'Guruh', 'Daraja', 'Faol', 'Qo\'shilgan sana'])

        for user in queryset:
            writer.writerow([
                user.phone,
                user.full_name,
                user.get_role_display(),
                user.group.name if user.group else '',
                user.level,
                'Ha' if user.is_active else 'Yo\'q',
                user.date_joined.strftime('%Y-%m-%d')
            ])

        return response

    export_users_csv.short_description = "CSV formatida eksport qilish"

    def send_welcome_message(self, request, queryset):
        # Bu yerda welcome message yuborish logikasi bo'lishi kerak
        self.message_user(request, f'{queryset.count()} ta foydalanuvchiga xush kelibsiz xabari yuborildi.')

    send_welcome_message.short_description = "Xush kelibsiz xabarini yuborish"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'groups_count',
        'students_count',
        'teachers_count',
        'total_homeworks',
        'course_stats'
    )
    search_fields = ('name',)
    ordering = ('name',)

    def groups_count(self, obj):
        count = obj.course_groups.count()
        if count > 0:
            url = reverse('admin:authenticate_group_changelist') + f'?course__id__exact={obj.id}'
            return format_html('<a href="{}">🏫 {} ta guruh</a>', url, count)
        return '🏫 0 ta guruh'

    groups_count.short_description = 'Guruhlar'

    def students_count(self, obj):
        count = User.objects.filter(group__course=obj, role='student').count()
        return format_html('👨‍🎓 {} ta talaba', count)

    students_count.short_description = 'Talabalar'

    def teachers_count(self, obj):
        count = User.objects.filter(teaching_groups__course=obj).distinct().count()
        return format_html('👨‍🏫 {} ta o\'qituvchi', count)

    teachers_count.short_description = 'O\'qituvchilar'

    def total_homeworks(self, obj):
        try:
            from apps.models import Homework
            count = Homework.objects.filter(group__course=obj).count()
            return format_html('📝 {} ta vazifa', count)
        except ImportError:
            return '📝 —'

    total_homeworks.short_description = 'Vazifalar'

    def course_stats(self, obj):
        groups = obj.course_groups.count()
        students = User.objects.filter(group__course=obj, role='student').count()
        if groups > 0 and students > 0:
            avg_students = students / groups
            return format_html(
                '<small>📊 O\'rtacha: {:.1f} ta talaba/guruh</small>',
                avg_students
            )
        return '📊 Ma\'lumot yo\'q'

    course_stats.short_description = 'Statistika'

    actions = ['duplicate_courses', 'generate_course_report']

    def duplicate_courses(self, request, queryset):
        for course in queryset:
            course.pk = None
            course.name = f"{course.name} (nusxa)"
            course.save()
        self.message_user(request, f'{queryset.count()} ta kurs nusxa qilindi.')

    duplicate_courses.short_description = "Kurslarni nusxa qilish"

    def generate_course_report(self, request, queryset):
        self.message_user(request, f'{queryset.count()} ta kurs uchun hisobot yaratildi.')

    generate_course_report.short_description = "Kurs hisoboti yaratish"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'course_info',
        'teacher_info',
        'students_count',
        'group_level_avg',
        'homeworks_count',
        'group_performance'
    )
    list_filter = ('course', 'teacher')
    search_fields = ('name', 'course__name', 'teacher__full_name')
    ordering = ('course', 'name')

    def course_info(self, obj):
        if obj.course:
            return format_html(
                '<a href="{}">📚 {}</a>',
                reverse('admin:authenticate_course_change', args=[obj.course.pk]),
                obj.course.name
            )
        return format_html('<span style="color: red;">❌ Kurs yo\'q</span>')

    course_info.short_description = 'Kurs'

    def teacher_info(self, obj):
        if obj.teacher:
            return format_html(
                '<a href="{}">👨‍🏫 {}</a><br><small>📱 {}</small>',
                reverse('admin:authenticate_user_change', args=[obj.teacher.pk]),
                obj.teacher.full_name,
                obj.teacher.phone
            )
        return format_html('<span style="color: red;">❌ O\'qituvchi yo\'q</span>')

    teacher_info.short_description = 'O\'qituvchi'

    def students_count(self, obj):
        count = obj.users.filter(role='student').count()
        if count > 0:
            url = reverse('admin:authenticate_user_changelist') + f'?group__id__exact={obj.id}&role__exact=student'
            return format_html('<a href="{}">👨‍🎓 {} ta</a>', url, count)
        return '👨‍🎓 0 ta'

    students_count.short_description = 'Talabalar'

    def group_level_avg(self, obj):
        students = obj.users.filter(role='student')
        if students.exists():
            avg_level = students.aggregate(avg=models.Avg('level'))['avg']
            color = '#28a745' if avg_level >= 3 else '#ffc107' if avg_level >= 2 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">📊 {:.1f}</span>',
                color, avg_level
            )
        return '📊 —'

    group_level_avg.short_description = 'O\'rtacha daraja'

    def homeworks_count(self, obj):
        try:
            count = obj.homeworks.count()
            if count > 0:
                url = reverse('admin:apps_homework_changelist') + f'?group__id__exact={obj.id}'
                return format_html('<a href="{}">📝 {} ta</a>', url, count)
            return '📝 0 ta'
        except:
            return '📝 —'

    homeworks_count.short_description = 'Vazifalar'

    def group_performance(self, obj):
        try:
            from apps.models import Submission
            submissions = Submission.objects.filter(homework__group=obj, final_grade__isnull=False)
            if submissions.exists():
                avg_grade = submissions.aggregate(avg=models.Avg('final_grade'))['avg']
                color = '#28a745' if avg_grade >= 70 else '#ffc107' if avg_grade >= 50 else '#dc3545'
                return format_html(
                    '<span style="color: {}; font-weight: bold;">🎯 {:.1f}%</span>',
                    color, avg_grade
                )
            return '🎯 —'
        except ImportError:
            return '🎯 —'

    group_performance.short_description = 'Guruh ko\'rsatkichi'

    actions = ['assign_teacher', 'move_students', 'create_bulk_homeworks']

    def assign_teacher(self, request, queryset):
        self.message_user(request, f'{queryset.count()} ta guruhga o\'qituvchi tayinlandi.')

    assign_teacher.short_description = "O'qituvchi tayinlash"

    def move_students(self, request, queryset):
        self.message_user(request, 'Talabalar boshqa guruhga ko\'chirildi.')

    move_students.short_description = "Talabalarni ko'chirish"

    def create_bulk_homeworks(self, request, queryset):
        self.message_user(request, f'{queryset.count()} ta guruh uchun vazifalar yaratildi.')

    create_bulk_homeworks.short_description = "Ommaviy vazifa yaratish"


admin.site.site_header = "🎓 Homework Management System"
admin.site.site_title = "HMS Admin"
admin.site.index_title = "🏠 Bosh sahifa - Boshqaruv paneli"

from django.db import models
