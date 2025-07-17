from rest_framework.serializers import ModelSerializer

from apps.models import Submission, Homework, Grade, SubmissionFile


class GradeModelSerializer(ModelSerializer):
    class Meta:
        model = Grade
        fields = ('final_task_completeness', 'final_code_quality', 'final_correctness', 'teacher_total',
                  'task_completeness_feedback', 'code_quality_feedback', 'correctness_feedback', 'submission',
                  'ai_task_completeness', 'ai_code_quality', 'ai_correctness', 'ai_total', 'modified_by_teacher',
                  'created_at', 'updated_at')
        read_only_fields = ('submission', 'ai_task_completeness', 'ai_code_quality', 'ai_correctness',
                            'ai_total', 'modified_by_teacher', 'created_at', 'updated_at')


class SubmissionFileModelSerializer(ModelSerializer):
    class Meta:
        model = SubmissionFile
        fields = ('file_name', 'content', 'line_count', 'submission')
        read_only_fields = ('id', 'line_count')

    def create(self, validated_data):
        uploaded_file = validated_data.get('content')

        line_count = 0
        if uploaded_file:
            uploaded_file.open()
            content_bytes = uploaded_file.read()
            content_text = content_bytes.decode('utf-8')
            line_count = len(content_text.strip().splitlines())
            uploaded_file.seek(0)

        validated_data['line_count'] = line_count
        return super().create(validated_data)


class SubmissionModelSerialize(ModelSerializer):
    files = SubmissionFileModelSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('student', 'homework', 'student', 'submitted_at', 'ai_grade', 'final_grade', 'ai_feedback', 'files',
                  'created_at')
        read_only_fields = ('student', 'created_at')

    def create(self, validated_data):
        files_data = validated_data.pop('files')
        submission = Submission.objects.create(**validated_data)
        for file_data in files_data:
            SubmissionFile.objects.create(submission=submission, **file_data)
        return submission


class HomeworkModelSerializer(ModelSerializer):
    class Meta:
        model = Homework
        fields = ('id', 'title', 'description', 'points', 'start_date', 'deadline', 'line_limit', 'teacher', 'group',
                  'file_extensions', 'ai_grading_prompt', 'created_at')
        read_only_fields = ('id', 'created_at', 'teacher')
