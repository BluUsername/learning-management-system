import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../api/axiosConfig';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const response = await api.get('auth/me/');
      setUser(response.data);
    } catch {
      localStorage.removeItem('token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = async (username, password) => {
    const response = await api.post('auth/login/', { username, password });
    localStorage.setItem('token', response.data.token);
    setUser(response.data.user);
    return response.data.user;
  };

  const register = async (username, email, password, password2, role) => {
    const response = await api.post('auth/register/', {
      username, email, password, password2, role,
    });
    localStorage.setItem('token', response.data.token);
    setUser(response.data.user);
    return response.data.user;
  };

  const logout = async () => {
    try {
      await api.post('auth/logout/');
    } catch {
      // Token may already be invalid
    }
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
