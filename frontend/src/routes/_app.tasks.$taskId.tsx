import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, Bell, CheckCircle2, Clock, Send, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { PriorityBadge, StatusBadge } from "@/components/app/badges";
import { useTask, useUpdateTaskStatus, useUserProfile } from "@/lib/services";
import { tasks as mockTasks } from "@/lib/mock-data";
import { getAuthSession } from "@/lib/auth";
import { toast } from "sonner";

export const Route = createFileRoute("/_app/tasks/$taskId")({
  head: () => ({ meta: [{ title: "Task — Loop" }] }),
  component: TaskDetail,
});

function initials(n: string) {
  return n.split(" ").map((x) => x[0]).join("");
}

function TaskDetail() {
  const { taskId } = Route.useParams();

  // Queries
  const { data: realTask, isLoading } = useTask(taskId);
  const { data: userProfile } = useUserProfile();
  const session = getAuthSession();
  const userName = userProfile?.name || session?.user?.name || "User";
  const userEmail = userProfile?.email || session?.user?.email || "you@company.com";

  const updateStatusMutation = useUpdateTaskStatus();

  // Fallback to mock data if task isn't found in real database
  const isMock = !realTask && !isLoading;
  const task = realTask || mockTasks.find((t) => t.id === taskId);

  if (isLoading) {
    return (
      <div className="flex h-60 items-center justify-center">
        <p className="text-muted-foreground animate-pulse">Loading task details...</p>
      </div>
    );
  }

  if (!task) throw notFound();

  const handleMarkComplete = () => {
    if (isMock) {
      toast.success("Task marked complete (Demo mode)");
      return;
    }

    updateStatusMutation.mutate(
      { id: task.id, status: "completed" },
      {
        onSuccess: () => {
          toast.success("Task marked complete");
        },
        onError: (err) => {
          toast.error(`Error completing task: ${err.message}`);
        },
      }
    );
  };

  const ownerName = (task as any).owner?.name || userName;
  const ownerEmail = (task as any).owner?.email || userEmail;
  const deadline = task.deadline || (task.due_date ? new Date(task.due_date).toLocaleDateString() : "No deadline");
  const meetingTitle = (task as any).meetingTitle || "Source Meeting";
  const meetingId = (task as any).meetingId || task.meeting_id;
  const createdAt = (task as any).createdAt || (task.created_at ? new Date(task.created_at).toLocaleDateString() : "Recently");

  const activity = [
    { icon: CheckCircle2, tone: "text-success", text: "Task extracted from meeting", time: createdAt },
    { icon: Send, tone: "text-primary", text: `Assigned to ${ownerName}`, time: createdAt },
    { icon: Bell, tone: "text-warning", text: `Reminder sent (${(task as any).remindersSent || 0})`, time: "Scheduled" },
    { icon: Clock, tone: "text-muted-foreground", text: `Deadline set for ${deadline}`, time: createdAt },
  ];

  return (
    <div className="space-y-6">
      {isMock && (
        <div className="flex items-center gap-2 rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm text-muted-foreground">
          <Sparkles className="h-4 w-4 text-primary" />
          <span>Showing sample task details. Real tasks support live status updates via the API.</span>
        </div>
      )}

      <Button variant="ghost" size="sm" asChild className="-ml-2">
        <Link to="/tasks"><ArrowLeft className="mr-1 h-4 w-4" /> Back to tasks</Link>
      </Button>

      <PageHeader
        title={task.title}
        description={task.description || "No description provided."}
        actions={
          <>
            <Button variant="outline" onClick={() => toast.info("Reminder sent (Demo mode)")}>
              <Bell className="mr-2 h-4 w-4" /> Send reminder
            </Button>
            <Button onClick={handleMarkComplete}>
              <CheckCircle2 className="mr-2 h-4 w-4" /> Mark complete
            </Button>
          </>
        }
      />

      <div className="flex flex-wrap items-center gap-2">
        <PriorityBadge priority={task.priority} />
        <StatusBadge status={task.status} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Activity</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {activity.map((a, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className={`grid h-8 w-8 shrink-0 place-items-center rounded-full bg-muted ${a.tone}`}>
                    <a.icon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{a.text}</p>
                    <p className="text-xs text-muted-foreground">{a.time}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Reminder history</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {[1].map((i) => (
                <div key={i} className="flex items-center gap-3 rounded-lg border border-border/60 p-3">
                  <Bell className="h-4 w-4 text-warning" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold">Reminder #{i} sent via Email</p>
                    <p className="text-xs text-muted-foreground">Auto-triggered by agent</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Owner</CardTitle></CardHeader>
            <CardContent className="flex items-center gap-3">
              <Avatar className="h-10 w-10">
                <AvatarFallback className="bg-primary/10 text-sm font-semibold text-primary">
                  {initials(ownerName)}
                </AvatarFallback>
              </Avatar>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold">{ownerName}</p>
                <p className="truncate text-xs text-muted-foreground">{ownerEmail}</p>
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Source meeting</CardTitle></CardHeader>
            <CardContent>
              {meetingId ? (
                <Link
                  to="/meetings/$meetingId"
                  params={{ meetingId }}
                  className="text-sm font-semibold text-primary hover:underline"
                >
                  {meetingTitle}
                </Link>
              ) : (
                <span className="text-sm font-semibold text-muted-foreground">{meetingTitle}</span>
              )}
              <p className="mt-1 text-xs text-muted-foreground">Extracted {createdAt}</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
