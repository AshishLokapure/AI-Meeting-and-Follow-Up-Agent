import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Priority, TaskStatus, MeetingStatus } from "@/lib/mock-data";

const statusStyle: Record<TaskStatus, string> = {
  pending: "bg-muted text-foreground border-border",
  in_progress: "bg-primary/10 text-primary border-primary/20",
  completed: "bg-success/10 text-success border-success/20",
  overdue: "bg-destructive/10 text-destructive border-destructive/20",
};

const statusLabel: Record<TaskStatus, string> = {
  pending: "Pending",
  in_progress: "In progress",
  completed: "Completed",
  overdue: "Overdue",
};

export function StatusBadge({ status }: { status: TaskStatus }) {
  return (
    <Badge variant="outline" className={cn("rounded-full font-medium", statusStyle[status])}>
      {statusLabel[status]}
    </Badge>
  );
}

const priorityStyle: Record<Priority, string> = {
  low: "bg-muted text-muted-foreground border-border",
  medium: "bg-primary/10 text-primary border-primary/20",
  high: "bg-warning/15 text-warning border-warning/30",
  urgent: "bg-destructive/10 text-destructive border-destructive/20",
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <Badge variant="outline" className={cn("rounded-full capitalize", priorityStyle[priority])}>
      {priority}
    </Badge>
  );
}

const meetingStatusStyle: Record<MeetingStatus, string> = {
  processed: "bg-success/10 text-success border-success/20",
  processing: "bg-primary/10 text-primary border-primary/20",
  scheduled: "bg-muted text-muted-foreground border-border",
  failed: "bg-destructive/10 text-destructive border-destructive/20",
};

export function MeetingStatusBadge({ status }: { status: MeetingStatus }) {
  return (
    <Badge variant="outline" className={cn("rounded-full capitalize", meetingStatusStyle[status])}>
      {status}
    </Badge>
  );
}
