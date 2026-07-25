import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Video,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Upload,
  Plus,
  CalendarDays,
  ArrowRight,
  Bot,
  Sparkles,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { PageHeader } from "@/components/app/page-header";
import { KpiCard } from "@/components/app/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { StatusBadge, PriorityBadge } from "@/components/app/badges";
import {
  tasks,
  meetings,
  meetingTrends,
  completionTrend,
  priorityBreakdown,
} from "@/lib/mock-data";

export const Route = createFileRoute("/_app/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — Loop" },
      { name: "description", content: "Track meetings, tasks, and follow-ups at a glance." },
    ],
  }),
  component: DashboardPage,
});

function initials(name: string) {
  return name.split(" ").map((n) => n[0]).join("");
}

function DashboardPage() {
  const upcoming = tasks.filter((t) => t.status !== "completed").slice(0, 5);
  const recent = tasks.slice(0, 5);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Good morning, Alex"
        description="Here's what your meetings and agents are up to today."
        actions={
          <>
            <Button asChild variant="outline">
              <Link to="/meetings">
                <CalendarDays className="mr-2 h-4 w-4" /> View meetings
              </Link>
            </Button>
            <Button asChild>
              <Link to="/upload">
                <Upload className="mr-2 h-4 w-4" /> Upload meeting
              </Link>
            </Button>
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Total meetings" value={128} icon={Video} tone="primary" delta={{ value: "+12%", positive: true }} />
        <KpiCard label="Completed tasks" value={342} icon={CheckCircle2} tone="success" delta={{ value: "+8%", positive: true }} />
        <KpiCard label="Pending tasks" value={47} icon={Clock} tone="warning" delta={{ value: "-4%", positive: true }} />
        <KpiCard label="Overdue tasks" value={9} icon={AlertTriangle} tone="danger" delta={{ value: "+2", positive: false }} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2 rounded-xl shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Meeting activity</CardTitle>
              <p className="text-sm text-muted-foreground">Meetings processed and tasks extracted</p>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/analytics">
                Analytics <ArrowRight className="ml-1 h-3.5 w-3.5" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={meetingTrends}>
                <defs>
                  <linearGradient id="m1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="t1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-success)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="var(--color-success)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="week" stroke="var(--color-muted-foreground)" fontSize={12} />
                <YAxis stroke="var(--color-muted-foreground)" fontSize={12} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid var(--color-border)" }} />
                <Area type="monotone" dataKey="meetings" stroke="var(--color-primary)" fill="url(#m1)" strokeWidth={2} />
                <Area type="monotone" dataKey="tasks" stroke="var(--color-success)" fill="url(#t1)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="rounded-xl shadow-sm">
          <CardHeader>
            <CardTitle>Priority breakdown</CardTitle>
            <p className="text-sm text-muted-foreground">Open tasks by priority</p>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={priorityBreakdown} dataKey="value" innerRadius={55} outerRadius={85} paddingAngle={2}>
                  {priorityBreakdown.map((d) => (
                    <Cell key={d.name} fill={d.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid var(--color-border)" }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
              {priorityBreakdown.map((d) => (
                <div key={d.name} className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                  <span className="text-muted-foreground">{d.name}</span>
                  <span className="ml-auto font-semibold">{d.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2 rounded-xl shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Upcoming deadlines</CardTitle>
              <p className="text-sm text-muted-foreground">Tasks the reminder agent is watching</p>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/tasks">
                View all <ArrowRight className="ml-1 h-3.5 w-3.5" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {upcoming.map((task) => (
              <Link
                key={task.id}
                to="/tasks/$taskId"
                params={{ taskId: task.id }}
                className="flex items-center gap-3 rounded-lg border border-border/60 p-3 transition-colors hover:bg-muted/40"
              >
                <Avatar className="h-9 w-9 shrink-0">
                  <AvatarFallback className="bg-primary/10 text-xs font-semibold text-primary">
                    {initials(task.owner.name)}
                  </AvatarFallback>
                </Avatar>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold">{task.title}</p>
                  <p className="truncate text-xs text-muted-foreground">
                    {task.owner.name} · Due {task.deadline}
                  </p>
                </div>
                <div className="hidden shrink-0 items-center gap-2 sm:flex">
                  <PriorityBadge priority={task.priority} />
                  <StatusBadge status={task.status} />
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>

        <Card className="rounded-xl shadow-sm">
          <CardHeader>
            <CardTitle>Quick actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button asChild variant="outline" className="w-full justify-start">
              <Link to="/upload">
                <Upload className="mr-2 h-4 w-4" /> Upload a recording
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full justify-start">
              <Link to="/tasks">
                <Plus className="mr-2 h-4 w-4" /> Create a task
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full justify-start">
              <Link to="/agents">
                <Bot className="mr-2 h-4 w-4" /> Manage AI agents
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full justify-start">
              <Link to="/calendar">
                <CalendarDays className="mr-2 h-4 w-4" /> Open calendar
              </Link>
            </Button>

            <div className="mt-4 rounded-xl border border-primary/20 bg-primary/5 p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-primary">
                <Sparkles className="h-4 w-4" /> AI accuracy this week
              </div>
              <p className="mt-1 text-2xl font-bold">97.8%</p>
              <Progress value={97.8} className="mt-2 h-1.5" />
              <p className="mt-1 text-xs text-muted-foreground">
                Across 128 processed meetings
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="rounded-xl shadow-sm">
          <CardHeader>
            <CardTitle>Task completion</CardTitle>
            <p className="text-sm text-muted-foreground">Completed vs. still pending this week</p>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={completionTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="day" stroke="var(--color-muted-foreground)" fontSize={12} />
                <YAxis stroke="var(--color-muted-foreground)" fontSize={12} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid var(--color-border)" }} />
                <Bar dataKey="completed" fill="var(--color-success)" radius={[6, 6, 0, 0]} />
                <Bar dataKey="pending" fill="var(--color-warning)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="rounded-xl shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent meetings</CardTitle>
              <p className="text-sm text-muted-foreground">Latest processed conversations</p>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/meetings">
                All meetings <ArrowRight className="ml-1 h-3.5 w-3.5" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {meetings.slice(0, 4).map((m) => (
              <Link
                key={m.id}
                to="/meetings/$meetingId"
                params={{ meetingId: m.id }}
                className="flex items-center gap-3 rounded-lg border border-border/60 p-3 transition-colors hover:bg-muted/40"
              >
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary">
                  <Video className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold">{m.title}</p>
                  <p className="truncate text-xs text-muted-foreground">
                    {m.participants.length} participants · {m.duration} min · {m.actionItems} action items
                  </p>
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-xl shadow-sm">
        <CardHeader>
          <CardTitle>Recent tasks</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {recent.map((t) => (
            <div
              key={t.id}
              className="flex flex-wrap items-center gap-3 rounded-lg border border-border/60 p-3"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold">{t.title}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {t.meetingTitle} · {t.owner.name}
                </p>
              </div>
              <PriorityBadge priority={t.priority} />
              <StatusBadge status={t.status} />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
