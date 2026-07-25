import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { PageHeader } from "@/components/app/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { useUserProfile, useUpdateProfile, useChangePassword } from "@/lib/services";
import { getAuthSession } from "@/lib/auth";
import { toast } from "sonner";

export const Route = createFileRoute("/_app/profile")({
  head: () => ({ meta: [{ title: "Profile — Loop" }] }),
  component: ProfilePage,
});

function ProfilePage() {
  const { data: userProfile, isLoading } = useUserProfile();
  const updateProfileMutation = useUpdateProfile();
  const changePasswordMutation = useChangePassword();

  const session = getAuthSession();
  const initialName = userProfile?.name || session?.user?.name || "";
  const initialEmail = userProfile?.email || session?.user?.email || "";
  const role = userProfile?.role || session?.user?.role || "User";

  const [name, setName] = useState(initialName);
  const [email, setEmail] = useState(initialEmail);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Sync state once fetched
  useEffect(() => {
    if (userProfile) {
      setName(userProfile.name);
      setEmail(userProfile.email);
    }
  }, [userProfile]);

  const handleSaveChanges = () => {
    if (!name || !email) {
      toast.error("Name and Email are required");
      return;
    }

    updateProfileMutation.mutate(
      { name, email },
      {
        onSuccess: () => {
          toast.success("Profile updated successfully");
        },
        onError: (err) => {
          toast.error(`Error updating profile: ${err.message}`);
        },
      }
    );
  };

  const handleChangePassword = () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error("All password fields are required");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match");
      return;
    }

    changePasswordMutation.mutate(
      { current_password: currentPassword, new_password: newPassword },
      {
        onSuccess: () => {
          toast.success("Password updated successfully");
          setCurrentPassword("");
          setNewPassword("");
          setConfirmPassword("");
        },
        onError: (err) => {
          toast.error(`Error updating password: ${err.message}`);
        },
      }
    );
  };

  const initials = name.split(" ").map((n) => n[0]).join("");

  if (isLoading) {
    return (
      <div className="flex h-60 items-center justify-center">
        <p className="text-muted-foreground animate-pulse">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Profile" description="Manage your personal info and preferences" />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="rounded-xl shadow-sm">
          <CardContent className="flex flex-col items-center gap-3 p-6 text-center">
            <Avatar className="h-24 w-24">
              <AvatarFallback className="bg-primary/10 text-2xl font-semibold text-primary">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div>
              <h3 className="text-lg font-bold">{name}</h3>
              <p className="text-sm text-muted-foreground">{role}</p>
              <p className="mt-1 text-xs text-muted-foreground">{email}</p>
            </div>
            <Button variant="outline" size="sm">Change photo</Button>
          </CardContent>
        </Card>

        <Card className="rounded-xl shadow-sm lg:col-span-2">
          <CardHeader><CardTitle>User information</CardTitle></CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="name">Full name</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="role">Role</Label>
              <Input id="role" value={role} disabled className="bg-muted" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="tz">Timezone</Label>
              <Input id="tz" defaultValue="America/Los_Angeles" />
            </div>
            <div className="sm:col-span-2">
              <Button onClick={handleSaveChanges} disabled={updateProfileMutation.isPending}>
                {updateProfileMutation.isPending ? "Saving..." : "Save changes"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-xl shadow-sm lg:col-span-2">
          <CardHeader><CardTitle>Change password</CardTitle></CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5 sm:col-span-2">
              <Label htmlFor="current">Current password</Label>
              <Input
                id="current"
                type="password"
                placeholder="••••••••"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="new">New password</Label>
              <Input
                id="new"
                type="password"
                placeholder="••••••••"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="confirm">Confirm</Label>
              <Input
                id="confirm"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
            <div className="sm:col-span-2">
              <Button onClick={handleChangePassword} disabled={changePasswordMutation.isPending}>
                {changePasswordMutation.isPending ? "Updating..." : "Update password"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-xl shadow-sm">
          <CardHeader><CardTitle>Notification preferences</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {["Email reminders", "Slack reminders", "Weekly digest", "Escalation alerts"].map((label, i) => (
              <div key={label} className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-sm font-medium">{label}</p>
                  <p className="text-xs text-muted-foreground">Delivered when action is required</p>
                </div>
                <Switch defaultChecked={i !== 2} />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
