import { z } from "zod";

const passwordSchema = z
  .string()
  .min(8, "Password must be at least 8 characters")
  .max(128, "Password must be at most 128 characters")
  .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
  .regex(/[a-z]/, "Password must contain at least one lowercase letter")
  .regex(/\d/, "Password must contain at least one digit");

export const registerSchema = z.object({
  fullName: z
    .string()
    .min(1, "Full name is required")
    .max(100, "Full name must be at most 100 characters")
    .refine((val) => val.trim().length > 0, "Full name cannot be blank"),
  email: z.string().min(1, "Email is required").email("Invalid email format"),
  password: passwordSchema,
});

export const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Invalid email format"),
  password: z.string().min(1, "Password is required"),
});

export const forgotPasswordSchema = z.object({
  email: z.string().min(1, "Email is required").email("Invalid email format"),
});

export const resetPasswordSchema = z.object({
  token: z.string().min(1, "Token is required"),
  newPassword: passwordSchema,
});

export type RegisterFormData = z.infer<typeof registerSchema>;
export type LoginFormData = z.infer<typeof loginSchema>;
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
