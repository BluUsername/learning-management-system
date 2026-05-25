import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Profile from '../pages/Profile';

jest.mock('../api/axiosConfig', () => {
  const mock = { get: jest.fn(), patch: jest.fn() };
  mock.getResults = (data) => (Array.isArray(data) ? data : data?.results ?? data);
  return { __esModule: true, default: mock, getResults: mock.getResults };
});
jest.mock('../contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

const api = require('../api/axiosConfig').default;
const { useAuth } = require('../contexts/AuthContext');

beforeEach(() => {
  jest.clearAllMocks();
  useAuth.mockReturnValue({
    user: {
      id: 1, username: 'Tom', role: 'student',
      first_name: 'Tom', last_name: 'Herman', bio: 'I love coding',
      email: 'tom@email.com', date_joined: '2026-01-15T00:00:00Z',
    },
    updateUser: jest.fn(),
  });
  // Profile fetches enrollments for stats
  api.get.mockResolvedValueOnce({ data: [{ id: 1 }, { id: 2 }] });
});

function renderProfile() {
  return render(<BrowserRouter><Profile /></BrowserRouter>);
}

// CHECK: username is displayed
test('displays username', async () => {
  renderProfile();
  expect(await screen.findByText(/@Tom/)).toBeInTheDocument();
});

// CHECK: user's name appears
test('displays user full name', async () => {
  renderProfile();
  expect(await screen.findByText(/Tom Herman/)).toBeInTheDocument();
});

// CHECK: role is shown (use getAllByText since "Student" may appear multiple times)
test('displays user role', async () => {
  renderProfile();
  await screen.findByText(/@Tom/);
  expect(screen.getAllByText(/Student/).length).toBeGreaterThan(0);
});

// CHECK: course stats load and display
test('shows course count from API', async () => {
  renderProfile();
  expect(await screen.findByText('2')).toBeInTheDocument();
});

// DO: change bio, click Save Changes
// CHECK: API is called with updated data
test('saves profile changes via API', async () => {
  api.patch.mockResolvedValueOnce({
    data: { first_name: 'Tom', last_name: 'Herman', bio: 'Updated bio' },
  });

  renderProfile();
  await screen.findByText(/@Tom/);

  // Change the bio field
  const bioField = screen.getByLabelText(/Bio/);
  fireEvent.change(bioField, { target: { value: 'Updated bio' } });

  // Click Save Changes button
  fireEvent.click(screen.getByText('Save Changes'));

  await waitFor(() => {
    expect(api.patch).toHaveBeenCalledWith('auth/me/', expect.objectContaining({
      bio: 'Updated bio',
    }));
  });
});

// --- MORE INTERACTION TESTS ---
// These test error handling and multi-field editing flows.

// DO: change bio and click Save, but API returns an error
// CHECK: error message appears on screen
test('shows error message when save fails', async () => {
  api.patch.mockRejectedValueOnce({
    response: { data: { detail: 'Failed to update profile. Please try again.' } },
  });

  // Use mockReturnValue (not mockReturnValueOnce) so the mock persists across
  // component re-renders. The component re-renders when you edit the bio field.
  useAuth.mockReturnValue({
    user: {
      id: 1, username: 'Tom', role: 'student',
      first_name: 'Tom', last_name: 'Herman', bio: 'I love coding',
      email: 'tom@email.com', date_joined: '2026-01-15T00:00:00Z',
    },
    updateUser: jest.fn(),
  });
  api.get.mockResolvedValueOnce({ data: [{ id: 1 }, { id: 2 }] });

  renderProfile();
  await screen.findByText(/@Tom/);

  // Edit the bio
  fireEvent.change(screen.getByLabelText(/Bio/), {
    target: { value: 'This will fail' },
  });

  // Click Save
  fireEvent.click(screen.getByText('Save Changes'));

  // Error feedback should appear
  expect(await screen.findByText(/failed to update profile/i)).toBeInTheDocument();
});

// DO: change first name, last name, and bio together, then save
// CHECK: API is called with ALL updated fields
test('saves all profile fields together', async () => {
  api.patch.mockResolvedValueOnce({
    data: { first_name: 'Thomas', last_name: 'Smith', bio: 'New bio text' },
  });

  useAuth.mockReturnValue({
    user: {
      id: 1, username: 'Tom', role: 'student',
      first_name: 'Tom', last_name: 'Herman', bio: 'I love coding',
      email: 'tom@email.com', date_joined: '2026-01-15T00:00:00Z',
    },
    updateUser: jest.fn(),
  });
  api.get.mockResolvedValueOnce({ data: [{ id: 1 }, { id: 2 }] });

  renderProfile();
  await screen.findByText(/@Tom/);

  // Change multiple fields
  fireEvent.change(screen.getByLabelText(/First Name/), {
    target: { value: 'Thomas' },
  });
  fireEvent.change(screen.getByLabelText(/Last Name/), {
    target: { value: 'Smith' },
  });
  fireEvent.change(screen.getByLabelText(/Bio/), {
    target: { value: 'New bio text' },
  });

  fireEvent.click(screen.getByText('Save Changes'));

  // Verify ALL fields were sent in the PATCH request
  await waitFor(() => {
    expect(api.patch).toHaveBeenCalledWith('auth/me/', {
      first_name: 'Thomas',
      last_name: 'Smith',
      bio: 'New bio text',
    });
  });
});

// CRITICAL TEST: After profile update succeeds, AuthContext must refresh
// so the UI reflects updated user data (hero banner, account info, etc).
// This test verifies the fix from PR #20 works correctly.
test('refreshes user context after successful profile update', async () => {
  const mockFetchUser = jest.fn();

  // Use mockReturnValue (not mockReturnValueOnce) so the mock persists across
  // component re-renders. The component will re-render when form fields change.
  useAuth.mockReturnValue({
    user: {
      id: 1, username: 'Tom', role: 'student',
      first_name: 'Tom', last_name: 'Herman', bio: 'Old bio',
      email: 'tom@email.com', date_joined: '2026-01-15T00:00:00Z',
    },
    fetchUser: mockFetchUser,
  });

  api.get.mockResolvedValueOnce({ data: [] }); // enrollments fetch
  api.patch.mockResolvedValueOnce({
    data: { first_name: 'Tom', last_name: 'Herman', bio: 'Updated bio' },
  });

  renderProfile();
  await screen.findByText(/@Tom/);

  // Update the bio
  fireEvent.change(screen.getByLabelText(/Bio/), {
    target: { value: 'Updated bio' },
  });

  // Save changes
  fireEvent.click(screen.getByText('Save Changes'));

  // Verify that fetchUser() was called to refresh the AuthContext
  // This ensures the UI will update with fresh user data from the server
  await waitFor(() => {
    expect(mockFetchUser).toHaveBeenCalled();
  });
});
