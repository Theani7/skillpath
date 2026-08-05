import { lazy, Suspense, useState, useCallback, type ReactNode } from 'react';
import { BrowserRouter, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import PublicTopBar from './components/Navbar';
import AuthModal from './components/AuthModal';
import Sidebar from './components/Sidebar';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import PageLoader from './components/Skeleton';

const Landing = lazy(() => import('./pages/Landing'));
const Analyzer = lazy(() => import('./pages/Analyzer'));
const AnalysisResult = lazy(() => import('./pages/AnalysisResult'));
const Settings = lazy(() => import('./pages/Settings'));
const Profile = lazy(() => import('./pages/Profile'));
const Admin = lazy(() => import('./pages/Admin'));
const JobRoles = lazy(() => import('./pages/JobRoles'));
const AIMonitoring = lazy(() => import('./pages/AIMonitoring'));
const SharedReport = lazy(() => import('./pages/SharedReport'));
const MockInterview = lazy(() => import('./pages/MockInterview'));

const withBoundary = (node: ReactNode) => <ErrorBoundary>{node}</ErrorBoundary>;

const PUBLIC_PATHS = ['/', '/shared/'];

const Layout = () => {
  const location = useLocation();
  const { user, loading } = useAuth();
  const isPublic = PUBLIC_PATHS.includes(location.pathname) || location.pathname.startsWith('/shared/');

  const [authModal, setAuthModal] = useState<{ isOpen: boolean; tab: 'login' | 'register' }>({ isOpen: false, tab: 'login' });

  const openAuthModal = useCallback((tab: 'login' | 'register' = 'login') => {
    setAuthModal({ isOpen: true, tab });
  }, []);

  const closeAuthModal = useCallback(() => {
    setAuthModal({ isOpen: false, tab: 'login' });
  }, []);

  if (loading && !isPublic) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)' }}>
        <PageLoader />
      </div>
    );
  }

  if (isPublic) {
    return (
      <div className="app-shell" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <PublicTopBar openAuthModal={openAuthModal} />
        <main style={{ flex: 1, width: '100%' }}>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={withBoundary(<Landing openAuthModal={openAuthModal} />)} />
              <Route path="/shared/:token" element={withBoundary(<SharedReport openAuthModal={openAuthModal} />)} />
            </Routes>
          </Suspense>
        </main>
        <AuthModal
          isOpen={authModal.isOpen}
          onClose={closeAuthModal}
          initialTab={authModal.tab}
        />
      </div>
    );
  }

  return (
    <div
      className="app-shell"
      style={{
        minHeight: '100vh', display: 'flex',
        flexDirection: 'row', alignItems: 'stretch',
        background: 'var(--color-bg)',
      }}
    >
      {user ? <ErrorBoundary><Sidebar /></ErrorBoundary> : <Navigate to="/" replace />}
      <main
        style={{
          flex: 1, minWidth: 0,
          padding: '32px 32px 64px',
          background: 'var(--color-bg)',
        }}
        className="app-main"
      >
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/app" element={<ProtectedRoute excludedRoles={['admin']} redirectTo="/admin">{withBoundary(<Analyzer />)}</ProtectedRoute>} />
            <Route path="/analysis" element={<ProtectedRoute excludedRoles={['admin']} redirectTo="/admin">{withBoundary(<AnalysisResult />)}</ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute>{withBoundary(<Settings />)}</ProtectedRoute>} />
            <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={['admin']}>{withBoundary(<Admin />)}</ProtectedRoute>} />
            <Route path="/admin/resumes" element={<ProtectedRoute allowedRoles={['admin']}>{withBoundary(<Admin />)}</ProtectedRoute>} />
            <Route path="/admin/users" element={<ProtectedRoute allowedRoles={['admin']}>{withBoundary(<Admin />)}</ProtectedRoute>} />
            <Route path="/admin/feedback" element={<ProtectedRoute allowedRoles={['admin']}>{withBoundary(<Admin />)}</ProtectedRoute>} />
            <Route path="/admin/courses" element={<ProtectedRoute allowedRoles={['admin']}>{withBoundary(<Admin />)}</ProtectedRoute>} />
            <Route path="/admin/job-roles" element={<ProtectedRoute allowedRoles={['admin']}>{withBoundary(<JobRoles />)}</ProtectedRoute>} />
            <Route path="/admin/ai-monitoring" element={<ProtectedRoute allowedRoles={['admin']}>{withBoundary(<AIMonitoring />)}</ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute>{withBoundary(<Profile />)}</ProtectedRoute>} />
            <Route path="/mock-interview" element={<ProtectedRoute excludedRoles={['admin']} redirectTo="/admin">{withBoundary(<MockInterview />)}</ProtectedRoute>} />
            <Route path="*" element={<Navigate to={user?.role === 'admin' ? '/admin/dashboard' : '/app'} replace />} />
          </Routes>
        </Suspense>
      </main>

      <style>{`
        @media (max-width: 1023px) {
          .app-main { padding: 64px 20px 48px !important; }
        }
        @media (max-width: 480px) {
          .app-main { padding: 56px 16px 40px !important; }
        }
      `}</style>
    </div>
  );
};

const App = () => (
  <AuthProvider>
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  </AuthProvider>
);

export default App;
