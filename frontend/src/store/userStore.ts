import { create } from 'zustand';
import type { User } from '../types';

interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null,

  login: async (email: string, _password: string) => {
    set({ loading: true, error: null });
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock successful login
      const mockUser: User = {
        id: '1',
        username: 'astronomer',
        email,
        createdAt: new Date(),
      };
      
      localStorage.setItem('astroai_token', 'mock_token');
      set({ user: mockUser, isAuthenticated: true, loading: false });
    } catch (error) {
      set({ error: 'Login failed', loading: false });
    }
  },

  register: async (username: string, email: string, _password: string) => {
    set({ loading: true, error: null });
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockUser: User = {
        id: crypto.randomUUID(),
        username,
        email,
        createdAt: new Date(),
      };
      
      localStorage.setItem('astroai_token', 'mock_token');
      set({ user: mockUser, isAuthenticated: true, loading: false });
    } catch (error) {
      set({ error: 'Registration failed', loading: false });
    }
  },

  logout: () => {
    localStorage.removeItem('astroai_token');
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('astroai_token');
    
    if (token) {
      // Simulate token validation
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const mockUser: User = {
        id: '1',
        username: 'astronomer',
        email: 'user@astroai.com',
        createdAt: new Date(),
      };
      
      set({ user: mockUser, isAuthenticated: true });
    }
  },
}));
