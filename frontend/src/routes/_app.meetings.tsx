import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Upload, Search, Video, Users, Clock } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { MeetingStatusBadge } from "@/components/app/badges";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { meetings } from "@/lib/mock-data";
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

  const filtered = meetings
    .filter((m) => (status === "all" ? true : m.status === status))
    .filter((m) => m.title.toLowerCase().includes(q.toLowerCase()))
    .sort((a, b) => {
      if (sort === "duration") return b.duration - a.duration;
      return new Date(b.date).getTime() - new Date(a.date).getTime();
    });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Meetings"
        description={`${meetings.length} meetings tracked by your workspace`}
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
            <SelectItem value="scheduled">Scheduled</SelectItem>
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

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {filtered.map((m) => (
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
                    {format(new Date(m.date), "MMM d, yyyy · h:mm a")}
                  </p>
                </div>
                <p className="line-clamp-3 text-sm text-muted-foreground">{m.summary}</p>
                <div className="mt-auto flex items-center justify-between gap-2 pt-2">
                  <div className="flex -space-x-2">
                    {m.participants.slice(0, 4).map((p) => (
                      <Avatar key={p.id} className="h-7 w-7 border-2 border-background">
                        <AvatarFallback className="bg-muted text-[10px] font-semibold">
                          {initials(p.name)}
                        </AvatarFallback>
                      </Avatar>
                    ))}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" />{m.participants.length}</span>
                    <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{m.duration}m</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
