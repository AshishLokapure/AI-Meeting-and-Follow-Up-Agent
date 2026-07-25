import { createFileRoute } from "@tanstack/react-router";
import * as Icons from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { agents } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/_app/agents")({
  head: () => ({
    meta: [
      { title: "AI Agents — Loop" },
      { name: "description", content: "Your autonomous meeting agents and their runtime status." },
    ],
  }),
  component: AgentsPage,
});

const statusTone: Record<string, string> = {
  active: "bg-success/10 text-success border-success/20",
  idle: "bg-muted text-muted-foreground border-border",
  error: "bg-destructive/10 text-destructive border-destructive/20",
};

function AgentsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Agents"
        description="Six specialized agents power your meeting-to-follow-up pipeline"
      />

      <div className="flex items-center gap-2 rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm text-muted-foreground">
        <Icons.Sparkles className="h-4 w-4 text-primary" />
        <span>Demo Mode: Specialized agents are configured and running in the background. Real-time run counts and success logs will show below.</span>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {agents.map((a) => {
          const Icon = (Icons as unknown as Record<string, Icons.LucideIcon>)[a.icon] ?? Icons.Bot;
          return (
            <Card key={a.id} className="rounded-xl shadow-sm">
              <CardContent className="flex h-full flex-col gap-4 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary/10 text-primary">
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="truncate text-sm font-semibold">{a.name}</h3>
                      <p className="text-xs text-muted-foreground">Last run · {a.lastRun}</p>
                    </div>
                  </div>
                  <Badge variant="outline" className={cn("rounded-full capitalize", statusTone[a.status])}>
                    {a.status}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{a.description}</p>
                <div>
                  <div className="mb-1 flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">Accuracy</span>
                    <span className="font-semibold">{a.successRate}%</span>
                  </div>
                  <Progress value={a.successRate} className="h-1.5" />
                </div>
                <div className="mt-auto flex items-center justify-between border-t pt-3">
                  <span className="text-xs text-muted-foreground">{a.runsToday} runs today</span>
                  <Button variant="ghost" size="sm">View logs</Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
