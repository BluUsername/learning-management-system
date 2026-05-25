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

// DO: look at the teacher filter chips
// CHECK: "All" chip is present plus one chip per unique teacher
// Note: teacher names appear in BOTH filter chips AND course cards,
// so we use getAllByText and check there are at least 2 matches
// (one in the chip, one in the card).
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
