// Docusaurus authentication plugin configuration
// This would typically be implemented as a Docusaurus plugin

// For client-side auth with context
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useHistory } from '@docusaurus/router';

// Create authentication context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in from localStorage/sessionStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    // In a real implementation, this would call an API
    // This is simplified for demonstration
    if (username && password) {
      const userData = { username, loginTime: new Date() };
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return { success: true, message: 'Login successful' };
    }
    return { success: false, message: 'Invalid credentials' };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value = {
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Protected route component
export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const history = useHistory();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    // Redirect to login page if not authenticated
    history.push('/login');
    return null;
  }

  return children;
};