import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Navbar from '../components/Navbar';
import { AuthProvider } from '../contexts/AuthContext';

jest.mock('../api/axiosConfig', () => ({
  get: jest.fn(),
  post: jest.fn(),
  interceptors: { request: { use: jest.fn() } },
}));

// Mock matchMedia for useMediaQuery in jsdom environment
window.matchMedia = window.matchMedia || function matchMedia() {
  return {
    matches: false,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  };
};

beforeEach(() => {
  localStorage.clear();
});

const theme = createTheme();

function renderNavbar() {
  return render(
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <AuthProvider>
          <Navbar />
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}

test('renders LearnHub title', () => {
  renderNavbar();
  expect(screen.getByText('LearnHub')).toBeInTheDocument();
});

test('shows login and register links when logged out', async () => {
  renderNavbar();
  const loginLink = await screen.findByRole('link', { name: /login/i });
  expect(loginLink).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /register/i })).toBeInTheDocument();
});

test('does not show logout when logged out', async () => {
  renderNavbar();
  await screen.findByRole('link', { name: /login/i });
  expect(screen.queryByRole('button', { name: /logout/i })).not.toBeInTheDocument();
});
