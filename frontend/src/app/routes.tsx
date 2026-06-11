import { Routes, Route } from "react-router-dom";
import { Layout } from "@/shared/components/Layout";

// Placeholder pages — will be replaced by feature modules
function DashboardPage() {
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Dashboard</h1><p className="text-muted-foreground">Your practice overview will appear here.</p></div>;
}

function InterviewPage() {
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Interview Practice</h1><p className="text-muted-foreground">Start a new interview session.</p></div>;
}

function PresentationPage() {
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Presentation Practice</h1><p className="text-muted-foreground">Practice your presentation skills.</p></div>;
}

function AnalyticsPage() {
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Analytics</h1><p className="text-muted-foreground">Track your progress over time.</p></div>;
}

function HistoryPage() {
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Session History</h1><p className="text-muted-foreground">Review your past sessions.</p></div>;
}

function ProfilePage() {
  return <div className="space-y-4"><h1 className="text-2xl font-bold">Profile</h1><p className="text-muted-foreground">Manage your profile and preferences.</p></div>;
}

function LoginPage() {
  return <div className="flex min-h-screen items-center justify-center"><div className="space-y-4 text-center"><h1 className="text-2xl font-bold">Sign In</h1><p className="text-muted-foreground">Login form will be implemented here.</p></div></div>;
}

function LandingPage() {
  return <div className="flex min-h-screen items-center justify-center"><div className="space-y-4 text-center"><h1 className="text-4xl font-bold">AI Interview & Presentation Coach</h1><p className="text-muted-foreground">Practice smarter, perform better.</p></div></div>;
}

function NotFoundPage() {
  return <div className="flex min-h-screen items-center justify-center"><div className="space-y-4 text-center"><h1 className="text-4xl font-bold">404</h1><p className="text-muted-foreground">Page not found.</p></div></div>;
}

export function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />

      {/* Authenticated routes with layout */}
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/interview" element={<InterviewPage />} />
        <Route path="/presentation" element={<PresentationPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
