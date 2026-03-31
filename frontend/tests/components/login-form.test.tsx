import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { LoginForm } from "@/features/auth/login-form";

const loginMock = vi.fn();

vi.mock("@/lib/auth/context", () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    role: null,
    login: loginMock,
    logout: vi.fn(),
  }),
}));

describe("LoginForm", () => {
  beforeEach(() => {
    loginMock.mockReset();
  });

  it("renders email and password input fields", () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/^email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password/i)).toBeInTheDocument();
  });

  it("shows validation error when submitting empty form", async () => {
    const user = userEvent.setup();
    render(<LoginForm />);
    await user.click(screen.getByRole("button", { name: /sign in/i }));
    expect(await screen.findByText("Email is required")).toBeInTheDocument();
    expect(screen.getByText("Password is required")).toBeInTheDocument();
  });

  it("shows validation error for invalid email format", async () => {
    const user = userEvent.setup();
    render(<LoginForm />);
    await user.type(screen.getByLabelText(/^email/i), "not-an-email");
    await user.type(screen.getByLabelText(/^password/i), "secret");
    await user.click(screen.getByRole("button", { name: /sign in/i }));
    expect(await screen.findByText("Invalid email format")).toBeInTheDocument();
    expect(loginMock).not.toHaveBeenCalled();
  });

  it("calls login function with email and password on valid submit", async () => {
    const user = userEvent.setup();
    loginMock.mockResolvedValue(undefined);
    render(<LoginForm />);
    await user.type(screen.getByLabelText(/^email/i), "user@company.com");
    await user.type(screen.getByLabelText(/^password/i), "password123");
    await user.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith("user@company.com", "password123");
    });
  });

  it("shows error message when login fails (API error)", async () => {
    const user = userEvent.setup();
    loginMock.mockRejectedValue({ detail: "Invalid email or password" });
    render(<LoginForm />);
    await user.type(screen.getByLabelText(/^email/i), "user@company.com");
    await user.type(screen.getByLabelText(/^password/i), "wrong");
    await user.click(screen.getByRole("button", { name: /sign in/i }));
    expect(await screen.findByText("Invalid email or password")).toBeInTheDocument();
  });

  it("shows loading state on submit button during submission", async () => {
    const user = userEvent.setup();
    let release!: () => void;
    const loginPromise = new Promise<void>((resolve) => {
      release = resolve;
    });
    loginMock.mockReturnValue(loginPromise);

    render(<LoginForm />);
    await user.type(screen.getByLabelText(/^email/i), "user@company.com");
    await user.type(screen.getByLabelText(/^password/i), "password123");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    const button = screen.getByRole("button", { name: /sign in/i });
    await waitFor(() => expect(button).toBeDisabled());
    expect(button.querySelector("svg")).toBeTruthy();

    release!();
    await waitFor(() => expect(button).not.toBeDisabled());
  });
});
