import React, { createContext, useState, useEffect, useContext } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('medvibe_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const register = async (email, password, fullName) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed. Please try again.');
      }
      localStorage.setItem('medvibe_user', JSON.stringify(data));
      setUser(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Incorrect email or password.');
      }
      localStorage.setItem('medvibe_user', JSON.stringify(data));
      setUser(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('medvibe_user');
    setUser(null);
    setError(null);
  };

  // Secure API fetch helper that attaches JWT token and intercepts 401s
  const authFetch = async (url, options = {}) => {
    const headers = options.headers || {};
    
    if (user?.access_token) {
      headers['Authorization'] = `Bearer ${user.access_token}`;
    }
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      }
    };
    
    try {
      const response = await fetch(url, config);
      
      // Auto-logout if token is expired or unauthorized
      if (response.status === 401) {
        logout();
        window.location.href = '/login';
        throw new Error('Session expired. Please log in again.');
      }
      
      return response;
    } catch (err) {
      console.error('API request error:', err);
      throw err;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, register, login, logout, authFetch }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
