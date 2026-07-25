import { createFileRoute } from "@tanstack/react-router";
import { Bell, CheckCircle2, AlertTriangle, UserPlus, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { notifications } from "@/lib/mock-data";
import type { Notification } from "@/lib/mock-data";
import { format } from "date-fns";

export const Route = createFileRoute("/_app/notifications")({
  head: () => ({
    meta: [
      { title: "Notifications — Loop" },
      { name: "description", content: "Follow-ups, reminders, and escalations from your agents." },
    ],
  }),
  component: NotificationsPage,
});

const iconFor: Record<Notification["type"], { icon: typeof Bell; tone: string }> = {
  reminder: { icon: Bell, tone: "bg-warning/15 text-warning" },
  escalation: { icon: AlertTriangle, tone: "bg-destructive/10 text-destructive" },
  assignment: { icon: UserPlus, tone: "bg-primary/10 text-primary" },
  completion: { icon: CheckCircle2, tone: "bg-success/10 text-success" },
};

function NotificationRow({ n }: { n: Notification }) {
  const { icon: Icon, tone } = iconFor[n.type];
  return (
    <div className="flex items-start gap-3 rounded-lg border border-border/60 p-3">
      <div className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg ${tone}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-sm font-semibold">{n.title}</p>
          <Badge variant="outline" className="rounded-full capitalize">{n.status}</Badge>
        </div>
        <p className="mt-0.5 truncate text-sm text-muted-foreground">{n.message}</p>
        <p className="mt-1 text-xs text-muted-foreground">
          {n.recipient} · {format(new Date(n.timestamp), "MMM d, h:mm a")}
        </p>
      </div>
    </div>
  );
}

function NotificationsPage() {
  const sent = notifications.filter((n) => n.status === "sent");
  const scheduled = notifications.filter((n) => n.status === "scheduled");

  return (
    <div className="space-y-6">
      <PageHeader
        title="Notifications"
        description="Follow-ups your reminder and escalation agents have sent"
      />

      <div className="flex items-center gap-2 rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm text-muted-foreground">
        <Sparkles className="h-4 w-4 text-primary" />
        <span>Demo Mode: Shows sample notification logs. Auto-generated notifications and email/Slack follow-up alerts will be logged as tasks approach their deadlines.</span>
      </div>

      <Card className="rounded-xl shadow-sm">
        <CardHeader><CardTitle>Feed</CardTitle></CardHeader>
        <CardContent>
          <Tabs defaultValue="all">
            <TabsList>
              <TabsTrigger value="all">All ({notifications.length})</TabsTrigger>
              <TabsTrigger value="sent">Sent ({sent.length})</TabsTrigger>
              <TabsTrigger value="scheduled">Upcoming ({scheduled.length})</TabsTrigger>
            </TabsList>
            <TabsContent value="all" className="mt-4 space-y-2">
              {notifications.map((n) => <NotificationRow key={n.id} n={n} />)}
            </TabsContent>
            <TabsContent value="sent" className="mt-4 space-y-2">
              {sent.map((n) => <NotificationRow key={n.id} n={n} />)}
            </TabsContent>
            <TabsContent value="scheduled" className="mt-4 space-y-2">
              {scheduled.map((n) => <NotificationRow key={n.id} n={n} />)}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
