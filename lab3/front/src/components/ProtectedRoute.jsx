import { Navigate } from 'react-router-dom';
import { tokenUtils } from '../services/authService';

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = tokenUtils.hasToken();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;

