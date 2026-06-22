import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useSearchParams } from "react-router-dom";
import { Eye, EyeOff, Loader2, CheckCircle2 } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import { resetPasswordSchema } from "../schemas/authSchemas";
import type { ResetPasswordFormData } from "../schemas/authSchemas";
import { useAuth } from "../hooks/useAuth";

export function ResetPasswordForm() {
  const { resetPassword } = useAuth();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { token },
  });

  const onSubmit = async (data: ResetPasswordFormData) => {
    setFormError(null);
    setSuccessMessage(null);
    try {
      await resetPassword(data.token, data.newPassword);
      setSuccessMessage("Your password has been reset successfully.");
    } catch (error) {
      if (error instanceof Error) {
        setFormError(error.message);
      } else {
        setFormError("The reset link is invalid or has expired. Please request a new one.");
      }
    }
  };

  if (!token) {
    return (
      <div className="space-y-4 text-center">
        <p className="text-sm text-destructive">
          Invalid reset link. The token is missing.
        </p>
        <Link
          to="/forgot-password"
          className="inline-block text-sm text-primary hover:underline font-medium"
        >
          Request a new reset link
        </Link>
      </div>
    );
  }

  if (successMessage) {
    return (
      <div className="space-y-4 text-center">
        <CheckCircle2 className="mx-auto h-12 w-12 text-green-500" />
        <p className="text-sm text-muted-foreground">{successMessage}</p>
        <Link
          to="/login"
          className="inline-block text-sm text-primary hover:underline font-medium"
        >
          Sign in with your new password
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      {formError && (
        <div
          className="rounded-md bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive"
          role="alert"
        >
          {formError}
        </div>
      )}

      <input type="hidden" {...register("token")} />

      <div className="space-y-2">
        <label htmlFor="newPassword" className="text-sm font-medium text-foreground">
          New Password
        </label>
        <div className="relative">
          <input
            id="newPassword"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="Enter your new password"
            className={cn(
              "flex h-10 w-full rounded-md border bg-background px-3 py-2 pr-10 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors duration-200",
              errors.newPassword ? "border-destructive" : "border-input"
            )}
            aria-invalid={errors.newPassword ? "true" : undefined}
            aria-describedby={errors.newPassword ? "newPassword-error" : undefined}
            {...register("newPassword")}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {errors.newPassword && (
          <p id="newPassword-error" className="text-xs text-destructive">
            {errors.newPassword.message}
          </p>
        )}
        <p className="text-xs text-muted-foreground">
          At least 8 characters with uppercase, lowercase, and a number.
        </p>
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        Reset Password
      </Button>
    </form>
  );
}
