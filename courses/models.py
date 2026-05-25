from django.conf import settings
from django.db import models


class Course(models.Model):
    """A course created by a teacher or admin."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='taught_courses',
    )
    # null = unlimited capacity
    max_students = models.PositiveIntegerField(null=True, blank=True)
    category = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Soft delete: is_active=False hides course but preserves enrollments and grades
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title

    @property
    def is_full(self) -> bool:
        """Check if course has reached its capacity limit."""
        if self.max_students is None:
            return False
        return self.enrollments.count() >= self.max_students


class Enrollment(models.Model):
    """A student's enrollment in a course with status tracking."""

    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='enrolled',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self) -> str:
        return f"{self.student.username} enrolled in {self.course.title}"


class Assignment(models.Model):
    """An assignment created by a teacher for a specific course."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_points = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self) -> str:
        return f"{self.title} ({self.course.title})"


class Submission(models.Model):
    """A student's submission for an assignment."""

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    content = models.TextField(blank=True, default='')
    file = models.FileField(
        upload_to='submissions/%Y/%m/',
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='submitted',
    )
    grade = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, default='')
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self) -> str:
        return f"{self.student.username} - {self.assignment.title}"
