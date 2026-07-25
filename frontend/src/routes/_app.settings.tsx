import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/app/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/_app/settings")({
  head: () => ({ meta: [{ title: "Settings — Loop" }] }),
  component: SettingsPage,
});

function SettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Settings" description="Configure your workspace" />

      <Tabs defaultValue="general">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="mt-4">
          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Workspace</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label>Workspace name</Label>
                <Input defaultValue="Acme Inc." />
              </div>
              <div className="space-y-1.5">
                <Label>Language</Label>
                <Select defaultValue="en">
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Spanish</SelectItem>
                    <SelectItem value="fr">French</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="sm:col-span-2"><Button>Save</Button></div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="appearance" className="mt-4">
          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Appearance</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Compact mode</p>
                  <p className="text-xs text-muted-foreground">Reduce spacing across the UI</p>
                </div>
                <Switch />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Reduce animations</p>
                  <p className="text-xs text-muted-foreground">Minimize motion effects</p>
                </div>
                <Switch />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="mt-4">
          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Reminder cadence</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label>Reminder frequency</Label>
                <Select defaultValue="daily">
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hourly">Hourly</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Escalate after</Label>
                <Select defaultValue="2">
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 missed reminder</SelectItem>
                    <SelectItem value="2">2 missed reminders</SelectItem>
                    <SelectItem value="3">3 missed reminders</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="mt-4">
          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Security</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Two-factor authentication</p>
                  <p className="text-xs text-muted-foreground">Require a second factor on login</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">SSO (SAML)</p>
                  <p className="text-xs text-muted-foreground">Enterprise plan required</p>
                </div>
                <Badge variant="outline" className="rounded-full">Enterprise</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api" className="mt-4">
          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>API keys</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2 rounded-lg border border-border/60 p-3">
                <code className="min-w-0 flex-1 truncate text-xs text-muted-foreground">
                  sk_live_••••••••••••••••••••3f2a
                </code>
                <Button variant="outline" size="sm">Reveal</Button>
                <Button variant="outline" size="sm">Rotate</Button>
              </div>
              <Button>Generate new key</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
