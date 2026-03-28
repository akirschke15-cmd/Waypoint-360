import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  border: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  text: {
    primary: string;
    secondary: string;
    muted: string;
  };
}

export type ThemeName = 'swa' | 'neutral';

export const themes: Record<ThemeName, ThemeColors> = {
  swa: {
    primary: '#304CB2',
    secondary: '#FFBF00',
    accent: '#C8102E',
    background: '#0f172a',
    surface: '#1e293b',
    border: '#475569',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    text: {
      primary: '#f1f5f9',
      secondary: '#cbd5e1',
      muted: '#94a3b8',
    },
  },
  neutral: {
    primary: '#3b82f6',
    secondary: '#6366f1',
    accent: '#8b5cf6',
    background: '#09090b',
    surface: '#18181b',
    border: '#3f3f46',
    success: '#22c55e',
    warning: '#eab308',
    error: '#ef4444',
    info: '#06b6d4',
    text: {
      primary: '#fafafa',
      secondary: '#d4d4d8',
      muted: '#a1a1aa',
    },
  },
};

interface ThemeContextType {
  currentTheme: ThemeName;
  setTheme: (theme: ThemeName) => void;
  colors: ThemeColors;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: ThemeName;
}

export function ThemeProvider({
  children,
  defaultTheme = 'swa',
}: ThemeProviderProps): React.ReactElement {
  const [currentTheme, setTheme] = useState<ThemeName>(defaultTheme);

  return React.createElement(
    ThemeContext.Provider,
    {
      value: {
        currentTheme,
        setTheme,
        colors: themes[currentTheme],
      },
    },
    children
  );
}

export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
