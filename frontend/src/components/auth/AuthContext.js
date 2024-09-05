import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const initialAuthToken = localStorage.getItem('authToken');
  const initialuser_id = localStorage.getItem('user_id');

  const [authToken, setAuthToken] = useState(initialAuthToken);
  const [user_id, setuser_id] = useState(initialuser_id);

  const login = (token, user_id) => {
    localStorage.setItem('authToken', token);
    localStorage.setItem('user_id', user_id);
    setAuthToken(token);
    setuser_id(user_id);
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user_id');
    setAuthToken(null);
    setuser_id(null);
  };

  const isAuthenticated = () => {
    return authToken !== null;
  };

  return (
    <AuthContext.Provider value={{ authToken, user_id, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
