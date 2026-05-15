from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from accounts.models import User
from .models import Assignment, Course, Enrollment, Submission


class CourseListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher', email='teacher@example.com',
            password='testpass123', role='teacher',
        )
        self.student = User.objects.create_user(
            username='student', email='student@example.com',
            password='testpass123', role='student',
        )
        self.teacher_token = Token.objects.create(user=self.teacher)
        self.student_token = Token.objects.create(user=self.student)

        self.course = Course.objects.create(
            title='Test Course', description='A test course', teacher=self.teacher,
        )

    def test_list_courses_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Paginated response: results are in response.data['results']
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_list_courses_unauthenticated(self):
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher', email='teacher@example.com',
            password='testpass123', role='teacher',
        )
        self.student = User.objects.create_user(
            username='student', email='student@example.com',
            password='testpass123', role='student',
        )
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='testpass123', role='admin',
        )
        self.teacher_token = Token.objects.create(user=self.teacher)
        self.student_token = Token.objects.create(user=self.student)
        self.admin_token = Token.objects.create(user=self.admin)

    def test_create_course_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
        response = self.client.post('/api/courses/', {
            'title': 'New Course',
            'description': 'A comprehensive course on the subject matter',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['teacher'], self.teacher.id)

    def test_create_course_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.post('/api/courses/', {
            'title': 'Admin Course',
            'description': 'A course created by the admin user',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_course_student_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post('/api/courses/', {
            'title': 'Student Course',
            'description': 'This course should not be created',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CourseUpdateDeleteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher1 = User.objects.create_user(
            username='teacher1', email='t1@example.com',
            password='testpass123', role='teacher',
        )
        self.teacher2 = User.objects.create_user(
            username='teacher2', email='t2@example.com',
            password='testpass123', role='teacher',
        )
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='testpass123', role='admin',
        )
        self.t1_token = Token.objects.create(user=self.teacher1)
        self.t2_token = Token.objects.create(user=self.teacher2)
        self.admin_token = Token.objects.create(user=self.admin)

        self.course = Course.objects.create(
            title='Course 1', description='A test course description', teacher=self.teacher1,
        )

    def test_update_course_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.t1_token.key}')
        response = self.client.put(f'/api/courses/{self.course.id}/', {
            'title': 'Updated Title',
            'description': 'An updated course description',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_update_course_non_owner_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.t2_token.key}')
        response = self.client.put(f'/api/courses/{self.course.id}/', {
            'title': 'Hacked Title',
            'description': 'This should not be allowed',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_course_admin(self):
        """Admin can soft-delete a course (is_active set to False)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.delete(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Soft delete: course still exists but is inactive
        self.course.refresh_from_db()
        self.assertFalse(self.course.is_active)


class EnrollmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher', email='teacher@example.com',
            password='testpass123', role='teacher',
        )
        self.student = User.objects.create_user(
            username='student', email='student@example.com',
            password='testpass123', role='student',
        )
        self.teacher_token = Token.objects.create(user=self.teacher)
        self.student_token = Token.objects.create(user=self.student)

        self.course = Course.objects.create(
            title='Test Course', description='A test course description', teacher=self.teacher,
        )

    def test_enroll_student(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(f'/api/courses/{self.course.id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Enrollment.objects.filter(student=self.student, course=self.course).exists()
        )

    def test_enroll_duplicate(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(f'/api/courses/{self.course.id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unenroll_student(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.delete(f'/api/courses/{self.course.id}/unenroll/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Enrollment.objects.filter(student=self.student, course=self.course).exists()
        )

    def test_enroll_teacher_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
        response = self.client.post(f'/api/courses/{self.course.id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_enrollments(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/api/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Paginated response: results are in response.data['results']
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_enroll_nonexistent_course_returns_404(self):
        """A student trying to enroll in a course that doesn't exist must
        get a 404 — not a 500 — so the API stays a well-behaved REST citizen.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post('/api/courses/999999/enroll/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_enroll_full_course_returns_400(self):
        """When a course hits its max_students capacity, further enrolment
        attempts must be rejected with a clear 400 instead of being silently
        accepted (which would break the capacity contract).
        """
        full_course = Course.objects.create(
            title='Tiny Cohort', description='Capacity of one.',
            teacher=self.teacher, max_students=1,
        )
        first_student = User.objects.create_user(
            username='first', email='first@example.com',
            password='testpass123', role='student',
        )
        Enrollment.objects.create(student=first_student, course=full_course)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(f'/api/courses/{full_course.id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('full', response.data['detail'].lower())

    def test_unenroll_when_not_enrolled_returns_404(self):
        """Trying to leave a course the student was never in must 404 —
        the resource (their enrolment) genuinely doesn't exist.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.delete(f'/api/courses/{self.course.id}/unenroll/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AssignmentTests(TestCase):
    """Tests for assignment CRUD operations."""

    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher', email='teacher@example.com',
            password='testpass123', role='teacher',
        )
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='testpass123', role='admin',
        )
        self.student = User.objects.create_user(
            username='student', email='student@example.com',
            password='testpass123', role='student',
        )
        self.teacher_token = Token.objects.create(user=self.teacher)
        self.admin_token = Token.objects.create(user=self.admin)
        self.student_token = Token.objects.create(user=self.student)

        self.course = Course.objects.create(
            title='Test Course', description='A test course', teacher=self.teacher,
        )
        Enrollment.objects.create(student=self.student, course=self.course)

        self.assignment = Assignment.objects.create(
            course=self.course, title='Homework 1',
            description='Complete the exercises',
            due_date=timezone.now() + timezone.timedelta(days=7),
            max_points=100,
        )

    def test_list_assignments_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
        response = self.client.get(f'/api/courses/{self.course.id}/assignments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_list_assignments_enrolled_student(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get(f'/api/courses/{self.course.id}/assignments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_assignments_unenrolled_student_forbidden(self):
        other_student = User.objects.create_user(
            username='other', email='other@example.com',
            password='testpass123', role='student',
        )
        other_token = Token.objects.create(user=other_student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        response = self.client.get(f'/api/courses/{self.course.id}/assignments/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_assignment_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
        response = self.client.post(f'/api/courses/{self.course.id}/assignments/', {
            'title': 'Homework 2',
            'description': 'Write an essay on the topic',
            'due_date': '2026-12-31T23:59:00Z',
            'max_points': 50,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['course'], self.course.id)

    def test_create_assignment_student_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(f'/api/courses/{self.course.id}/assignments/', {
            'title': 'Sneaky Assignment',
            'description': 'Students should not create these',
            'due_date': '2026-12-31T23:59:00Z',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_assignment_admin_missing_course_returns_404(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.post('/api/courses/999999/assignments/', {
            'title': 'Admin Assignment',
            'description': 'Should fail for missing course',
            'due_date': '2026-12-31T23:59:00Z',
            'max_points': 50,
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_assignment_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
        response = self.client.delete(
            f'/api/courses/{self.course.id}/assignments/{self.assignment.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Assignment.objects.filter(pk=self.assignment.id).exists())


class SubmissionTests(TestCase):
    """Tests for submission and grading operations."""

    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher', email='teacher@example.com',
            password='testpass123', role='teacher',
        )
        self.student = User.objects.create_user(
            username='student', email='student@example.com',
            password='testpass123', role='student',
        )
        self.teacher_token = Token.objects.create(user=self.teacher)
        self.student_token = Token.objects.create(user=self.student)

        self.course = Course.objects.create(
            title='Test Course', description='A test course', teacher=self.teacher,
        )
        Enrollment.objects.create(student=self.student, course=self.course)
        self.assignment = Assignment.objects.create(
            course=self.course, title='Homework 1',
            description='Complete the exercises',
            due_date=timezone.now() + timezone.timedelta(days=7),
            max_points=100,
        )

    def test_submit_assignment(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(f'/api/assignments/{self.assignment.id}/submit/', {
            'content': 'Here is my completed homework.',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'submitted')

    def test_submit_duplicate_rejected(self):
        Submission.objects.create(
            assignment=self.assignment, student=self.student,
            content='First attempt',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(f'/api/assignments/{self.assignment.id}/submit/', {
            'content': 'Second attempt',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_not_enrolled_forbidden(self):
        other_student = User.objects.create_user(
            username='other', email='other@example.com',
            password='testpass123', role='student',
        )
        other_token = Token.objects.create(user=other_student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        response = self.client.post(f'/api/assignments/{self.assignment.id}/submit/', {
            'content': 'I am not enrolled.',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_submission(self):
        submission = Submission.objects.create(
            assignment=self.assignment, student=self.student,
            content='My homework',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
        response = self.client.patch(f'/api/submissions/{submission.id}/grade/', {
            'grade': 85,
            'feedback': 'Good work!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['grade'], 85)
        self.assertEqual(response.data['status'], 'graded')
        self.assertIsNotNone(response.data['graded_at'])

    def test_grade_exceeds_max_rejected(self):
        submission = Submission.objects.create(
            assignment=self.assignment, student=self.student,
            content='My homework',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
        response = self.client.patch(f'/api/submissions/{submission.id}/grade/', {
            'grade': 150,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_cannot_grade(self):
        submission = Submission.objects.create(
            assignment=self.assignment, student=self.student,
            content='My homework',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.patch(f'/api/submissions/{submission.id}/grade/', {
            'grade': 100,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_submissions_teacher_sees_all(self):
        Submission.objects.create(
            assignment=self.assignment, student=self.student,
            content='My homework',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
        response = self.client.get(f'/api/assignments/{self.assignment.id}/submissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_my_submissions(self):
        Submission.objects.create(
            assignment=self.assignment, student=self.student,
            content='My homework',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/api/my-submissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    @override_settings(MEDIA_ROOT='/tmp/lms_test_media/')
    def test_submit_with_file(self):
        """Student can submit an assignment with a file upload."""
        test_file = SimpleUploadedFile(
            'homework.txt', b'File content here', content_type='text/plain',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(
            f'/api/assignments/{self.assignment.id}/submit/',
            {'content': 'See attached file.', 'file': test_file},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file_url', response.data)
        self.assertIsNotNone(response.data['file_url'])

    @override_settings(MEDIA_ROOT='/tmp/lms_test_media/')
    def test_submit_file_only(self):
        """Student can submit with only a file (no text content)."""
        test_file = SimpleUploadedFile(
            'essay.pdf', b'%PDF-1.4 fake pdf content', content_type='application/pdf',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(
            f'/api/assignments/{self.assignment.id}/submit/',
            {'file': test_file},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_submit_empty_rejected(self):
        """Submitting with no content and no file should be rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(
            f'/api/assignments/{self.assignment.id}/submit/',
            {},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_null_content_rejected_not_500(self):
        """JSON {"content": null} must return 400, not crash with 500."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.post(
            f'/api/assignments/{self.assignment.id}/submit/',
            {'content': None},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_grade_submission_not_found_returns_404(self):
        """Grading a submission that doesn't exist must 404, not 500."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
        response = self.client.patch(
            '/api/submissions/999999/grade/',
            {'grade': 50, 'feedback': 'n/a'},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_cannot_grade_other_teachers_submission(self):
        """Security: teacher A must not be able to grade a submission that
        belongs to teacher B's course. This is the cross-teacher boundary
        — a much subtler attack surface than student-vs-teacher.
        """
        other_teacher = User.objects.create_user(
            username='other_teacher', email='ot@example.com',
            password='testpass123', role='teacher',
        )
        other_token = Token.objects.create(user=other_teacher)
        submission = Submission.objects.create(
            assignment=self.assignment, student=self.student,
            content='Work on teacher A\'s course',
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        response = self.client.patch(
            f'/api/submissions/{submission.id}/grade/',
            {'grade': 0, 'feedback': 'malicious grade attempt'},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And the actual submission must NOT have been altered.
        submission.refresh_from_db()
        self.assertIsNone(submission.grade)
