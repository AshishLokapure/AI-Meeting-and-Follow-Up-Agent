import { createFileRoute, Link, redirect, useNavigate } from "@tanstack/react-router";
import type { FormEvent } from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
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

export const Route = createFileRoute("/login")({
  beforeLoad: () => {
    if (hasAuthSession()) {
      throw redirect({ to: "/dashboard" });
    }
  },
  head: () => ({ meta: [{ title: "Sign in - Loop" }] }),
  component: LoginPage,
});

function LoginPage() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const response = await apiRequest<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      if (!response.tokens) {
        throw new Error("Login did not return tokens.");
      }

      saveAuthSession({ user: response.user, tokens: response.tokens });
      if (!rememberMe) {
        window.sessionStorage.setItem("loop.auth.temporary", "true");
      }
      await nav({ to: "/dashboard", replace: true });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to your Loop workspace"
      footer={
        <>
          Don't have an account? {" "}
          <Link to="/register" className="font-semibold text-primary hover:underline">
            Create one
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-1.5">
          <Label htmlFor="email">Email</Label>
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
          <div className="flex items-center justify-between">
            <Label htmlFor="pw">Password</Label>
            <Link to="/forgot-password" className="text-xs font-medium text-primary hover:underline">
              Forgot?
            </Link>
          </div>
          <Input
            id="pw"
            type="password"
            placeholder="********"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <Checkbox checked={rememberMe} onCheckedChange={(checked) => setRememberMe(checked === true)} />
          Remember me
        </label>
        {errorMessage ? (
          <p className="rounded-md border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive">
            {errorMessage}
          </p>
        ) : null}
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </Button>
        <Button type="button" variant="outline" className="w-full" disabled={isSubmitting}>
          Continue with Google
        </Button>
      </form>
    </AuthLayout>
  );
}
