import { useState } from 'react';
import useDocumentTitle from '../hooks/useDocumentTitle';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Typography, TextField, Button, Alert, Box, Link, Chip,
} from '@mui/material';
import {
  Login as LoginIcon, School as SchoolIcon,
  ArrowDownward as ArrowDownIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  useDocumentTitle('Sign In');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const user = await login(username, password);
      switch (user.role) {
        case 'student': navigate('/student'); break;
        case 'teacher': navigate('/teacher'); break;
        case 'admin': navigate('/admin'); break;
        default: navigate('/courses');
      }
    } catch (err) {
      const data = err.response?.data;
      // Custom error envelope: { error: { status_code, message, details } }
      const message =
        data?.error?.details?.non_field_errors?.[0]
        || data?.error?.message
        || data?.non_field_errors?.[0]
        || data?.detail
        || 'Login failed. Please try again.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{
      display: 'flex',
      minHeight: '100vh',
      margin: '-64px 0 0 0',
      paddingTop: 0,
    }}>
      {/* Left Panel - Branding with Hero Image */}
      <Box sx={{
        flex: '1 1 50%',
        backgroundImage: `
          linear-gradient(160deg, rgba(10, 14, 39, 0.85) 0%, rgba(26, 31, 78, 0.75) 40%, rgba(45, 27, 105, 0.8) 70%, rgba(26, 35, 126, 0.85) 100%),
          url('https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80')
        `,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        display: { xs: 'none', md: 'flex' },
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'flex-start',
        p: 8,
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Decorative circles */}
        <Box sx={{
          position: 'absolute', width: 300, height: 300, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(123, 31, 162, 0.3) 0%, transparent 70%)',
          bottom: -50, left: -50,
        }} />
        <Box sx={{
          position: 'absolute', width: 200, height: 200, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(21, 101, 192, 0.25) 0%, transparent 70%)',
          top: 80, right: 60,
        }} />
        <Box sx={{
          position: 'absolute', width: 150, height: 150, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(245, 124, 0, 0.2) 0%, transparent 70%)',
          bottom: 150, right: 120,
        }} />

        {/* Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 6 }}>
          <SchoolIcon sx={{ color: '#fff', fontSize: 32 }} />
          <Typography variant="h5" component="p" sx={{ color: '#fff', fontWeight: 700, letterSpacing: '0.5px' }}>
            LearnHub
          </Typography>
        </Box>

        {/* Tagline */}
        <Typography variant="h2" sx={{
          color: '#fff',
          fontWeight: 800,
          lineHeight: 1.15,
          mb: 3,
          fontSize: { md: '2.8rem', lg: '3.5rem' },
        }}>
          Learn without{' '}
          <Box component="span" sx={{
            background: 'linear-gradient(135deg, #42a5f5, #ab47bc, #ffb74d)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            limits.
          </Box>
        </Typography>

        <Typography variant="h6" component="p" sx={{ color: 'rgba(255,255,255,0.75)', fontWeight: 400, mb: 5, maxWidth: 380 }}>
          A platform built for students, teachers, and the curious.
        </Typography>

        {/* Role chips */}
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          {['Student', 'Teacher', 'Admin'].map((role) => (
            <Chip
              key={role}
              label={role}
              sx={{
                backgroundColor: 'rgba(255,255,255,0.1)',
                color: 'rgba(255,255,255,0.8)',
                border: '1px solid rgba(255,255,255,0.15)',
                fontWeight: 500,
                backdropFilter: 'blur(8px)',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.2)',
                },
              }}
            />
          ))}
        </Box>

        {/* Scroll indicator */}
        <Box sx={{
          position: 'absolute', bottom: 40, left: '50%', transform: 'translateX(-50%)',
          display: 'flex', flexDirection: 'column', alignItems: 'center',
        }}>
          <Box sx={{
            width: 36, height: 36, borderRadius: '50%',
            border: '2px solid rgba(255,255,255,0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            animation: 'bounce 2s infinite',
            '@keyframes bounce': {
              '0%, 100%': { transform: 'translateY(0)' },
              '50%': { transform: 'translateY(8px)' },
            },
          }}>
            <ArrowDownIcon sx={{ color: 'rgba(255,255,255,0.7)', fontSize: 20 }} />
          </Box>
        </Box>
      </Box>

      {/* Right Panel - Login Form */}
      <Box sx={{
        flex: '1 1 50%',
        background: 'linear-gradient(160deg, #121228 0%, #1a1a2e 50%, #16213e 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        p: { xs: 4, md: 8 },
      }}>
        <Box sx={{ width: '100%', maxWidth: 400 }}>
          <Typography variant="h4" component="h1" sx={{ color: '#fff', fontWeight: 700, mb: 1 }}>
            Welcome back
          </Typography>
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.75)', mb: 4 }}>
            Sign in to your account
          </Typography>

          {error && <Alert severity="error" role="alert" sx={{ mb: 3 }}>{error}</Alert>}

          <Box component="form" onSubmit={handleSubmit} noValidate>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.75)', mb: 0.5 }}>
              Username
            </Typography>
            <TextField
              placeholder="Enter your username"
              fullWidth
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              autoFocus
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255,255,255,0.06)',
                  borderRadius: 2,
                  color: '#fff',
                  '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' },
                  '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.25)' },
                  '&.Mui-focused fieldset': { borderColor: '#7b1fa2' },
                },
                '& .MuiInputBase-input::placeholder': { color: 'rgba(255,255,255,0.65)' },
              }}
            />
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.75)', mb: 0.5 }}>
              Password
            </Typography>
            <TextField
              placeholder="Enter your password"
              type="password"
              fullWidth
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              sx={{
                mb: 4,
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255,255,255,0.06)',
                  borderRadius: 2,
                  color: '#fff',
                  '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' },
                  '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.25)' },
                  '&.Mui-focused fieldset': { borderColor: '#7b1fa2' },
                },
                '& .MuiInputBase-input::placeholder': { color: 'rgba(255,255,255,0.65)' },
              }}
            />
            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              disabled={loading}
              startIcon={<LoginIcon />}
              sx={{
                py: 1.5,
                mb: 3,
                fontWeight: 600,
                fontSize: '1rem',
                background: 'linear-gradient(135deg, #1565c0 0%, #7b1fa2 100%)',
                borderRadius: 2,
                '&:hover': {
                  background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
                  boxShadow: '0 4px 20px rgba(123, 31, 162, 0.4)',
                },
              }}
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </Button>
          </Box>

          <Typography variant="body2" align="center" sx={{ color: 'rgba(255,255,255,0.75)' }}>
            Don't have an account?{' '}
            <Link
              component={RouterLink}
              to="/register"
              sx={{
                color: '#ab47bc',
                fontWeight: 600,
                textDecoration: 'none',
                '&:hover': { color: '#ce93d8', textDecoration: 'underline' },
              }}
            >
              Register
            </Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}

export default Login;
