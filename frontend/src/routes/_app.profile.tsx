import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/app/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { currentUser } from "@/lib/mock-data";

export const Route = createFileRoute("/_app/profile")({
  head: () => ({ meta: [{ title: "Profile — Loop" }] }),
  component: ProfilePage,
});

function ProfilePage() {
  const initials = currentUser.name.split(" ").map((n) => n[0]).join("");
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
              <h3 className="text-lg font-bold">{currentUser.name}</h3>
              <p className="text-sm text-muted-foreground">{currentUser.role}</p>
              <p className="mt-1 text-xs text-muted-foreground">{currentUser.email}</p>
            </div>
            <Button variant="outline" size="sm">Change photo</Button>
          </CardContent>
        </Card>

        <Card className="rounded-xl shadow-sm lg:col-span-2">
          <CardHeader><CardTitle>User information</CardTitle></CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="name">Full name</Label>
              <Input id="name" defaultValue={currentUser.name} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" defaultValue={currentUser.email} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="role">Role</Label>
              <Input id="role" defaultValue={currentUser.role} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="tz">Timezone</Label>
              <Input id="tz" defaultValue="America/Los_Angeles" />
            </div>
            <div className="sm:col-span-2">
              <Button>Save changes</Button>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-xl shadow-sm lg:col-span-2">
          <CardHeader><CardTitle>Change password</CardTitle></CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5 sm:col-span-2">
              <Label htmlFor="current">Current password</Label>
              <Input id="current" type="password" placeholder="••••••••" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="new">New password</Label>
              <Input id="new" type="password" placeholder="••••••••" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="confirm">Confirm</Label>
              <Input id="confirm" type="password" placeholder="••••••••" />
            </div>
            <div className="sm:col-span-2">
              <Button>Update password</Button>
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
