import { ResetPasswordForm } from "../components/ResetPasswordForm";

export function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 auth-bg-gradient">
      <div className="w-full max-w-md space-y-6 rounded-xl border bg-card/80 backdrop-blur-sm shadow-lg p-8">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Set New Password
          </h1>
          <p className="text-sm text-muted-foreground">
            Choose a strong password for your account
          </p>
        </div>

        <ResetPasswordForm />
      </div>
    </div>
  );
}
