import type { LucideIcon } from "lucide-react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  delta?: { value: string; positive?: boolean };
  hint?: string;
  tone?: "primary" | "success" | "warning" | "danger";
}

const toneMap: Record<NonNullable<KpiCardProps["tone"]>, string> = {
  primary: "bg-primary/10 text-primary",
  success: "bg-success/10 text-success",
  warning: "bg-warning/10 text-warning",
  danger: "bg-destructive/10 text-destructive",
};

export function KpiCard({ label, value, icon: Icon, delta, hint, tone = "primary" }: KpiCardProps) {
  return (
    <Card className="rounded-xl border-border/70 shadow-sm">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {label}
            </p>
            <p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>
            {hint ? <p className="mt-1 text-xs text-muted-foreground">{hint}</p> : null}
          </div>
          <div className={cn("grid h-11 w-11 shrink-0 place-items-center rounded-xl", toneMap[tone])}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
        {delta ? (
          <div className="mt-4 flex items-center gap-1 text-xs font-medium">
            {delta.positive ? (
              <ArrowUpRight className="h-3.5 w-3.5 text-success" />
            ) : (
              <ArrowDownRight className="h-3.5 w-3.5 text-destructive" />
            )}
            <span className={delta.positive ? "text-success" : "text-destructive"}>
              {delta.value}
            </span>
            <span className="text-muted-foreground">vs last week</span>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
