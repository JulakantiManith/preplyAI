import { supabase, getEmailVerificationUrl } from "@/shared/lib/supabase";
import apiClient from "@/shared/lib/axios";
import type { RegisterFormData, LoginFormData } from "../schemas/authSchemas";

export interface AuthUser {
  id: string;
  email: string;
  fullName: string;
}

export interface AuthResponse {
  accessToken: string;
  tokenType: string;
  user: AuthUser;
}

export interface MessageResponse {
  message: string;
}

export async function registerUser(data: RegisterFormData): Promise<AuthResponse> {
  // Use Supabase client directly for registration (handles session automatically)
  const { data: authData, error } = await supabase.auth.signUp({
    email: data.email,
    password: data.password,
    options: {
      data: { full_name: data.fullName },
      emailRedirectTo: getEmailVerificationUrl(),
    },
  });

  if (error) {
    console.error("[Auth] Registration failed:", {
      code: error.code,
      message: error.message,
      status: error.status,
      name: error.name,
    });
    const authError: AuthError = new Error(error.message || "Registration failed. Please try again.");
    authError.code = error.code;
    throw authError;
  }

  if (!authData.user) {
    throw new Error("Registration failed. Please try again.");
  }

  const user = authData.user;
  const session = authData.session;

  return {
    accessToken: session?.access_token ?? "",
    tokenType: "bearer",
    user: {
      id: user.id,
      email: user.email ?? data.email,
      fullName: user.user_metadata?.full_name ?? data.fullName,
    },
  };
}

export interface AuthError extends Error {
  code?: string;
}

export async function loginUser(data: LoginFormData): Promise<AuthResponse> {
  // Use Supabase client for auth (handles tokens automatically)
  const { data: authData, error } = await supabase.auth.signInWithPassword({
    email: data.email,
    password: data.password,
  });

  if (error) {
    const authError: AuthError = new Error(error.message || "Invalid email or password");
    authError.code = error.code;
    throw authError;
  }

  const session = authData.session;
  const user = authData.user;

  return {
    accessToken: session.access_token,
    tokenType: "bearer",
    user: {
      id: user.id,
      email: user.email ?? "",
      fullName: user.user_metadata?.full_name ?? "",
    },
  };
}

export async function logoutUser(): Promise<void> {
  const { error } = await supabase.auth.signOut();
  if (error) {
    throw new Error(error.message);
  }
}

export async function forgotPassword(email: string): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>("/auth/forgot-password", {
    email,
  });
  return response.data;
}

export async function resetPassword(
  token: string,
  newPassword: string
): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>("/auth/reset-password", {
    token,
    new_password: newPassword,
  });
  return response.data;
}
