import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, Bell, CheckCircle2, Clock, Send } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { PriorityBadge, StatusBadge } from "@/components/app/badges";
import { tasks } from "@/lib/mock-data";

export const Route = createFileRoute("/_app/tasks/$taskId")({
  head: () => ({ meta: [{ title: "Task — Loop" }] }),
  component: TaskDetail,
});

function initials(n: string) {
  return n.split(" ").map((x) => x[0]).join("");
}

function TaskDetail() {
  const { taskId } = Route.useParams();
  const task = tasks.find((t) => t.id === taskId);
  if (!task) throw notFound();

  const activity = [
    { icon: CheckCircle2, tone: "text-success", text: "Task extracted from meeting", time: task.createdAt },
    { icon: Send, tone: "text-primary", text: `Assigned to ${task.owner.name}`, time: task.createdAt },
    { icon: Bell, tone: "text-warning", text: `Reminder sent (${task.remindersSent})`, time: "2h ago" },
    { icon: Clock, tone: "text-muted-foreground", text: `Deadline set for ${task.deadline}`, time: task.createdAt },
  ];

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" asChild className="-ml-2">
        <Link to="/tasks"><ArrowLeft className="mr-1 h-4 w-4" /> Back to tasks</Link>
      </Button>

      <PageHeader
        title={task.title}
        description={task.description}
        actions={
          <>
            <Button variant="outline"><Bell className="mr-2 h-4 w-4" /> Send reminder</Button>
            <Button><CheckCircle2 className="mr-2 h-4 w-4" /> Mark complete</Button>
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
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-3 rounded-lg border border-border/60 p-3">
                  <Bell className="h-4 w-4 text-warning" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold">Reminder #{i} sent via Email</p>
                    <p className="text-xs text-muted-foreground">{i} day{i > 1 ? "s" : ""} ago</p>
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
                  {initials(task.owner.name)}
                </AvatarFallback>
              </Avatar>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold">{task.owner.name}</p>
                <p className="truncate text-xs text-muted-foreground">{task.owner.email}</p>
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Source meeting</CardTitle></CardHeader>
            <CardContent>
              <Link
                to="/meetings/$meetingId"
                params={{ meetingId: task.meetingId }}
                className="text-sm font-semibold text-primary hover:underline"
              >
                {task.meetingTitle}
              </Link>
              <p className="mt-1 text-xs text-muted-foreground">Extracted {task.createdAt}</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
