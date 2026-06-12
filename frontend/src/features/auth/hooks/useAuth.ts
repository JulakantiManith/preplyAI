import { useState, useEffect, useCallback, createContext, useContext, createElement } from "react";
import type { ReactNode } from "react";
import { supabase } from "@/shared/lib/supabase";
import type { User as SupabaseUser, Session } from "@supabase/supabase-js";
import * as authService from "../services/authService";
import type { RegisterFormData, LoginFormData } from "../schemas/authSchemas";

export interface AuthState {
  user: authService.AuthUser | null;
  session: Session | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface AuthActions {
  login: (data: LoginFormData) => Promise<void>;
  register: (data: RegisterFormData) => Promise<void>;
  logout: () => Promise<void>;
  forgotPassword: (email: string) => Promise<string>;
  resetPassword: (token: string, newPassword: string) => Promise<string>;
}

export type AuthContextValue = AuthState & AuthActions;

const AuthContext = createContext<AuthContextValue | null>(null);

function mapSupabaseUser(user: SupabaseUser): authService.AuthUser {
  return {
    id: user.id,
    email: user.email ?? "",
    fullName: user.user_metadata?.full_name ?? "",
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<authService.AuthUser | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session: currentSession } }) => {
      setSession(currentSession);
      if (currentSession?.user) {
        setUser(mapSupabaseUser(currentSession.user));
      }
      setIsLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, currentSession) => {
        setSession(currentSession);
        if (currentSession?.user) {
          setUser(mapSupabaseUser(currentSession.user));
        } else {
          setUser(null);
        }
        setIsLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const login = useCallback(async (data: LoginFormData) => {
    const result = await authService.loginUser(data);
    setUser(result.user);
  }, []);

  const register = useCallback(async (data: RegisterFormData) => {
    await authService.registerUser(data);
  }, []);

  const logout = useCallback(async () => {
    await authService.logoutUser();
    setUser(null);
    setSession(null);
  }, []);

  const forgotPassword = useCallback(async (email: string) => {
    const response = await authService.forgotPassword(email);
    return response.message;
  }, []);

  const resetPassword = useCallback(async (token: string, newPassword: string) => {
    const response = await authService.resetPassword(token, newPassword);
    return response.message;
  }, []);

  const value: AuthContextValue = {
    user,
    session,
    isAuthenticated: !!session,
    isLoading,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
  };

  return createElement(AuthContext.Provider, { value }, children);
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export { AuthContext };
