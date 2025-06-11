import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authService from '../services_api/authService';

interface User {
  email: string;
  username: string;
  id: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, userInfo: User) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar si hay token guardado al cargar la aplicación
    const savedToken = authService.getToken();
    const savedUser = authService.getUser();
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(savedUser);
    }
    setLoading(false);
  }, []);

  const login = (newToken: string, userInfo: User) => {
    setToken(newToken);
    setUser(userInfo);
    authService.setToken(newToken);
    authService.setUser(userInfo);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    authService.logout();
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user,
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

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
