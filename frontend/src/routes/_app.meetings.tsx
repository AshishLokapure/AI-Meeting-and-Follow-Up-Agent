import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Upload, Search, Video, Users, Clock, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { MeetingStatusBadge } from "@/components/app/badges";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useMeetings } from "@/lib/services";
import { meetings as mockMeetings } from "@/lib/mock-data";
import { format } from "date-fns";

export const Route = createFileRoute("/_app/meetings")({
  head: () => ({
    meta: [
      { title: "Meetings — Loop" },
      { name: "description", content: "Browse and search processed meetings." },
    ],
  }),
  component: MeetingsPage,
});

function initials(n: string) {
  return n.split(" ").map((x) => x[0]).join("");
}

function MeetingsPage() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<string>("all");
  const [sort, setSort] = useState<string>("recent");

  // Fetch from real API
  const { data, isLoading } = useMeetings(status !== "all" ? status : undefined, q || undefined);

  const realMeetings = data?.meetings ?? [];
  const hasRealMeetings = realMeetings.length > 0;

  // Fallback to mock data if there are no real meetings in the database
  const meetingsToRender = hasRealMeetings
    ? realMeetings
    : mockMeetings
        .filter((m) => (status === "all" ? true : m.status === status))
        .filter((m) => m.title.toLowerCase().includes(q.toLowerCase()));

  // Sort them
  const sortedMeetings = [...meetingsToRender].sort((a: any, b: any) => {
    const aDuration = a.duration_minutes !== undefined ? a.duration_minutes : (a.duration ?? 0);
    const bDuration = b.duration_minutes !== undefined ? b.duration_minutes : (b.duration ?? 0);

    const aDate = a.meeting_date || a.created_at || a.date;
    const bDate = b.meeting_date || b.created_at || b.date;

    if (sort === "duration") return bDuration - aDuration;
    return new Date(bDate).getTime() - new Date(aDate).getTime();
  });

  return (
    <div className="space-y-6">
      {!hasRealMeetings && !isLoading && (
        <div className="flex flex-col gap-4 rounded-xl border border-primary/20 bg-primary/5 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2 font-semibold text-primary">
              <Sparkles className="h-4 w-4" /> Demo Mode Enabled
            </div>
            <p className="text-sm text-muted-foreground">
              Showing sample meetings. Upload a meeting recording file to see real meetings processed by your AI agents.
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
        title="Meetings"
        description={`${meetingsToRender.length} meetings tracked by your workspace`}
        actions={
          <Button asChild>
            <Link to="/upload">
              <Upload className="mr-2 h-4 w-4" /> Upload meeting
            </Link>
          </Button>
        }
      />

      <div className="flex flex-wrap items-center gap-2">
        <div className="relative min-w-0 flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search meetings"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="processed">Processed</SelectItem>
            <SelectItem value="processing">Processing</SelectItem>
            <SelectItem value="uploaded">Uploaded</SelectItem>
            <SelectItem value="transcribed">Transcribed</SelectItem>
            <SelectItem value="summarized">Summarized</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sort} onValueChange={setSort}>
          <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="recent">Most recent</SelectItem>
            <SelectItem value="duration">Longest first</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="flex h-60 items-center justify-center">
          <p className="text-muted-foreground animate-pulse">Loading meetings...</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {sortedMeetings.map((m: any) => {
            const date = m.meeting_date || m.created_at || m.date;
            const duration = m.duration_minutes !== undefined ? m.duration_minutes : (m.duration ?? 0);
            const actionItemsCount = m.action_items_count !== undefined ? m.action_items_count : (m.actionItems ?? 0);
            const summary = m.summary_text || m.summary || "No summary available yet.";
            const participantsList = m.participants ?? [];

            return (
              <Link
                key={m.id}
                to="/meetings/$meetingId"
                params={{ meetingId: m.id }}
                className="group"
              >
                <Card className="h-full rounded-xl border-border/70 shadow-sm transition-shadow group-hover:shadow-md">
                  <CardContent className="flex h-full flex-col gap-4 p-5">
                    <div className="flex items-start justify-between gap-3">
                      <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary">
                        <Video className="h-5 w-5" />
                      </div>
                      <MeetingStatusBadge status={m.status} />
                    </div>
                    <div className="min-w-0">
                      <h3 className="line-clamp-2 text-base font-semibold">{m.title}</h3>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {format(new Date(date), "MMM d, yyyy · h:mm a")}
                      </p>
                    </div>
                    <p className="line-clamp-3 text-sm text-muted-foreground">{summary}</p>
                    <div className="mt-auto flex items-center justify-between gap-2 pt-2">
                      <div className="flex -space-x-2">
                        {participantsList.slice(0, 4).map((p: any) => (
                          <Avatar key={p.id} className="h-7 w-7 border-2 border-background">
                            <AvatarFallback className="bg-muted text-[10px] font-semibold">
                              {initials(p.name)}
                            </AvatarFallback>
                          </Avatar>
                        ))}
                      </div>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" />{participantsList.length}</span>
                        <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{duration}m</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
