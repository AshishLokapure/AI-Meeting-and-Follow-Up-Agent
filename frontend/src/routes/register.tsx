import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthLayout } from "@/components/app/auth-layout";

export const Route = createFileRoute("/register")({
  head: () => ({ meta: [{ title: "Create account — Loop" }] }),
  component: RegisterPage,
});

function RegisterPage() {
  const nav = useNavigate();
  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start closing the loop on every meeting"
      footer={<>Already have an account? <Link to="/login" className="font-semibold text-primary hover:underline">Sign in</Link></>}
    >
      <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); nav({ to: "/dashboard" }); }}>
        <div className="space-y-1.5">
          <Label htmlFor="name">Full name</Label>
          <Input id="name" placeholder="Alex Morgan" required />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="email">Work email</Label>
          <Input id="email" type="email" placeholder="you@company.com" required />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="pw">Password</Label>
          <Input id="pw" type="password" placeholder="••••••••" required />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="cpw">Confirm password</Label>
          <Input id="cpw" type="password" placeholder="••••••••" required />
        </div>
        <Button type="submit" className="w-full">Create account</Button>
        <Button type="button" variant="outline" className="w-full">Continue with Google</Button>
      </form>
    </AuthLayout>
  );
}
