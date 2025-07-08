import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Create axios instance with interceptors
  const api = axios.create({
    baseURL: API_BASE_URL,
  });

  // Request interceptor to add auth token
  api.interceptors.request.use(
    (config) => {
      const token = Cookies.get('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor to handle auth errors
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        logout();
      }
      return Promise.reject(error);
    }
  );

  const login = async (username, password) => {
    try {
      const response = await api.post('/api/auth/login', { username, password });
      const { access_token } = response.data;
      
      // Store token in cookie
      Cookies.set('token', access_token, { expires: 7 });
      
      // Get user info
      const userResponse = await api.get('/api/auth/me');
      setUser(userResponse.data);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await api.post('/api/auth/register', { username, email, password });
      const { access_token } = response.data;
      
      // Store token in cookie
      Cookies.set('token', access_token, { expires: 7 });
      
      // Get user info
      const userResponse = await api.get('/api/auth/me');
      setUser(userResponse.data);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    Cookies.remove('token');
    setUser(null);
  };

  const checkAuth = async () => {
    try {
      const token = Cookies.get('token');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await api.get('/api/auth/me');
      setUser(response.data);
    } catch (error) {
      Cookies.remove('token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    api
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};