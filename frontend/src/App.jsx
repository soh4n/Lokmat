import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import Navbar from './components/Navbar.jsx';
import BottomNav from './components/BottomNav.jsx';
import Login from './pages/Login.jsx';
import Profile from './pages/Profile.jsx';
import Home from './pages/Home.jsx';
import MyVote from './pages/MyVote.jsx';
import Election from './pages/Election.jsx';
import Live from './pages/Live.jsx';
import Volunteer from './pages/Volunteer.jsx';
import SOS from './pages/SOS.jsx';
import AIGuide from './pages/AIGuide.jsx';

/**
 * Route guard — redirects to /login if not authenticated.
 */
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

/**
 * Route guard for login — redirects to / if already authenticated.
 */
function PublicRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return children;
}

/**
 * Layout wrapper — shows Navbar + BottomNav for authenticated pages.
 */
function AppLayout({ children }) {
  return (
    <>
      <a href="#main-content" className="skip-to-content">
        Skip to main content
      </a>
      <Navbar />
      <div id="main-content">{children}</div>
      <BottomNav />
    </>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
    <BrowserRouter>
      <Routes>
        {/* Public route — login */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />

        {/* Protected routes with layout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout><Home /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <AppLayout><Profile /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/my-vote"
          element={
            <ProtectedRoute>
              <AppLayout><MyVote /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/election"
          element={
            <ProtectedRoute>
              <AppLayout><Election /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/live"
          element={
            <ProtectedRoute>
              <AppLayout><Live /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/volunteer"
          element={
            <ProtectedRoute>
              <AppLayout><Volunteer /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/sos"
          element={
            <ProtectedRoute>
              <AppLayout><SOS /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-guide"
          element={
            <ProtectedRoute>
              <AppLayout><AIGuide /></AppLayout>
            </ProtectedRoute>
          }
        />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
    </ErrorBoundary>
  );
}
