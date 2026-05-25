from rest_framework import serializers

from .models import Assignment, Course, Enrollment, Submission


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for course data with computed fields."""

    title = serializers.CharField(max_length=200, min_length=3)
    description = serializers.CharField(max_length=5000, min_length=10)
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher', 'teacher_name',
            'category', 'max_students',
            'enrollment_count', 'is_full',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']

    def get_enrollment_count(self, obj: Course) -> int:
        return obj.enrollments.count()


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollment data with nested course info."""

    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'status', 'enrolled_at']
        read_only_fields = ['id', 'enrolled_at']


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for assignment data with computed fields."""

    course_title = serializers.CharField(source='course.title', read_only=True)
    submission_count = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'course', 'course_title', 'title', 'description',
            'due_date', 'max_points', 'submission_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'course', 'created_at', 'updated_at']

    def get_submission_count(self, obj: Assignment) -> int:
        # Use annotated value from queryset if available, fallback to query
        return getattr(obj, '_submission_count', obj.submissions.count())


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for submission data with related names."""

    student_name = serializers.CharField(source='student.username', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_name',
            'content', 'file', 'file_url', 'status', 'grade', 'feedback',
            'submitted_at', 'graded_at',
        ]
        read_only_fields = [
            'id', 'assignment', 'student', 'status',
            'submitted_at', 'graded_at',
        ]

    def get_file_url(self, obj: Submission) -> str | None:
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class GradeSubmissionSerializer(serializers.Serializer):
    """Standalone serializer for the grading action."""

    grade = serializers.IntegerField(min_value=0)
    feedback = serializers.CharField(required=False, allow_blank=True, default='')
