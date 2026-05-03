import { createContext, useContext, useState, useCallback, useEffect } from 'react';

const AuthContext = createContext();

const USER_KEY = 'lokmat_user';
const TOKEN_KEY = 'lokmat_token';

/**
 * Provides authentication state, JWT token, and user profile management.
 * Persists to localStorage for session continuity per GEMINI.md UX requirements.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem(USER_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem(TOKEN_KEY) || null;
    } catch {
      return null;
    }
  });

  const [isAuthenticated, setIsAuthenticated] = useState(!!user);

  useEffect(() => {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      setIsAuthenticated(true);
    } else {
      localStorage.removeItem(USER_KEY);
      setIsAuthenticated(false);
    }
  }, [user]);

  useEffect(() => {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  }, [token]);

  const login = useCallback((userData, authToken = null) => {
    setUser({
      ...userData,
      loginAt: new Date().toISOString(),
    });
    if (authToken) {
      setToken(authToken);
    }
  }, []);

  const updateProfile = useCallback((profileData) => {
    setUser((prev) => ({
      ...prev,
      ...profileData,
      profileComplete: true,
      updatedAt: new Date().toISOString(),
    }));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
  }, []);

  const isProfileComplete = user?.profileComplete === true;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        isProfileComplete,
        login,
        updateProfile,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
