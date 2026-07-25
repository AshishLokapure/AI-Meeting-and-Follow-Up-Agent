import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { AuthLayout } from "@/components/app/auth-layout";

export const Route = createFileRoute("/login")({
  head: () => ({ meta: [{ title: "Sign in — Loop" }] }),
  component: LoginPage,
});

function LoginPage() {
  const nav = useNavigate();
  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to your Loop workspace"
      footer={<>Don't have an account? <Link to="/register" className="font-semibold text-primary hover:underline">Create one</Link></>}
    >
      <form
        className="space-y-4"
        onSubmit={(e) => { e.preventDefault(); nav({ to: "/dashboard" }); }}
      >
        <div className="space-y-1.5">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" placeholder="you@company.com" required />
        </div>
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="pw">Password</Label>
            <Link to="/forgot-password" className="text-xs font-medium text-primary hover:underline">Forgot?</Link>
          </div>
          <Input id="pw" type="password" placeholder="••••••••" required />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <Checkbox defaultChecked /> Remember me
        </label>
        <Button type="submit" className="w-full">Sign in</Button>
        <Button type="button" variant="outline" className="w-full">Continue with Google</Button>
      </form>
    </AuthLayout>
  );
}
