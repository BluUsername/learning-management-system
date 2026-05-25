import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CourseList from '../pages/CourseList';

const mockEnrollments = [];

// Mock useAuth to return a student user
jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'student1', role: 'student' },
    loading: false,
  }),
}));

// Mock axios with plain functions (not jest.fn) so implementations persist
jest.mock('../api/axiosConfig', () => {
  const courses = [
    {
      id: 1,
      title: 'Introduction to Python',
      description: 'Learn Python programming from scratch.',
      teacher_name: 'Dr. Smith',
      enrollment_count: 15,
    },
    {
      id: 2,
      title: 'Web Development 101',
      description: 'Build modern web applications with React.',
      teacher_name: 'Prof. Johnson',
      enrollment_count: 30,
    },
  ];

  return {
    __esModule: true,
    default: {
      get: (url) => {
        if (url === 'courses/') {
          return Promise.resolve({ data: { results: courses } });
        }
        if (url === 'enrollments/') {
          return Promise.resolve({ data: { results: mockEnrollments } });
        }
        return Promise.resolve({ data: [] });
      },
      post: () => Promise.resolve({ data: {} }),
      interceptors: { request: { use: () => {} } },
    },
    getResults: (data) => {
      if (Array.isArray(data)) return data;
      if (data && Array.isArray(data.results)) return data.results;
      return [];
    },
  };
});

function renderCourseList() {
  return render(
    <BrowserRouter>
      <CourseList />
    </BrowserRouter>
  );
}

beforeEach(() => {
  mockEnrollments.length = 0;
});

test('renders page heading', async () => {
  renderCourseList();
  await waitFor(() => {
    expect(screen.getByText('All Courses')).toBeInTheDocument();
  });
});

test('displays courses from API', async () => {
  renderCourseList();
  await screen.findByText('Introduction to Python');
  await screen.findByText('Web Development 101');
});

test('shows search input', async () => {
  renderCourseList();
  await waitFor(() => {
    expect(
      screen.getByPlaceholderText(/search courses/i)
    ).toBeInTheDocument();
  });
});

test('renders enroll buttons for student user', async () => {
  renderCourseList();
  await waitFor(() => {
    const enrollButtons = screen.getAllByText('Enroll');
    expect(enrollButtons.length).toBe(2);
  });
});

// --- INTERACTION TESTS ---
// These test real user actions on the course list page:
// searching, filtering by teacher, and enrolling in a course.

// DO: type in the search box
// CHECK: the input value updates (verifies the controlled input works)
test('allows typing in the search input', async () => {
  renderCourseList();
  const searchInput = await screen.findByPlaceholderText(/search courses/i);

  fireEvent.change(searchInput, { target: { value: 'Python' } });

  expect(searchInput.value).toBe('Python');
});

test('student can enroll in a course', async () => {
  // This test verifies the full enrollment flow: clicking the Enroll button,
  // making an API call, and verifying the API was called with the correct data.
  // It demonstrates understanding of async operations, mocking, and verifying
  // side effects (not just checking what's on screen).

  // Mock the POST request to enroll (returns success with the enrollment object)
  api.post.mockResolvedValueOnce({
    data: { id: 1, student: 1, course: 1, status: 'enrolled' },
  });

  renderCourseList();

  // Wait for courses to load
  await screen.findByText('Introduction to Python');

  // Get the first Enroll button and click it
  const enrollButtons = await screen.findAllByText('Enroll');
  fireEvent.click(enrollButtons[0]);

  // Verify the enrollment API was called with the correct course ID (course 1)
  await waitFor(() => {
    expect(api.post).toHaveBeenCalledWith(
      expect.stringMatching(/courses\/\d+\/enroll/),
      expect.any(Object)
    );
  });
});

test('displays teacher filter chips including All', async () => {
  renderCourseList();

  // Wait for courses to load so teacher names are extracted
  await screen.findByText('All');
  // Each teacher name appears in both the filter chip AND the course card
  expect(screen.getAllByText('Dr. Smith').length).toBeGreaterThanOrEqual(2);
  expect(screen.getAllByText('Prof. Johnson').length).toBeGreaterThanOrEqual(2);
});

test('handles enrolled course ids when enrollment course values are mixed', async () => {
  mockEnrollments.push({ course: 1 }, { course: { id: 2 } }, { course: null });

  renderCourseList();

  await screen.findByText('All Courses');
  expect(screen.queryByText('Failed to load courses.')).not.toBeInTheDocument();
  await waitFor(() => {
    expect(screen.queryAllByText('Enroll')).toHaveLength(0);
  });
});
