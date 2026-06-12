import { ForgotPasswordForm } from "../components/ForgotPasswordForm";

export function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Reset Your Password
          </h1>
          <p className="text-sm text-muted-foreground">
            We&apos;ll send you a link to reset your password
          </p>
        </div>

        <ForgotPasswordForm />
      </div>
    </div>
  );
}
