# LearnHub — Learning Management System

A full-stack Learning Management System built with **Django**, **Django REST Framework**, **React 19**, and **Material UI**. The platform supports three user roles — **Students**, **Teachers**, and **Admins** — each with tailored dashboards and functionality.

**Live Demo:** [https://thelearnhub.netlify.app](https://thelearnhub.netlify.app)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Front-End Wireframes & Screenshots](#front-end-wireframes--screenshots)
- [How It Works](#how-it-works)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Lighthouse Scores](#lighthouse-scores)
- [Code Validation](#code-validation)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Technologies & Libraries](#technologies--libraries)

---

## Features

### Student
- Browse all available courses with search, filter by teacher, and sort options
- Enroll and unenroll from courses
- View a personal dashboard showing enrolled courses with sorting (Recent / A–Z)
- Submit assignments with text content, file uploads, or both
- Track submission status and view grades with teacher feedback

### Teacher
- Create new courses with a title and description
- Edit and delete their own courses
- View a dashboard with course and student enrollment stats
- Create assignments with due dates and point values
- Grade student submissions with scores and written feedback
- Download student-uploaded files for review

### Admin
- Create, edit, and delete any course
- View platform-wide statistics (total users, courses, enrollments)
- Manage all users — change roles or delete accounts via a dedicated User Management page

### Chat & AI Assistant
- Real-time chat interface with conversation history
- Rule-based chatbot that responds to questions about courses, enrolments, profile, leaderboard, and more
- Personalised responses using real user data (e.g. enrolled courses, created courses)
- Designed with a single-function swap point for future AI integration

### General
- User registration with role selection (Student or Teacher)
- Secure token-based authentication (DRF TokenAuthentication)
- Fully responsive design — mobile, tablet, and desktop
- Role-based access control enforced on both frontend and backend
- Dark/light theme toggle with localStorage persistence
- Functional settings page with toggleable notification and appearance preferences
- Notification bell with real-time badge count
- Editable user profile with avatar and bio
- Leaderboard with top courses and teachers
- Achievements & badges system with backend-driven progress tracking (10 unlockable badges)
- Searchable Help/FAQ page with accordion categories
- About page with mission, values, and platform statistics

---

## Tech Stack

| Layer       | Technology                                |
|-------------|-------------------------------------------|
| Backend     | Python 3, Django 6, Django REST Framework |
| Frontend    | JavaScript, React 19, Material UI 7       |
| Database    | PostgreSQL (production) / SQLite (local)  |
| Auth        | Token Authentication (DRF)                |
| Testing     | Django TestCase, Jest, React Testing Library |
| HTTP Client | Axios                                     |
| Routing     | React Router v6                           |
| Deployment  | Heroku (backend), Netlify (frontend)      |

---

## Project Structure

```
LearningManagementSystem/
├── README.md
├── docs/
│   ├── API.md                       # Full API endpoint documentation
│   └── wireframes/                  # Front-end wireframes and screenshots
│
├── requirements.txt                 # Python dependencies
├── manage.py                        # Django management script
├── Procfile                         # Heroku process configuration
├── Dockerfile                       # Container image for backend
├── docker-compose.yml               # Local Postgres + backend + frontend stack
│
├── lms_project/
│   ├── settings.py                  # Django configuration
│   ├── urls.py                      # Root URL routing
│   └── wsgi.py                      # WSGI entry point
├── accounts/
│   ├── models.py                    # Custom User model with roles
│   ├── serializers.py               # User/Auth serializers
│   ├── views.py                     # Auth & user management views
│   ├── permissions.py               # IsAdmin permission class
│   ├── urls.py                      # Auth & user URL routes
│   └── tests.py                     # Auth API tests (12 tests)
├── courses/
│   ├── models.py                    # Course, Enrollment, Assignment & Submission models
│   ├── serializers.py               # Course/Enrollment/Assignment/Submission serializers
│   ├── views.py                     # Course CRUD, enrollment, assignment & grading views
│   ├── permissions.py               # Role-based permission classes
│   ├── urls.py                      # Course & assignment URL routes
│   └── tests.py                     # Course, assignment & submission API tests (30 tests)
├── achievements/
│   ├── models.py                    # AchievementDefinition & UserAchievement models
│   ├── services.py                  # Achievement evaluation engine & check registry
│   ├── serializers.py               # Achievement serializers
│   ├── views.py                     # Achievement list, earned & check views
│   ├── urls.py                      # Achievement URL routes
│   └── tests.py                     # Achievement API tests (10 tests)
├── chat/
│   ├── models.py                    # ChatConversation & ChatMessage models
│   ├── serializers.py               # Chat serializers
│   ├── views.py                     # Chat API views + chatbot logic
│   ├── urls.py                      # Chat URL routes
│   └── migrations/                  # Chat database migrations
│
└── frontend/
    ├── package.json                 # Node dependencies
    ├── netlify.toml                 # Netlify deployment config
    └── src/
        ├── App.js                   # Root component with routing & theme
        ├── index.css                # Global styles
        ├── api/
        │   └── axiosConfig.js       # Axios instance with auth interceptor
        ├── contexts/
        │   ├── AuthContext.js        # Global authentication state
        │   └── ThemeContext.js       # Dark/light theme provider
        ├── components/
        │   ├── Navbar.js            # Responsive navigation with drawer
        │   ├── ProtectedRoute.js    # Route guard with role checking
        │   └── CourseCard.js        # Reusable course display card
        ├── pages/ (16 pages)
        │   ├── Login.js             # Split-screen login form
        │   ├── Register.js          # Registration with role selector
        │   ├── CourseList.js        # Browse courses with search & filters
        │   ├── CourseDetail.js      # Single course view with assignments section
        │   ├── AssignmentDetail.js  # Assignment view with submission & grading
        │   ├── StudentDashboard.js  # Student enrolled courses & stats
        │   ├── TeacherDashboard.js  # Teacher course management & stats
        │   ├── AdminDashboard.js    # Platform overview & management
        │   ├── UserManagement.js    # Admin user role & account management
        │   ├── Profile.js           # Editable user profile with avatar
        │   ├── Leaderboard.js       # Top courses & teachers ranking
        │   ├── About.js             # Mission, values & platform stats
        │   ├── Achievements.js      # Badges & gamification system (API-driven)
        │   ├── HelpFAQ.js           # Searchable FAQ & contact form
        │   ├── Settings.js          # Theme, notifications & preferences
        │   └── Chat.js             # AI chat assistant interface
        └── __tests__/               # React component & interaction tests
```

---

## Front-End Wireframes & Screenshots

### Figma Wireframes

The complete set of design mockups lives in Figma — **[LearnHub — Design Mockups](https://www.figma.com/design/4JoA5G16ce9jKcG9rOouWA/LearnHub-%E2%80%94-Design-Mockups)**.

The file contains 16 dark-theme mockups grouped into 4 sections that mirror the platform's role-based access model:

- **01 · Public** — Login, Register, About, Help & FAQ
- **02 · Student** — Student Dashboard, Course List, Course Detail, Assignment Detail
- **03 · Teacher / Admin** — Teacher Dashboard, Admin Dashboard, User Management, Leaderboard
- **04 · Cross-cutting** — Profile, Settings, Achievements, Chat Assistant

Each mockup uses the same brand palette as the live site (dark navy `#0a0e1a` backgrounds, blue→purple gradient CTAs `#1565c0 → #7b1fa2`) and includes annotation callouts at the bottom describing the page's API contract, permission rules, and role-aware behaviour.

### Production Screenshots

The screenshots below capture the same pages as rendered in the deployed application. Each demonstrates the responsive layout, consistent colour palette, and role-based UI tailored to the user type.

### Login Page
Split-screen layout with an Unsplash hero image on the left featuring the LearnHub brand and tagline. The right panel contains username and password fields, a gradient "Sign in" button, and a link to the registration page.

![Login](docs/wireframes/login.png)

### Registration Page
Similar split-screen layout with a different hero image. The right panel includes fields for username, email, password, confirm password, and a role selector (Student or Teacher). Client-side validation checks that passwords match before submitting.

![Register](docs/wireframes/register.png)

### Student Dashboard
Hero banner with welcome message and stats badges (Courses Enrolled, Active Learner). A grid of course cards with Unsplash header images showing the student's enrolled courses. Sort controls for Recent or A–Z ordering with a "Browse Courses" button.

![Student Dashboard](docs/wireframes/student-dashboard.png)

### Teacher Dashboard
Hero banner with course and student stats. A "Create Course" button opens a dialog with title and description fields. Course cards display with Edit and Delete action buttons.

![Teacher Dashboard](docs/wireframes/teacher-dashboard.png)

### Admin Dashboard
Hero banner with platform overview stats (Total Users, Total Courses, Total Enrollments). Course grid with full CRUD management actions. Links to User Management and course creation.

![Admin Dashboard](docs/wireframes/admin-dashboard.png)

### Course List Page
Hero banner with search bar, teacher filter chips, and sort controls (Recent / A–Z). Responsive grid of course cards with rotating Unsplash header images, teacher badges, and enrollment counts.

![Course List](docs/wireframes/course-list.png)

### Course Detail Page
Hero image banner with the course title overlaid. Full course information including teacher name, creation date, enrollment count, and description. Action buttons vary by user role (Enroll, Edit, Delete).

![Course Detail](docs/wireframes/course-detail.png)

### User Management Page (Admin)
Data table listing all platform users. Columns include Username, Email, Role (editable dropdown), Date Joined, and a Delete button. Admins cannot modify or delete their own account for safety.

![User Management](docs/wireframes/user-management.png)

### About / Our Mission
Marketing-style page with hero banner, mission statement, feature cards (Learn Together, Grow Your Skills, Build Community), how-it-works steps, values section, platform stats, and a call-to-action.

![About](docs/wireframes/about.png)

### Leaderboard
Gamified ranking page showing Most Popular Courses (with gold, silver, and bronze medals) and Top Teachers, aggregated from real enrollment data.

![Leaderboard](docs/wireframes/leaderboard.png)

### Achievements
Badge and achievement system with 10 unlockable achievements. Progress bar tracks overall completion. Unlocked achievements display with coloured cards, while locked achievements appear in greyscale.

![Achievements](docs/wireframes/achievements.png)

### Profile
Editable user profile with avatar (generated from initials), stats sidebar showing account age and role, form fields for display name and bio, and a read-only account information section.

![Profile](docs/wireframes/profile.png)

### Settings
Functional settings page with toggleable preferences for appearance (dark/light mode), notification settings (email, push, in-app), and account management options. All toggles persist to localStorage with toast feedback.

![Settings](docs/wireframes/settings.png)

### Help / FAQ
Searchable accordion FAQ with categorised questions covering Getting Started, Courses, and Account topics. Includes a contact/support form at the bottom.

![Help & FAQ](docs/wireframes/help-faq.png)

---

## How It Works

### Architecture Overview

The application follows a **client-server architecture** with a clear separation between the frontend and backend:

```
┌─────────────────┐         HTTP/JSON          ┌──────────────────┐
│   React App     │ ◄──────────────────────►   │   Django API     │
│   (Netlify)     │     Token Auth Header       │   (Heroku)       │
│   Port 3000     │                             │   Port 8000      │
└─────────────────┘                             └──────────────────┘
        │                                               │
        ▼                                               ▼
   localStorage                                   PostgreSQL
   (token, theme,                                 (Users, Courses,
    settings)                                   Enrollments, Chat,
                                              Assignments, Achievements)
```

1. **React Frontend** sends HTTP requests to the Django API via Axios
2. **Django Backend** processes requests, enforces permissions, and interacts with the database
3. **Token Authentication** secures the API — the frontend stores the token in `localStorage` and attaches it to every request via an Axios interceptor

### Authentication Flow

1. User submits credentials on the Login or Register page
2. Django validates and returns a **Token** + user data
3. React stores the token in `localStorage` and the user object in `AuthContext`
4. All subsequent API requests include the token in the `Authorization: Token <key>` header
5. On page refresh, the app calls `/api/auth/me/` to rehydrate the user from the stored token

### Role-Based Access Control

**Backend:** Custom DRF permission classes (`IsAdmin`, `IsTeacherOrAdmin`, `IsCourseOwnerOrAdmin`, `IsStudent`, `IsEnrolledOrCourseStaff`, `IsAssignmentCourseOwnerOrAdmin`) enforce access rules at the API level. Even if the frontend is bypassed, the backend rejects unauthorised requests.

**Frontend:** The `ProtectedRoute` component checks the user's role before rendering a page. The `Navbar` dynamically shows different navigation links based on the logged-in user's role.

### Data Models

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│     User     │       │    Course    │       │  Enrollment  │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ username     │       │ title        │       │ student (FK) │
│ email        │       │ description  │       │ course  (FK) │
│ role         │──────►│ teacher (FK) │◄──────│ enrolled_at  │
│ display_name │       │ max_students │       └──────────────┘
│ bio          │       │ category     │        unique_together
│ avatar_url   │       │ is_active    │
└──────────────┘       │ created_at   │
        │              └──────┬───────┘
        │                     │
        │              ┌──────▼───────┐       ┌──────────────┐
        │              │  Assignment  │       │  Submission  │
        │              ├──────────────┤       ├──────────────┤
        │              │ course (FK)  │       │ assignment   │
        │              │ title        │──────►│ student (FK) │
        │              │ description  │       │ content      │
        │              │ due_date     │       │ file         │
        │              │ max_points   │       │ grade        │
        │              └──────────────┘       │ feedback     │
        │                                     │ status       │
        │                                     └──────────────┘
        │                                      unique_together
        │
        ├──────────────────────────────────────────────┐
        │                                              │
        ▼                                              ▼
┌──────────────────┐       ┌──────────────┐   ┌───────────────────────┐
│ ChatConversation │       │  ChatMessage  │   │ AchievementDefinition │
├──────────────────┤       ├──────────────┤   ├───────────────────────┤
│ user (FK)        │──────►│ conversation │   │ key (unique)          │
│ title            │       │ role         │   │ name                  │
│ created_at       │       │ content      │   │ description           │
│ updated_at       │       │ timestamp    │   │ icon, color           │
└──────────────────┘       └──────────────┘   │ category              │
                                              └───────────┬───────────┘
                                                          │
                                              ┌───────────▼───────────┐
                                              │   UserAchievement     │
                                              ├───────────────────────┤
                                              │ user (FK)             │
                                              │ achievement (FK)      │
                                              │ earned_at             │
                                              └───────────────────────┘
                                               unique_together
```

- **User** — extends Django's `AbstractUser` with a `role` field (student, teacher, or admin), plus profile fields (display_name, bio, avatar_url)
- **Course** — has a title, description, category, capacity limit, and a foreign key to the teacher who created it. Supports soft delete via `is_active`
- **Enrollment** — a join table linking students to courses (unique_together constraint prevents duplicate enrollments)
- **Assignment** — belongs to a course with a title, description, due date, and max points
- **Submission** — a student's work for an assignment, supporting text content and/or file uploads. Includes grade, feedback, and status tracking (unique_together on assignment + student)
- **AchievementDefinition** — defines a badge with a key, name, description, icon, color, and category (general, student, or teacher)
- **UserAchievement** — tracks which users have earned which achievements (unique_together prevents duplicates)
- **ChatConversation** — groups chat messages per user session
- **ChatMessage** — stores individual messages with a `role` field (user or assistant)

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+
- Git

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/BluUsername/learning-management-system.git
cd learning-management-system

# Create and activate virtual environment
python -m venv venv

# Windows
source venv/Scripts/activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create a superuser (admin account)
python manage.py createsuperuser
```

### Frontend Setup

```bash
# From the project root
cd frontend

# Install dependencies
npm install
```

---

## Running the Application

You need **two terminal windows** — one for the backend and one for the frontend.

### Terminal 1 — Backend (Django)

```bash
# From the project root
source venv/Scripts/activate  # or source venv/bin/activate on macOS/Linux
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

### Terminal 2 — Frontend (React)

```bash
cd frontend
npm start
```

The app will open at `http://localhost:3000`.

### Quick Start

1. Start both servers as described above
2. Open `http://localhost:3000` in your browser
3. Register a new account (choose Student or Teacher role)
4. Log in and explore your role-specific dashboard
5. To access the admin dashboard, log in with the superuser account you created and change its role to "admin" via the Django admin panel at `http://localhost:8000/admin/`

### Docker (Optional)

To run the full stack (Postgres + backend + frontend) in containers:

```bash
# 1. Copy the environment template and fill in your own secrets
cp .env.example .env
# Edit .env and set POSTGRES_PASSWORD and SECRET_KEY to strong random values.
#
# POSTGRES_PASSWORD constraint: docker-compose embeds it directly into the
# DATABASE_URL connection string, so use only URL-safe characters.
# A hex string is always safe:
#   openssl rand -hex 32
# If your password contains a literal $, escape it as $$ in .env so that
# docker-compose does not expand it as a variable reference.

# 2. Start all services
docker-compose up --build
```

The `.env` file is git-ignored so your local secrets never get committed. `docker-compose` will fail fast with a clear message if `POSTGRES_PASSWORD` or `SECRET_KEY` is missing.

---

## Running Tests

### Backend Tests (Django)

```bash
# From the project root
source venv/Scripts/activate
python manage.py test --verbosity=2
```

**52 tests** across 3 test modules:

| Module | Tests | What's Covered |
|--------|-------|----------------|
| `accounts` | 12 | Registration (valid, password mismatch, duplicate username), login (valid/invalid credentials), current user endpoint, unauthenticated access, admin user management permissions |
| `courses` | 30 | Course CRUD with role-based permissions, student enrollment/unenrollment, duplicate enrollment prevention, assignment creation and listing, submission with text/file uploads, grading with max-points validation, teacher-scoped submission access |
| `achievements` | 10 | Achievement definition listing, achievement checking and awarding, duplicate prevention, role-based badge isolation, earned achievements endpoint |

### Frontend Tests (React)

```bash
cd frontend
npm test
```

**102 tests** across 20 test suites — every page and component is tested:

| Test Suite | Tests | What's Covered |
|------------|-------|----------------|
| `CourseCard` | 8 | Renders course details, truncates descriptions, enroll button callback |
| `CourseDetail` | 5 | Course data rendering, enroll/unenroll API calls, assignments section, error handling |
| `AssignmentDetail` | 7 | Assignment details, student submission form, file upload button, FormData POST, teacher grading table, download button, submitted state |
| `CourseList` | 5 | Loading state, renders courses from API, search filtering |
| `Login` | 5 | Form rendering, failed login error, successful API call with credentials |
| `Register` | 6 | Form rendering, role selector, password mismatch, API error, registration |
| `Navbar` | 5 | Logged-out vs logged-in states, role-specific navigation links |
| `ProtectedRoute` | 3 | Redirects when unauthenticated, renders when authenticated |
| `AuthContext` | 6 | Token persistence, login/logout, API error handling |
| `StudentDashboard` | 5 | Welcome message, course count, enrolled courses, empty state, sort |
| `TeacherDashboard` | 7 | Welcome message, stats, course cards, create dialog, form submission |
| `AdminDashboard` | 4 | Platform stats (users/courses/enrollments), admin buttons |
| `UserManagement` | 5 | User table, emails, column headers, user count |
| `Profile` | 5 | Username, full name, role display, save changes via API |
| `Settings` | 6 | Theme toggle, settings sections, localStorage persistence |
| `Achievements` | 5 | API-driven badge display, achievement check trigger, earned/locked state rendering |
| `Leaderboard` | 4 | Course ranking, teacher ranking, section headings |
| `Chat` | 4 | New conversation, sidebar, empty state, create API call |
| `HelpFAQ` | 5 | Categories, questions, accordion expand, question count |
| `About` | 6 | Hero section, mission, values, how it works, CTA |

### Test Philosophy

Tests are written using **React Testing Library** which encourages testing components the way users interact with them — querying by role, placeholder text, and visible content rather than implementation details. This approach:

- Ensures tests remain valid even if internal implementation changes
- Catches real user-facing bugs (broken forms, missing error messages)
- Uses `fireEvent` and `waitFor` to simulate realistic user interactions
- Mocks API calls with `jest.fn()` to test components in isolation

**Total: 154 tests (52 backend + 102 frontend)**

---

## Lighthouse Scores

The deployed application achieves excellent Lighthouse scores:

| Category | Score |
|----------|-------|
| Accessibility | 100 |
| Best Practices | 100 |
| SEO | 100 |
| Performance | 75 |

> **Note on Performance:** The Performance score is affected by external dependencies outside the application's control — third-party image CDN (Unsplash), Google Fonts, and Heroku cold-start latency. Optimisations applied include non-render-blocking font loading (`display=optional`), `fetchpriority="high"` on hero images, preconnect hints, and Netlify asset caching headers.

---

## Code Validation

The application has been validated against industry-standard tools:

| Validator | Result |
|-----------|--------|
| [W3C HTML Validator](https://validator.w3.org/) | **0 errors** — only informational warnings about React's self-closing tag syntax |
| [Jigsaw CSS Validator](https://jigsaw.w3.org/css-validator/) | **0 errors** — only warnings for Material UI's vendor-prefixed properties (`-webkit-font-smoothing`) |
| ESLint (React) | 0 warnings — built-in Create React App linting |
| flake8 (Python PEP 8) | **0 errors** — all Django code passes PEP 8 style checks (`--max-line-length=120`, migrations excluded) |
| Python (Django check) | `python manage.py check` passes with no issues |

---

## API Reference

Full API documentation is available in [docs/API.md](docs/API.md).

### Quick Reference

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/auth/register/` | Register a new user | Public |
| POST | `/api/auth/login/` | Log in and receive token | Public |
| POST | `/api/auth/logout/` | Log out (delete token) | Authenticated |
| GET | `/api/auth/me/` | Get current user info | Authenticated |
| PATCH | `/api/auth/me/` | Update profile | Authenticated |
| GET | `/api/courses/` | List all courses | Authenticated |
| POST | `/api/courses/` | Create a course | Teacher, Admin |
| GET | `/api/courses/:id/` | Get course details | Authenticated |
| PUT | `/api/courses/:id/` | Update a course | Course owner, Admin |
| DELETE | `/api/courses/:id/` | Delete a course | Course owner, Admin |
| POST | `/api/courses/:id/enroll/` | Enroll in a course | Student |
| DELETE | `/api/courses/:id/unenroll/` | Unenroll from a course | Student |
| GET | `/api/enrollments/` | List my enrollments | Student |
| GET | `/api/courses/:course_id/assignments/` | List course assignments | Enrolled, Staff |
| POST | `/api/courses/:course_id/assignments/` | Create assignment | Course owner, Admin |
| GET | `/api/courses/:course_id/assignments/:assignment_id/` | Get assignment details | Enrolled, Staff |
| POST | `/api/assignments/:id/submit/` | Submit assignment (text/file) | Student (enrolled) |
| GET | `/api/assignments/:id/submissions/` | List submissions | Teacher (own course), Student (own), Admin |
| GET | `/api/submissions/:id/` | Get submission details | Owner, Course teacher, Admin |
| PATCH | `/api/submissions/:id/grade/` | Grade a submission | Course teacher, Admin |
| GET | `/api/my-submissions/` | List my submissions | Student |
| GET | `/api/achievements/` | List all achievement definitions | Authenticated |
| GET | `/api/achievements/me/` | List my earned achievements | Authenticated |
| POST | `/api/achievements/check/` | Check & award new achievements | Authenticated |
| GET | `/api/users/` | List all users | Admin |
| PATCH | `/api/users/:id/` | Update a user's role | Admin |
| DELETE | `/api/users/:id/` | Delete a user | Admin |
| GET | `/api/conversations/` | List chat conversations | Authenticated |
| POST | `/api/conversations/` | Create a conversation | Authenticated |
| GET | `/api/conversations/:id/` | Get conversation detail | Owner |
| GET | `/api/conversations/:id/messages/` | List messages | Owner |
| POST | `/api/conversations/:id/messages/` | Send message (returns bot reply) | Owner |

---

## Deployment

The application is deployed and live:

| Service | Platform | Live URL |
|---------|----------|----------|
| **Frontend** | Netlify | [https://thelearnhub.netlify.app](https://thelearnhub.netlify.app) |
| **Backend API** | Heroku | [https://lms-backend-tom-25f123572e9b.herokuapp.com/api/](https://lms-backend-tom-25f123572e9b.herokuapp.com/api/) |

> **Note:** The backend can be run locally following the Setup & Installation section. Frontend is fully deployed on Netlify.

### Deployment Stack

- **Backend (Heroku):** Gunicorn WSGI server, WhiteNoise for static files, PostgreSQL database (via Heroku Postgres), `dj-database-url` for database configuration, environment variables for secrets and CORS origins
- **Frontend (Netlify):** Production React build served via Netlify CDN, `netlify.toml` handles SPA routing redirects and cache headers, `REACT_APP_API_URL` environment variable points to the Heroku backend

---

## Technologies & Libraries

### Backend
| Package | Purpose |
|---------|---------|
| [Django 6](https://www.djangoproject.com/) | Web framework |
| [Django REST Framework](https://www.django-rest-framework.org/) | REST API toolkit |
| [django-cors-headers](https://github.com/adamchainz/django-cors-headers) | Cross-origin request handling |
| [Gunicorn](https://gunicorn.org/) | Production WSGI server |
| [WhiteNoise](http://whitenoise.evans.io/) | Static file serving |
| [dj-database-url](https://github.com/jazzband/dj-database-url) | Database URL configuration |

### Frontend
| Package | Purpose |
|---------|---------|
| [React 19](https://react.dev/) | UI library |
| [Material UI 7](https://mui.com/) | Component library & theming |
| [Axios](https://axios-http.com/) | HTTP client with interceptors |
| [React Router v6](https://reactrouter.com/) | Client-side routing |
| [Jest](https://jestjs.io/) | Test runner |
| [React Testing Library](https://testing-library.com/) | Component testing |
