import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Search, MoreHorizontal, Plus, Sparkles, Upload } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { PriorityBadge, StatusBadge } from "@/components/app/badges";
import { useTasks, useUpdateTaskStatus, useUserProfile } from "@/lib/services";
import { tasks as mockTasks } from "@/lib/mock-data";
import { getAuthSession } from "@/lib/auth";
import { toast } from "sonner";

export const Route = createFileRoute("/_app/tasks")({
  head: () => ({
    meta: [
      { title: "Tasks — Loop" },
      { name: "description", content: "Track every action item extracted from your meetings." },
    ],
  }),
  component: TasksPage,
});

function initials(n: string) {
  return n.split(" ").map((x) => x[0]).join("");
}

const PAGE_SIZE = 6;

function TasksPage() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("all");
  const [priority, setPriority] = useState("all");
  const [page, setPage] = useState(1);

  // Fetch real user & tasks
  const { data: userProfile } = useUserProfile();
  const session = getAuthSession();
  const userName = userProfile?.name || session?.user?.name || "User";

  const { data: tasksData, isLoading } = useTasks(
    status !== "all" ? status : undefined,
    priority !== "all" ? priority : undefined,
    q || undefined
  );

  const updateStatusMutation = useUpdateTaskStatus();

  const realTasks = tasksData?.tasks ?? [];
  const hasRealTasks = realTasks.length > 0;

  // Fallback to mock data if there are no real tasks
  const tasksToRender = hasRealTasks
    ? realTasks
    : mockTasks
        .filter((t) => (status === "all" ? true : t.status === status))
        .filter((t) => (priority === "all" ? true : t.priority === priority))
        .filter((t) => t.title.toLowerCase().includes(q.toLowerCase()));

  const pageCount = Math.max(1, Math.ceil(tasksToRender.length / PAGE_SIZE));
  const current = tasksToRender.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const handleMarkComplete = (taskId: string) => {
    // If it's a mock task, we just show a success toast
    if (!hasRealTasks) {
      toast.success("Task marked complete (Demo mode)");
      return;
    }

    updateStatusMutation.mutate(
      { id: taskId, status: "completed" },
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

  return (
    <div className="space-y-6">
      {!hasRealTasks && !isLoading && (
        <div className="flex flex-col gap-4 rounded-xl border border-primary/20 bg-primary/5 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2 font-semibold text-primary">
              <Sparkles className="h-4 w-4" /> Demo Mode Enabled
            </div>
            <p className="text-sm text-muted-foreground">
              Showing sample tasks. Real tasks will be extracted automatically from meetings after you upload a meeting recording.
            </p>
          </div>
          <Button asChild className="w-fit shrink-0">
            <Link to="/upload">
              <Upload className="mr-2 h-4 w-4" /> Upload a meeting
            </Link>
          </Button>
        </div>
      )}

      <PageHeader
        title="Tasks"
        description={`${tasksToRender.length} action items tracked`}
        actions={
          <Button><Plus className="mr-2 h-4 w-4" /> New task</Button>
        }
      />

      <div className="flex flex-wrap items-center gap-2">
        <div className="relative min-w-0 flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search tasks" value={q} onChange={(e) => setQ(e.target.value)} className="pl-9" />
        </div>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="in_progress">In progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="overdue">Overdue</SelectItem>
          </SelectContent>
        </Select>
        <Select value={priority} onValueChange={setPriority}>
          <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All priorities</SelectItem>
            <SelectItem value="urgent">Urgent</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="flex h-60 items-center justify-center">
          <p className="text-muted-foreground animate-pulse">Loading tasks...</p>
        </div>
      ) : (
        <Card className="rounded-xl shadow-sm">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Task</TableHead>
                  <TableHead>Owner</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Deadline</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Meeting</TableHead>
                  <TableHead className="w-10" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {current.map((t: any) => {
                  const ownerName = t.owner?.name || userName;
                  const deadline = t.deadline || (t.due_date ? new Date(t.due_date).toLocaleDateString() : "No deadline");
                  const meetingTitle = t.meetingTitle || "General Meeting";
                  return (
                    <TableRow key={t.id}>
                      <TableCell className="max-w-[280px]">
                        <Link
                          to="/tasks/$taskId"
                          params={{ taskId: t.id }}
                          className="line-clamp-1 font-semibold hover:underline"
                        >
                          {t.title}
                        </Link>
                        <p className="line-clamp-1 text-xs text-muted-foreground">{t.description || "No description."}</p>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Avatar className="h-7 w-7">
                            <AvatarFallback className="bg-primary/10 text-[10px] font-semibold text-primary">
                              {initials(ownerName)}
                            </AvatarFallback>
                          </Avatar>
                          <span className="text-sm">{ownerName}</span>
                        </div>
                      </TableCell>
                      <TableCell><PriorityBadge priority={t.priority} /></TableCell>
                      <TableCell className="text-sm text-muted-foreground">{deadline}</TableCell>
                      <TableCell><StatusBadge status={t.status} /></TableCell>
                      <TableCell className="max-w-[200px]">
                        <span className="line-clamp-1 text-sm text-muted-foreground">{meetingTitle}</span>
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon"><MoreHorizontal className="h-4 w-4" /></Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleMarkComplete(t.id)}>
                              Mark complete
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => toast.info("Reminder sent (Demo mode)")}>
                              Send reminder
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  );
                })}
                {current.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} className="py-10 text-center text-sm text-muted-foreground">
                      No tasks match your filters.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </Card>
      )}

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          Page {page} of {pageCount}
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
            Previous
          </Button>
          <Button variant="outline" size="sm" disabled={page === pageCount} onClick={() => setPage((p) => p + 1)}>
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
