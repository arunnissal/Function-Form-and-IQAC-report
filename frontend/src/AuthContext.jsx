import React, { createContext, useState, useEffect } from 'react';
import api from './api';
import { jwtDecode } from "jwt-decode";

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        // Add additional check for token expiry here if needed
        setUser(decoded);
      } catch (e) {
        localStorage.removeItem('access_token');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await api.post('auth/login/', { username: email, password });
    localStorage.setItem('access_token', response.data.access);
    const decoded = jwtDecode(response.data.access);
    setUser(decoded);
    return decoded;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
