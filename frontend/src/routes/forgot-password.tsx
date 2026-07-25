import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthLayout } from "@/components/app/auth-layout";
import { toast } from "sonner";

export const Route = createFileRoute("/forgot-password")({
  head: () => ({ meta: [{ title: "Reset password — Loop" }] }),
  component: ForgotPage,
});

function ForgotPage() {
  return (
    <AuthLayout
      title="Reset your password"
      subtitle="We'll email you a secure reset link"
      footer={<Link to="/login" className="font-semibold text-primary hover:underline">Back to sign in</Link>}
    >
      <form
        className="space-y-4"
        onSubmit={(e) => { e.preventDefault(); toast.success("Reset link sent"); }}
      >
        <div className="space-y-1.5">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" placeholder="you@company.com" required />
        </div>
        <Button type="submit" className="w-full">Send reset link</Button>
      </form>
    </AuthLayout>
  );
}
