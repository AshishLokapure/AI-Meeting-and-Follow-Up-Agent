import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const statusStyle: Record<string, string> = {
  pending: "bg-muted text-foreground border-border",
  in_progress: "bg-primary/10 text-primary border-primary/20",
  completed: "bg-success/10 text-success border-success/20",
  overdue: "bg-destructive/10 text-destructive border-destructive/20",
  blocked: "bg-warning/15 text-warning border-warning/30",
  cancelled: "bg-muted text-muted-foreground border-border",
};

const statusLabel: Record<string, string> = {
  pending: "Pending",
  in_progress: "In progress",
  completed: "Completed",
  overdue: "Overdue",
  blocked: "Blocked",
  cancelled: "Cancelled",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "rounded-full font-medium",
        statusStyle[status] ?? "bg-muted text-muted-foreground border-border",
      )}
    >
      {statusLabel[status] ?? status.replaceAll("_", " ")}
    </Badge>
  );
}

const priorityStyle: Record<string, string> = {
  low: "bg-muted text-muted-foreground border-border",
  medium: "bg-primary/10 text-primary border-primary/20",
  high: "bg-warning/15 text-warning border-warning/30",
  urgent: "bg-destructive/10 text-destructive border-destructive/20",
  critical: "bg-destructive/10 text-destructive border-destructive/20",
};

export function PriorityBadge({ priority }: { priority: string }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "rounded-full capitalize",
        priorityStyle[priority] ?? "bg-muted text-muted-foreground border-border",
      )}
    >
      {priority}
    </Badge>
  );
}

const meetingStatusStyle: Record<string, string> = {
  uploaded: "bg-muted text-muted-foreground border-border",
  queued: "bg-muted text-muted-foreground border-border",
  processing: "bg-primary/10 text-primary border-primary/20",
  transcribed: "bg-primary/10 text-primary border-primary/20",
  summarized: "bg-primary/10 text-primary border-primary/20",
  analyzed: "bg-success/10 text-success border-success/20",
  processed: "bg-success/10 text-success border-success/20",
  archived: "bg-muted text-muted-foreground border-border",
  scheduled: "bg-muted text-muted-foreground border-border",
  failed: "bg-destructive/10 text-destructive border-destructive/20",
};

export function MeetingStatusBadge({ status }: { status: string }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "rounded-full capitalize",
        meetingStatusStyle[status] ?? "bg-muted text-muted-foreground border-border",
      )}
    >
      {status.replaceAll("_", " ")}
    </Badge>
  );
}
