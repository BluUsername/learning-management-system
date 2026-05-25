import logging

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Assignment, Course, Enrollment, Submission
from .permissions import (
    IsAssignmentCourseOwnerOrAdmin,
    IsCourseOwnerOrAdmin,
    IsEnrolledOrCourseStaff,
    IsStudent,
    IsTeacherOrAdmin,
)
from .serializers import (
    AssignmentSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    GradeSubmissionSerializer,
    SubmissionSerializer,
)

logger = logging.getLogger(__name__)


class CourseListCreateView(generics.ListCreateAPIView):
    """List all active courses or create a new one (teacher/admin only).

    GET returns paginated list of active courses with teacher info. Supports search
    by title/description/teacher, filter by teacher or category, and sort by name
    or date. Teachers and admins can POST to create a new course; the course is
    automatically assigned to the requesting user as the teacher.
    """

    queryset = Course.objects.select_related('teacher').filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields = ['teacher', 'category']
    search_fields = ['title', 'description', 'teacher__username', 'category']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def perform_create(self, serializer: CourseSerializer) -> None:
        course = serializer.save(teacher=self.request.user)
        logger.info(f"Course created: '{course.title}' by {self.request.user.username}")


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a course (owner/admin only).

    Supports GET to view course details, PATCH/PUT to edit, and DELETE to remove.
    DELETE is a soft delete: marks the course inactive rather than destroying the
    record. This preserves audit trails and allows cascade cleanup (inactive courses
    don't show in student listings or accept new enrollments, but enrollments/grades
    are preserved).
    """

    queryset = Course.objects.select_related('teacher').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsCourseOwnerOrAdmin]

    def perform_destroy(self, instance: Course) -> None:
        instance.is_active = False
        instance.save()
        logger.info(f"Course soft-deleted: '{instance.title}'")


class EnrollView(APIView):
    """Enroll the current student in a course.

    POST /courses/<id>/enroll/ enrolls the requesting user in the course if:
    1. The course exists and is active
    2. The course is not at capacity (max_students limit)
    3. The user is not already enrolled

    Returns 201 with the enrollment record, or 400/404 with error details if
    validation fails.
    """

    permission_classes = [IsStudent]

    def post(self, request: Request, pk: int) -> Response:
        try:
            course = Course.objects.get(pk=pk, is_active=True)
        except Course.DoesNotExist:
            return Response(
                {'detail': 'Course not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if course.is_full:
            return Response(
                {'detail': 'This course is full.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {'detail': 'Already enrolled in this course.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enrollment = Enrollment.objects.create(student=request.user, course=course)
        logger.info(f"Student {request.user.username} enrolled in '{course.title}'")
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )


class UnenrollView(APIView):
    """Unenroll the current student from a course."""

    permission_classes = [IsStudent]

    def delete(self, request: Request, pk: int) -> Response:
        try:
            enrollment = Enrollment.objects.get(student=request.user, course_id=pk)
        except Enrollment.DoesNotExist:
            return Response(
                {'detail': 'Not enrolled in this course.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        logger.info(f"Student {request.user.username} unenrolled from course {pk}")
        enrollment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyEnrollmentsView(generics.ListAPIView):
    """List the current student's enrollments with full course details.

    Returns paginated list of courses the user is enrolled in, with course info,
    teacher details, and enrollment metadata. Used by the student dashboard to
    show "My Courses".
    """

    serializer_class = EnrollmentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Enrollment.objects.select_related(
            'course', 'course__teacher'
        ).filter(student=self.request.user)


# ---------------------------------------------------------------------------
# Assignment views
# ---------------------------------------------------------------------------

class AssignmentListCreateView(generics.ListCreateAPIView):
    """List assignments for a course, or create one (course owner/admin only).

    GET lists all assignments for a course, including submission counts (how many
    students submitted). Students can see assignments in courses they're enrolled
    in; teachers/admins can see all assignments for their courses.

    POST creates a new assignment (teacher/admin only). The assignment is
    automatically attached to the requested course.
    """

    serializer_class = AssignmentSerializer
    permission_classes = [IsEnrolledOrCourseStaff, IsAssignmentCourseOwnerOrAdmin]

    def get_queryset(self):
        return Assignment.objects.select_related('course').annotate(
            _submission_count=Count('submissions'),
        ).filter(
            course_id=self.kwargs['course_pk'],
            course__is_active=True,
        )

    def perform_create(self, serializer: AssignmentSerializer) -> None:
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'], is_active=True)
        assignment = serializer.save(course=course)
        logger.info(
            f"Assignment created: '{assignment.title}' for "
            f"'{course.title}' by {self.request.user.username}"
        )


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an assignment (course owner/admin only).

    GET returns assignment details with submission count. PATCH/PUT edits the
    assignment (title, description, due date, point value). DELETE removes the
    assignment and cascades deletion of all student submissions.
    """

    serializer_class = AssignmentSerializer
    permission_classes = [IsEnrolledOrCourseStaff, IsAssignmentCourseOwnerOrAdmin]

    def get_queryset(self):
        return Assignment.objects.select_related('course').annotate(
            _submission_count=Count('submissions'),
        ).filter(
            course_id=self.kwargs['course_pk'],
            course__is_active=True,
        )


