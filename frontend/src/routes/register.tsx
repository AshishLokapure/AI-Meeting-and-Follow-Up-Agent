import { createFileRoute, Link, redirect, useNavigate } from "@tanstack/react-router";
import type { FormEvent } from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthLayout } from "@/components/app/auth-layout";
import { apiRequest } from "@/lib/api";
import { hasAuthSession, saveAuthSession } from "@/lib/auth";

type AuthUser = {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  email_verified: boolean;
  avatar_url?: string | null;
  email_verified_at?: string | null;
  last_login_at?: string | null;
};

type AuthResponse = {
  user: AuthUser;
  tokens: {
    access_token: string;
    refresh_token: string;
    token_type?: string;
  } | null;
  message: string;
  verification_token?: string | null;
};

export const Route = createFileRoute("/register")({
  beforeLoad: () => {
    if (hasAuthSession()) {
      throw redirect({ to: "/dashboard" });
    }
  },
  head: () => ({ meta: [{ title: "Create account - Loop" }] }),
  component: RegisterPage,
});

function RegisterPage() {
  const nav = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);

    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match.");
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await apiRequest<AuthResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      });

      if (response.verification_token) {
        await apiRequest<{ message: string }>("/auth/verify-email", {
          method: "POST",
          body: JSON.stringify({ token: response.verification_token }),
        });
      }

      const loginResponse = await apiRequest<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      if (!loginResponse.tokens) {
        throw new Error("Registration completed, but login tokens were not returned.");
      }

      saveAuthSession({ user: loginResponse.user, tokens: loginResponse.tokens });
      await nav({ to: "/dashboard", replace: true });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Registration failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start closing the loop on every meeting"
      footer={
        <>
          Already have an account? {" "}
          <Link to="/login" className="font-semibold text-primary hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-1.5">
          <Label htmlFor="name">Full name</Label>
          <Input
            id="name"
            placeholder="Alex Morgan"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="email">Work email</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@company.com"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="pw">Password</Label>
          <Input
            id="pw"
            type="password"
            placeholder="********"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="cpw">Confirm password</Label>
          <Input
            id="cpw"
            type="password"
            placeholder="********"
            required
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
          />
        </div>
        {errorMessage ? (
          <p className="rounded-md border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive">
            {errorMessage}
          </p>
        ) : null}
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </Button>
        <Button type="button" variant="outline" className="w-full" disabled={isSubmitting}>
          Continue with Google
        </Button>
      </form>
    </AuthLayout>
  );
}
