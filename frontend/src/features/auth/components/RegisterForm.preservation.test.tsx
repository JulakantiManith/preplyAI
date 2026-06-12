import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { RegisterForm } from "./RegisterForm";

/**
 * **Validates: Requirements 3.1**
 *
 * Preservation Test: RegisterForm displays the error .message directly
 * for non-rate-limit errors (no special handling).
 *
 * On UNFIXED code, this test SHOULD PASS because RegisterForm currently
 * displays whatever error.message it receives without any code-specific logic.
 */

// Mock useAuth hook
vi.mock("../hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

import { useAuth } from "../hooks/useAuth";

const mockedUseAuth = vi.mocked(useAuth);

describe("RegisterForm - Preservation: Non-Rate-Limit Error Display", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display the raw error message for "User already registered" error', async () => {
    const user = userEvent.setup();

    const error = new Error("User already registered");

    mockedUseAuth.mockReturnValue({
      register: vi.fn().mockRejectedValue(error),
      login: vi.fn(),
      logout: vi.fn(),
      forgotPassword: vi.fn(),
      resetPassword: vi.fn(),
      user: null,
      session: null,
      isAuthenticated: false,
      isLoading: false,
    } as any);

    render(
      <MemoryRouter>
        <RegisterForm />
      </MemoryRouter>
    );

    // Fill in form with valid data
    await user.type(screen.getByLabelText(/full name/i), "John Doe");
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByPlaceholderText(/create a strong password/i), "StrongPass1");

    // Submit the form
    await user.click(screen.getByRole("button", { name: /create account/i }));

    // Wait for the error message - should display raw message
    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert).toHaveTextContent("User already registered");
    });
  });

  it('should display the raw error message for "Invalid credentials" error', async () => {
    const user = userEvent.setup();

    const error = new Error("Invalid credentials");

    mockedUseAuth.mockReturnValue({
      register: vi.fn().mockRejectedValue(error),
      login: vi.fn(),
      logout: vi.fn(),
      forgotPassword: vi.fn(),
      resetPassword: vi.fn(),
      user: null,
      session: null,
      isAuthenticated: false,
      isLoading: false,
    } as any);

    render(
      <MemoryRouter>
        <RegisterForm />
      </MemoryRouter>
    );

    // Fill in form with valid data
    await user.type(screen.getByLabelText(/full name/i), "Jane Smith");
    await user.type(screen.getByLabelText(/email/i), "jane@example.com");
    await user.type(screen.getByPlaceholderText(/create a strong password/i), "StrongPass1");

    // Submit the form
    await user.click(screen.getByRole("button", { name: /create account/i }));

    // Wait for the error message - should display raw message
    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert).toHaveTextContent("Invalid credentials");
    });
  });

  it('should display "Registration failed. Please try again." for non-Error exceptions', async () => {
    const user = userEvent.setup();

    // Throw a non-Error value (e.g., a string)
    mockedUseAuth.mockReturnValue({
      register: vi.fn().mockRejectedValue("some non-error value"),
      login: vi.fn(),
      logout: vi.fn(),
      forgotPassword: vi.fn(),
      resetPassword: vi.fn(),
      user: null,
      session: null,
      isAuthenticated: false,
      isLoading: false,
    } as any);

    render(
      <MemoryRouter>
        <RegisterForm />
      </MemoryRouter>
    );

    // Fill in form with valid data
    await user.type(screen.getByLabelText(/full name/i), "Test User");
    await user.type(screen.getByLabelText(/email/i), "test2@example.com");
    await user.type(screen.getByPlaceholderText(/create a strong password/i), "StrongPass1");

    // Submit the form
    await user.click(screen.getByRole("button", { name: /create account/i }));

    // Wait for the generic fallback message
    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert).toHaveTextContent("Registration failed. Please try again.");
    });
  });
});
