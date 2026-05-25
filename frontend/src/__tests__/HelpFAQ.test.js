import { screen, fireEvent } from '@testing-library/react';
import HelpFAQ from '../pages/HelpFAQ';
import { renderWithProviders } from '../test-utils';

// HelpFAQ is a static page — no API calls, no auth needed.
// This is the simplest type of test: just render and check content.

// CHECK: page title renders
test('renders Help & FAQ page title', () => {
  renderWithProviders(<HelpFAQ />);
  expect(screen.getByText(/Help & FAQ/)).toBeInTheDocument();
});

// CHECK: FAQ categories are present
test('renders FAQ categories', () => {
  renderWithProviders(<HelpFAQ />);
  expect(screen.getByText('Getting Started')).toBeInTheDocument();
  expect(screen.getByText('Courses')).toBeInTheDocument();
});

// CHECK: FAQ questions are visible
test('renders FAQ questions', () => {
  renderWithProviders(<HelpFAQ />);
  expect(screen.getByText('How do I create an account?')).toBeInTheDocument();
  expect(screen.getByText(/How do I enrol in a course/)).toBeInTheDocument();
});

// CHECK: FAQ question count chip is displayed
test('shows total question count', () => {
  renderWithProviders(<HelpFAQ />);
  expect(screen.getByText(/Questions Answered/)).toBeInTheDocument();
});

// DO: click on an accordion question
// CHECK: the answer expands and is visible
test('expands accordion to show answer when clicked', () => {
  renderWithProviders(<HelpFAQ />);
  const question = screen.getByText('How do I create an account?');
  fireEvent.click(question);
  expect(screen.getByText(/Click the "Register" button/)).toBeInTheDocument();
});
