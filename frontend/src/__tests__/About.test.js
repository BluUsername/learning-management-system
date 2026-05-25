import { screen } from '@testing-library/react';
import About from '../pages/About';
import { renderWithProviders } from '../test-utils';

// About is a static marketing page — no API calls needed.
// We just check that all sections render correctly.

function renderPage() {
  return renderWithProviders(<About />);
}

// CHECK: hero section renders with brand name
test('renders About page with hero section', () => {
  renderPage();
  expect(screen.getAllByText(/LearnHub/).length).toBeGreaterThan(0);
});

// CHECK: mission section exists
test('renders Our Mission section', () => {
  renderPage();
  expect(screen.getByText('Our Mission')).toBeInTheDocument();
});

// CHECK: mission cards are present
test('renders mission feature cards', () => {
  renderPage();
  expect(screen.getByText('Learn Together')).toBeInTheDocument();
  expect(screen.getByText('Grow Your Skills')).toBeInTheDocument();
  expect(screen.getByText('Build Community')).toBeInTheDocument();
});

// CHECK: how it works section
test('renders How It Works section with steps', () => {
  renderPage();
  expect(screen.getByText('How It Works')).toBeInTheDocument();
});

// CHECK: values section
test('renders Our Values section', () => {
  renderPage();
  expect(screen.getByText('Our Values')).toBeInTheDocument();
});

// CHECK: call-to-action button exists
test('renders call-to-action button', () => {
  renderPage();
  expect(screen.getByText(/Get Started/i)).toBeInTheDocument();
});
