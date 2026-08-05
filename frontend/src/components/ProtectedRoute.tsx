import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import PageLoader from './Skeleton';

type Props = {
  children: React.ReactNode;
  allowedRoles?: string[];
  excludedRoles?: string[];
  redirectTo?: string;
};

const ProtectedRoute = ({ children, allowedRoles, excludedRoles, redirectTo }: Props) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <PageLoader />;
  if (!user) return <Navigate to="/" state={{ from: location }} replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to={redirectTo || '/'} replace />;
  if (excludedRoles && excludedRoles.includes(user.role)) return <Navigate to={redirectTo || '/'} replace />;

  return <>{children}</>;
};

export default ProtectedRoute;
