import { RegisterForm } from "../components/RegisterForm";

export function RegisterPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 auth-bg-gradient">
      <div className="w-full max-w-md space-y-6 rounded-xl border bg-card/80 backdrop-blur-sm shadow-lg p-8">
        <div className="text-center space-y-2">
          <img src="/logo.png" alt="Preply AI" className="mx-auto h-12 w-12 rounded-lg object-contain" />
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Create an Account
          </h1>
          <p className="text-sm text-muted-foreground">
            Start practicing smarter with AI-powered coaching
          </p>
        </div>

        <RegisterForm />
      </div>
    </div>
  );
}
