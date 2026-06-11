import { useContext } from "react";
import { ThemeContext } from "@/shared/contexts/ThemeContext";

/**
 * Custom hook to access the current theme state and setter.
 * Must be used within a ThemeProvider.
 */
export function useTheme() {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }

  return context;
}
