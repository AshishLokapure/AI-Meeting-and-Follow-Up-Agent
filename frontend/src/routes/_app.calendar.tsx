import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { PageHeader } from "@/components/app/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Calendar } from "@/components/ui/calendar";
import { meetings, tasks } from "@/lib/mock-data";
import { format, isSameDay } from "date-fns";
import { Video, ListChecks, Sparkles } from "lucide-react";

export const Route = createFileRoute("/_app/calendar")({
  head: () => ({
    meta: [
      { title: "Calendar — Loop" },
      { name: "description", content: "Meetings and task deadlines in one view." },
    ],
  }),
  component: CalendarPage,
});

function CalendarPage() {
  const [date, setDate] = useState<Date | undefined>(new Date("2026-07-25"));

  const dayMeetings = date ? meetings.filter((m) => isSameDay(new Date(m.date), date)) : [];
  const dayTasks = date ? tasks.filter((t) => isSameDay(new Date(t.deadline), date)) : [];

  const meetingDays = meetings.map((m) => new Date(m.date));
  const deadlineDays = tasks.map((t) => new Date(t.deadline));

  return (
    <div className="space-y-6">
      <PageHeader title="Calendar" description="Meetings and deadlines your agents are tracking" />

      <div className="flex items-center gap-2 rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm text-muted-foreground">
        <Sparkles className="h-4 w-4 text-primary" />
        <span>Demo Mode: Shows sample calendar events. Upload real meetings to view active deadlines and upcoming meetings.</span>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="rounded-xl shadow-sm lg:col-span-2">
          <CardContent className="p-4">
            <Calendar
              mode="single"
              selected={date}
              onSelect={setDate}
              modifiers={{ meeting: meetingDays, deadline: deadlineDays }}
              modifiersClassNames={{
                meeting: "relative before:absolute before:bottom-1 before:left-1/2 before:-translate-x-1/2 before:h-1 before:w-1 before:rounded-full before:bg-primary",
                deadline: "relative after:absolute after:bottom-1 after:left-[calc(50%+4px)] after:h-1 after:w-1 after:rounded-full after:bg-warning",
              }}
              className="w-full"
            />
            <div className="mt-4 flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-primary" /> Meetings</span>
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-warning" /> Deadlines</span>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card className="rounded-xl shadow-sm">
            <CardHeader>
              <CardTitle className="text-base">
                {date ? format(date, "EEEE, MMM d") : "Select a date"}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Meetings</h4>
              {dayMeetings.length === 0 && <p className="text-sm text-muted-foreground">No meetings.</p>}
              {dayMeetings.map((m) => (
                <div key={m.id} className="flex items-center gap-2 rounded-lg border border-border/60 p-2">
                  <Video className="h-4 w-4 text-primary" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold">{m.title}</p>
                    <p className="text-xs text-muted-foreground">{format(new Date(m.date), "h:mm a")} · {m.duration}m</p>
                  </div>
                </div>
              ))}

              <h4 className="mt-4 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Deadlines</h4>
              {dayTasks.length === 0 && <p className="text-sm text-muted-foreground">No deadlines.</p>}
              {dayTasks.map((t) => (
                <div key={t.id} className="flex items-center gap-2 rounded-lg border border-border/60 p-2">
                  <ListChecks className="h-4 w-4 text-warning" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold">{t.title}</p>
                    <p className="truncate text-xs text-muted-foreground">{t.owner.name}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
