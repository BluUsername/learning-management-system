import { useState } from 'react';
import useDocumentTitle from '../hooks/useDocumentTitle';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Typography, TextField, Button, Alert, Box, Link,
  FormControl, Select, MenuItem,
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon, School as SchoolIcon,
  Rocket as RocketIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    role: 'student',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  useDocumentTitle('Register');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password2) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const user = await register(
        formData.username, formData.email,
        formData.password, formData.password2, formData.role,
      );
      switch (user.role) {
        case 'student': navigate('/student'); break;
        case 'teacher': navigate('/teacher'); break;
        default: navigate('/courses');
      }
    } catch (err) {
      const data = err.response?.data;
      if (data?.error?.details) {
        // Custom error envelope: { error: { status_code, message, details } }
        const messages = Object.values(data.error.details).flat().join(' ');
        setError(messages);
      } else if (data?.error?.message) {
        setError(data.error.message);
      } else if (data) {
        // Fallback: plain DRF format { field: [errors] }
        const messages = Object.values(data).flat().join(' ');
        setError(messages);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const inputSx = {
    mb: 2.5,
    '& .MuiOutlinedInput-root': {
      backgroundColor: 'rgba(255,255,255,0.06)',
      borderRadius: 2,
      color: '#fff',
      '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' },
      '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.25)' },
      '&.Mui-focused fieldset': { borderColor: '#7b1fa2' },
    },
    '& .MuiInputBase-input::placeholder': { color: 'rgba(255,255,255,0.65)' },
    '& .MuiFormHelperText-root': { color: 'rgba(255,255,255,0.65)' },
  };

  return (
    <Box sx={{
      display: 'flex',
      minHeight: '100vh',
      margin: '-64px 0 0 0',
    }}>
      {/* Left Panel - Branding with Hero Image */}
      <Box sx={{
        flex: '1 1 50%',
        backgroundImage: `
          linear-gradient(160deg, rgba(10, 14, 39, 0.85) 0%, rgba(26, 31, 78, 0.75) 40%, rgba(45, 27, 105, 0.8) 70%, rgba(26, 35, 126, 0.85) 100%),
          url('https://images.unsplash.com/photo-1531545514256-b1400bc00f31?auto=format&fit=crop&w=1200&q=80')
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
          position: 'absolute', width: 350, height: 350, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(245, 124, 0, 0.2) 0%, transparent 70%)',
          top: -80, right: -80,
        }} />
        <Box sx={{
          position: 'absolute', width: 250, height: 250, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(123, 31, 162, 0.3) 0%, transparent 70%)',
          bottom: 60, left: -40,
        }} />
        <Box sx={{
          position: 'absolute', width: 180, height: 180, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(21, 101, 192, 0.25) 0%, transparent 70%)',
          top: '40%', right: 100,
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
          Start your{' '}
          <Box component="span" sx={{
            background: 'linear-gradient(135deg, #ffb74d, #f57c00, #ab47bc)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            journey.
          </Box>
        </Typography>

        <Typography variant="h6" component="p" sx={{ color: 'rgba(255,255,255,0.75)', fontWeight: 400, mb: 5, maxWidth: 380 }}>
          Join thousands of learners and educators. Create your free account today.
        </Typography>

        {/* Feature highlights */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {[
            'Access courses from any device',
            'Track your learning progress',
            'Connect with expert teachers',
          ].map((feature) => (
            <Box key={feature} sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Box sx={{
                width: 8, height: 8, borderRadius: '50%',
                background: 'linear-gradient(135deg, #42a5f5, #ab47bc)',
              }} />
              <Typography sx={{ color: 'rgba(255,255,255,0.75)', fontSize: '0.95rem' }}>
                {feature}
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>

      {/* Right Panel - Register Form */}
      <Box sx={{
        flex: '1 1 50%',
        background: 'linear-gradient(160deg, #121228 0%, #1a1a2e 50%, #16213e 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        p: { xs: 4, md: 6 },
        overflowY: 'auto',
      }}>
        <Box sx={{ width: '100%', maxWidth: 420 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
            <RocketIcon sx={{ color: '#f57c00', fontSize: 28 }} />
            <Typography variant="h4" component="h1" sx={{ color: '#fff', fontWeight: 700 }}>
              Get started
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.75)', mb: 3.5 }}>
            Create your free account
          </Typography>

          {error && <Alert severity="error" role="alert" sx={{ mb: 2.5 }}>{error}</Alert>}

          <Box component="form" onSubmit={handleSubmit} noValidate>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.75)', mb: 0.5 }}>
              Username
            </Typography>
            <TextField
              placeholder="Choose a username"
              name="username"
              fullWidth
              required
              value={formData.username}
              onChange={handleChange}
              autoComplete="username"
              autoFocus
              sx={inputSx}
            />
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.75)', mb: 0.5 }}>
              Email
            </Typography>
            <TextField
              placeholder="you@example.com"
              name="email"
              type="email"
              fullWidth
              required
              value={formData.email}
              onChange={handleChange}
              autoComplete="email"
              sx={inputSx}
            />
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.75)', mb: 0.5 }}>
              Password
            </Typography>
            <TextField
              placeholder="Minimum 8 characters"
              name="password"
              type="password"
              fullWidth
              required
              value={formData.password}
              onChange={handleChange}
              autoComplete="new-password"
              helperText="Must be at least 8 characters"
              sx={inputSx}
            />
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.75)', mb: 0.5 }}>
              Confirm Password
            </Typography>
            <TextField
              placeholder="Re-enter your password"
              name="password2"
              type="password"
              fullWidth
              required
              value={formData.password2}
              onChange={handleChange}
              autoComplete="new-password"
              sx={inputSx}
            />
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.75)', mb: 0.5 }}>
              I want to join as a...
            </Typography>
            <FormControl fullWidth sx={{ mb: 3 }}>
              <Select
                name="role"
                value={formData.role}
                onChange={handleChange}
                inputProps={{ 'aria-label': 'Select your role' }}
                sx={{
                  backgroundColor: 'rgba(255,255,255,0.06)',
                  borderRadius: 2,
                  color: '#fff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.12)' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.25)' },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#7b1fa2' },
                  '& .MuiSvgIcon-root': { color: 'rgba(255,255,255,0.75)' },
                }}
              >
                <MenuItem value="student">Student</MenuItem>
                <MenuItem value="teacher">Teacher</MenuItem>
              </Select>
            </FormControl>
            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              disabled={loading}
              startIcon={<PersonAddIcon />}
              sx={{
                py: 1.5,
                mb: 3,
                fontWeight: 600,
                fontSize: '1rem',
                background: 'linear-gradient(135deg, #f57c00 0%, #ff9800 50%, #ffb74d 100%)',
                color: '#1a1a2e',
                borderRadius: 2,
                '&:hover': {
                  background: 'linear-gradient(135deg, #e65100 0%, #f57c00 50%, #ff9800 100%)',
                  boxShadow: '0 4px 20px rgba(245, 124, 0, 0.4)',
                },
              }}
            >
              {loading ? 'Creating account...' : 'Create account'}
            </Button>
          </Box>

          <Typography variant="body2" align="center" sx={{ color: 'rgba(255,255,255,0.75)' }}>
            Already have an account?{' '}
            <Link
              component={RouterLink}
              to="/login"
              sx={{
                color: '#42a5f5',
                fontWeight: 600,
                textDecoration: 'none',
                '&:hover': { color: '#90caf9', textDecoration: 'underline' },
              }}
            >
              Sign in
            </Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}

export default Register;
