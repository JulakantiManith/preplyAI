import type { ReactNode } from "react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "@/shared/contexts/ThemeContext";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system">
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
