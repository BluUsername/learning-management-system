import { useState, useEffect } from 'react';
import useDocumentTitle from '../hooks/useDocumentTitle';
import {
  Container, Typography, Grid, Box, CircularProgress, Alert, Button, Paper,
  TextField, Avatar, Chip, Divider, Snackbar,
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  CalendarMonth as CalendarIcon,
  School as SchoolIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  AutoStories as AutoStoriesIcon,
  EmojiEvents as TrophyIcon,
  WorkspacePremium as BadgeIcon,
  MenuBook as MenuBookIcon,
} from '@mui/icons-material';
import api, { getResults } from '../api/axiosConfig';
import { useAuth } from '../contexts/AuthContext';

function Profile() {
  const { user, fetchUser } = useAuth();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [bio, setBio] = useState('');
  const [saving, setSaving] = useState(false);
  const [alert, setAlert] = useState({ open: false, severity: 'success', message: '' });
  const [stats, setStats] = useState({ courses: 0 });
  const [statsLoading, setStatsLoading] = useState(true);

  useDocumentTitle('Profile');

  // Populate form fields from user data
  useEffect(() => {
    if (user) {
      setFirstName(user.first_name || '');
      setLastName(user.last_name || '');
      setBio(user.bio || '');
    }
  }, [user]);

  // Fetch stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        if (user?.role === 'student') {
          const res = await api.get('enrollments/');
          setStats({ courses: getResults(res.data).length });
        } else if (user?.role === 'teacher') {
          const res = await api.get('courses/');
          const allCourses = getResults(res.data);
          const myCourses = allCourses.filter(
            (c) => c.teacher === user.id || c.teacher_name === user.username
          );
          setStats({ courses: myCourses.length });
        }
      } catch {
        // Stats are non-critical, fail silently
      } finally {
        setStatsLoading(false);
      }
    };
    if (user) fetchStats();
  }, [user]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.patch('auth/me/', {
        first_name: firstName,
        last_name: lastName,
        bio,
      });
      await fetchUser();
      setAlert({ open: true, severity: 'success', message: 'Profile updated successfully!' });
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to update profile. Please try again.';
      setAlert({ open: true, severity: 'error', message: detail });
    } finally {
      setSaving(false);
    }
  };

  if (!user) {
    return (
      <Box display="flex" justifyContent="center" mt={8}>
        <CircularProgress />
      </Box>
    );
  }

  const initials = [user.first_name, user.last_name]
    .filter(Boolean)
    .map((n) => n[0].toUpperCase())
    .join('') || user.username[0].toUpperCase();

  const memberSince = new Date(user.date_joined).toLocaleDateString('en-GB', {
    year: 'numeric', month: 'long', day: 'numeric',
  });

  const roleLabel = user.role
    ? user.role.charAt(0).toUpperCase() + user.role.slice(1)
    : 'User';

  return (
    <Container sx={{ mt: 4, mb: 6 }}>
      {/* Hero Banner */}
      <Paper elevation={0} sx={{
        p: 4, mb: 4, borderRadius: 3, position: 'relative', overflow: 'hidden',
        backgroundImage: `
          linear-gradient(135deg, rgba(26, 35, 126, 0.92) 0%, rgba(21, 101, 192, 0.85) 60%, rgba(123, 31, 162, 0.9) 100%),
          url('https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1400&q=80')
        `,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        color: 'white',
      }}>
        <Box sx={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap' }}>
          {/* Avatar */}
          <Avatar sx={{
            width: 96, height: 96,
            fontSize: '2.2rem', fontWeight: 700,
            background: 'linear-gradient(135deg, #f57c00, #ff9800)',
            border: '4px solid rgba(255,255,255,0.3)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
          }}>
            {initials}
          </Avatar>

          <Box sx={{ flex: 1, minWidth: 200 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.5 }}>
              <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
                {user.first_name && user.last_name
                  ? `${user.first_name} ${user.last_name}`
                  : user.username}
              </Typography>
            </Box>
            <Typography variant="subtitle1" component="p" sx={{ opacity: 0.85, mb: 1.5 }}>
              @{user.username}
            </Typography>

            {/* Info Chips */}
            <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
              <Chip
                icon={<SchoolIcon sx={{ color: 'white !important', fontSize: 18 }} />}
                label={roleLabel}
                sx={{
                  backgroundColor: 'rgba(255,255,255,0.15)',
                  color: 'white',
                  fontWeight: 600,
                  backdropFilter: 'blur(8px)',
                }}
              />
              <Chip
                icon={<CalendarIcon sx={{ color: 'white !important', fontSize: 18 }} />}
                label={`Member since ${memberSince}`}
                sx={{
                  backgroundColor: 'rgba(255,255,255,0.15)',
                  color: 'white',
                  fontWeight: 600,
                  backdropFilter: 'blur(8px)',
                }}
              />
              <Chip
                icon={<EmailIcon sx={{ color: 'white !important', fontSize: 18 }} />}
                label={user.email}
                sx={{
                  backgroundColor: 'rgba(255,255,255,0.15)',
                  color: 'white',
                  fontWeight: 600,
                  backdropFilter: 'blur(8px)',
                }}
              />
            </Box>
          </Box>
        </Box>
      </Paper>

      <Grid container spacing={3}>
        {/* Stats Section */}
        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Course Stat Card */}
            <Paper elevation={0} sx={{
              p: 3, borderRadius: 3, textAlign: 'center',
              background: 'linear-gradient(135deg, rgba(21, 101, 192, 0.12) 0%, rgba(123, 31, 162, 0.12) 100%)',
              border: '1px solid rgba(66, 165, 245, 0.15)',
            }}>
              <Box sx={{
                width: 56, height: 56, borderRadius: '50%', mx: 'auto', mb: 1.5,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'linear-gradient(135deg, #1565c0, #7b1fa2)',
              }}>
                <AutoStoriesIcon sx={{ color: 'white', fontSize: 28 }} />
              </Box>
              {statsLoading ? (
                <CircularProgress size={28} />
              ) : (
                <Typography variant="h3" component="p" sx={{ fontWeight: 700, color: '#42a5f5' }}>
                  {stats.courses}
                </Typography>
              )}
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, mt: 0.5 }}>
                {user.role === 'student' ? 'Courses Enrolled' : 'Courses Created'}
              </Typography>
            </Paper>

            {/* Role Badge Card */}
            <Paper elevation={0} sx={{
              p: 3, borderRadius: 3, textAlign: 'center',
              background: 'linear-gradient(135deg, rgba(245, 124, 0, 0.12) 0%, rgba(255, 152, 0, 0.08) 100%)',
              border: '1px solid rgba(245, 124, 0, 0.15)',
            }}>
              <Box sx={{
                width: 56, height: 56, borderRadius: '50%', mx: 'auto', mb: 1.5,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'linear-gradient(135deg, #f57c00, #ff9800)',
              }}>
                <BadgeIcon sx={{ color: 'white', fontSize: 28 }} />
              </Box>
              <Typography variant="h6" component="p" sx={{ fontWeight: 700, color: '#ff9800' }}>
                {roleLabel}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, mt: 0.5 }}>
                Account Role
              </Typography>
            </Paper>

            {/* Achievement Card */}
            <Paper elevation={0} sx={{
              p: 3, borderRadius: 3, textAlign: 'center',
              background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.12) 0%, rgba(129, 199, 132, 0.08) 100%)',
              border: '1px solid rgba(76, 175, 80, 0.15)',
            }}>
              <Box sx={{
                width: 56, height: 56, borderRadius: '50%', mx: 'auto', mb: 1.5,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'linear-gradient(135deg, #388e3c, #66bb6a)',
              }}>
                <TrophyIcon sx={{ color: 'white', fontSize: 28 }} />
              </Box>
              <Typography variant="h6" component="p" sx={{ fontWeight: 700, color: '#66bb6a' }}>
                Active
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, mt: 0.5 }}>
                Account Status
              </Typography>
            </Paper>
          </Box>
        </Grid>

        {/* Edit Profile Section */}
        <Grid item xs={12} md={8}>
          <Paper elevation={0} sx={{
            p: 4, borderRadius: 3,
            background: 'linear-gradient(135deg, rgba(21, 101, 192, 0.08) 0%, rgba(123, 31, 162, 0.06) 100%)',
            border: '1px solid rgba(66, 165, 245, 0.12)',
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
              <EditIcon sx={{ color: '#42a5f5' }} />
              <Typography variant="h5" component="h2" sx={{ fontWeight: 700 }}>
                Edit Profile
              </Typography>
            </Box>
            <Divider sx={{ mb: 3, borderColor: 'rgba(66, 165, 245, 0.12)' }} />

            <Grid container spacing={2.5}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="First Name"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  fullWidth
                  InputProps={{
                    startAdornment: (
                      <PersonIcon sx={{ mr: 1, color: 'rgba(255,255,255,0.7)', fontSize: 20 }} />
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255,255,255,0.04)',
                      borderRadius: 2,
                      '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' },
                      '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.25)' },
                      '&.Mui-focused fieldset': { borderColor: '#42a5f5' },
                    },
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Last Name"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  fullWidth
                  InputProps={{
                    startAdornment: (
                      <PersonIcon sx={{ mr: 1, color: 'rgba(255,255,255,0.7)', fontSize: 20 }} />
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255,255,255,0.04)',
                      borderRadius: 2,
                      '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' },
                      '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.25)' },
                      '&.Mui-focused fieldset': { borderColor: '#42a5f5' },
                    },
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Bio"
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  fullWidth
                  multiline
                  rows={4}
                  placeholder="Tell us a bit about yourself, your interests, and what you're learning..."
                  InputProps={{
                    startAdornment: (
                      <MenuBookIcon sx={{ mr: 1, color: 'rgba(255,255,255,0.7)', fontSize: 20, alignSelf: 'flex-start', mt: 1 }} />
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255,255,255,0.04)',
                      borderRadius: 2,
                      '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' },
                      '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.25)' },
                      '&.Mui-focused fieldset': { borderColor: '#42a5f5' },
                    },
                    '& .MuiInputBase-input::placeholder': { color: 'rgba(255,255,255,0.65)' },
                  }}
                />
              </Grid>
            </Grid>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
              <Button
                variant="contained"
                startIcon={saving ? <CircularProgress size={18} color="inherit" /> : <SaveIcon />}
                onClick={handleSave}
                disabled={saving}
                sx={{
                  px: 4, py: 1.2, borderRadius: 2, fontWeight: 600,
                  background: 'linear-gradient(135deg, #f57c00, #ff9800)',
                  '&:hover': { background: 'linear-gradient(135deg, #e65100, #f57c00)' },
                  '&:disabled': { opacity: 0.7 },
                }}
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </Box>
          </Paper>

          {/* Account Info Card */}
          <Paper elevation={0} sx={{
            p: 4, mt: 3, borderRadius: 3,
            background: 'linear-gradient(135deg, rgba(245, 124, 0, 0.06) 0%, rgba(255, 152, 0, 0.04) 100%)',
            border: '1px solid rgba(245, 124, 0, 0.12)',
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
              <PersonIcon sx={{ color: '#ff9800' }} />
              <Typography variant="h5" component="h2" sx={{ fontWeight: 700 }}>
                Account Information
              </Typography>
            </Box>
            <Divider sx={{ mb: 3, borderColor: 'rgba(245, 124, 0, 0.12)' }} />

            <Grid container spacing={2}>
              {[
                { label: 'Username', value: user.username, icon: <PersonIcon sx={{ fontSize: 20 }} /> },
                { label: 'Email', value: user.email, icon: <EmailIcon sx={{ fontSize: 20 }} /> },
                { label: 'Role', value: roleLabel, icon: <SchoolIcon sx={{ fontSize: 20 }} /> },
                { label: 'Member Since', value: memberSince, icon: <CalendarIcon sx={{ fontSize: 20 }} /> },
              ].map((item) => (
                <Grid item xs={12} sm={6} key={item.label}>
                  <Box sx={{
                    p: 2, borderRadius: 2,
                    backgroundColor: 'rgba(255,255,255,0.04)',
                    border: '1px solid rgba(255,255,255,0.06)',
                  }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Box sx={{ color: 'rgba(255,255,255,0.7)' }}>{item.icon}</Box>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        {item.label}
                      </Typography>
                    </Box>
                    <Typography variant="body1" sx={{ fontWeight: 500, pl: 3.5 }}>
                      {item.value}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* Success / Error Snackbar */}
      <Snackbar
        open={alert.open}
        autoHideDuration={4000}
        onClose={() => setAlert({ ...alert, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setAlert({ ...alert, open: false })}
          severity={alert.severity}
          variant="filled"
          sx={{ width: '100%', borderRadius: 2 }}
        >
          {alert.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default Profile;