class SubmissionCreateView(APIView):
    """Student submits work (text and/or file upload) for an assignment.

    Enforces three business rules:
    1. Student must be enrolled in the course that owns the assignment
    2. Student can only submit once per assignment (no overwrites)
    3. Submission must include either text content or a file (not empty)

    Accepts multipart/form-data with optional 'content' (text) and 'file' (upload).
    Returns 201 with the submission record, or 400/403/404 with validation details.
    """

    permission_classes = [IsStudent]

    def post(self, request: Request, assignment_pk: int) -> Response:
        try:
            assignment = Assignment.objects.select_related('course').get(
                pk=assignment_pk, course__is_active=True,
            )
        except Assignment.DoesNotExist:
            return Response(
                {'detail': 'Assignment not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not Enrollment.objects.filter(
            student=request.user, course=assignment.course,
        ).exists():
            return Response(
                {'detail': 'You must be enrolled in this course.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if Submission.objects.filter(
            assignment=assignment, student=request.user,
        ).exists():
            return Response(
                {'detail': 'You have already submitted this assignment.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content = (request.data.get('content') or '').strip()
        uploaded_file = request.FILES.get('file')

        if not content and not uploaded_file:
            return Response(
                {'detail': 'Please provide text content or upload a file.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submission = Submission.objects.create(
            assignment=assignment,
            student=request.user,
            content=content,
            file=uploaded_file,
        )
        logger.info(
            f"Submission by {request.user.username} for "
            f"'{assignment.title}'"
            f"{' (with file)' if uploaded_file else ''}"
        )
        return Response(
            SubmissionSerializer(submission, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class SubmissionListView(generics.ListAPIView):
    """List submissions for an assignment (permission-aware filtering).

    Teachers and admins see all submissions for their assignment.
    Students see only their own submission(s). This endpoint powers both the
    teacher's grading dashboard (all submissions) and the student's submission
    history (personal only).
    """

    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Submission.objects.select_related(
            'student', 'assignment',
        ).filter(assignment_id=self.kwargs['assignment_pk'])

        # Students can only see their own submission
        if self.request.user.role == 'student':
            qs = qs.filter(student=self.request.user)
        # Teachers can only see submissions for their own courses
        elif self.request.user.role == 'teacher':
            qs = qs.filter(assignment__course__teacher=self.request.user)
        return qs


class SubmissionDetailView(generics.RetrieveAPIView):
    """View a single submission."""

    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Submission.objects.select_related('student', 'assignment')
        if self.request.user.role == 'student':
            qs = qs.filter(student=self.request.user)
        elif self.request.user.role == 'teacher':
            qs = qs.filter(assignment__course__teacher=self.request.user)
        return qs


class GradeSubmissionView(APIView):
    """Teacher or admin grades a student's submission."""

    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, pk: int) -> Response:
        if request.user.role not in ('teacher', 'admin'):
            return Response(
                {'detail': 'Only teachers and admins can grade submissions.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            submission = Submission.objects.select_related(
                'assignment__course',
            ).get(pk=pk)
        except Submission.DoesNotExist:
            return Response(
                {'detail': 'Submission not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Teachers can only grade submissions for their own courses
        course = submission.assignment.course
        if request.user.role == 'teacher' and course.teacher != request.user:
            return Response(
                {'detail': 'You can only grade submissions for your courses.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = GradeSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate grade doesn't exceed max points
        if serializer.validated_data['grade'] > submission.assignment.max_points:
            return Response(
                {'detail': f'Grade cannot exceed {submission.assignment.max_points} points.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submission.grade = serializer.validated_data['grade']
        submission.feedback = serializer.validated_data['feedback']
        submission.status = 'graded'
        submission.graded_at = timezone.now()
        submission.save()

        logger.info(
            f"Submission graded: {submission.student.username} got "
            f"{submission.grade}/{submission.assignment.max_points} "
            f"on '{submission.assignment.title}'"
        )
        return Response(
            SubmissionSerializer(submission, context={'request': request}).data,
        )


class MySubmissionsView(generics.ListAPIView):
    """List the current student's submissions across all courses."""

    serializer_class = SubmissionSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Submission.objects.select_related(
            'assignment', 'assignment__course',
        ).filter(student=self.request.user)
