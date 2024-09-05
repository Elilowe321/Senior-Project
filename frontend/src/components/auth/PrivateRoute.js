import React from 'react';
import { Navigate, Outlet, useParams } from 'react-router-dom';
import { useAuth } from './AuthContext';

const PrivateRoute = ({ element }) => {
  const { isAuthenticated } = useAuth();

  const user_id = localStorage.getItem('user_id');
  const authToken = localStorage.getItem('authToken');

  const isUserAuthenticated = () => {
    return isAuthenticated(user_id, authToken) && user_id === user_id;
  };

  return isUserAuthenticated() ? <Outlet /> : <Navigate to="/signin" />;
};

export default PrivateRoute;