import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, Download, Share2, Clock, Users } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { MeetingStatusBadge, PriorityBadge, StatusBadge } from "@/components/app/badges";
import { meetings, tasks, decisions, transcriptSample } from "@/lib/mock-data";
import { format } from "date-fns";

export const Route = createFileRoute("/_app/meetings/$meetingId")({
  head: ({ params }) => ({
    meta: [{ title: `Meeting — Loop` }, { name: "description", content: `Meeting ${params.meetingId}` }],
  }),
  component: MeetingDetail,
});

function initials(n: string) {
  return n.split(" ").map((x) => x[0]).join("");
}

function MeetingDetail() {
  const { meetingId } = Route.useParams();
  const meeting = meetings.find((m) => m.id === meetingId);
  if (!meeting) throw notFound();
  const meetingTasks = tasks.filter((t) => t.meetingId === meeting.id);
  const meetingDecisions = decisions.filter((d) => d.meetingId === meeting.id);

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" asChild className="-ml-2">
        <Link to="/meetings"><ArrowLeft className="mr-1 h-4 w-4" /> Back to meetings</Link>
      </Button>

      <PageHeader
        title={meeting.title}
        description={format(new Date(meeting.date), "EEEE, MMMM d, yyyy · h:mm a")}
        actions={
          <>
            <Button variant="outline"><Share2 className="mr-2 h-4 w-4" /> Share</Button>
            <Button><Download className="mr-2 h-4 w-4" /> Download</Button>
          </>
        }
      />

      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <MeetingStatusBadge status={meeting.status} />
        <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{meeting.duration} min</span>
        <span className="flex items-center gap-1"><Users className="h-4 w-4" />{meeting.participants.length} participants</span>
        <Badge variant="outline" className="rounded-full">{meeting.actionItems} action items</Badge>
        <Badge variant="outline" className="rounded-full">{meeting.decisions} decisions</Badge>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Tabs defaultValue="summary">
            <TabsList>
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="transcript">Transcript</TabsTrigger>
              <TabsTrigger value="actions">Action items</TabsTrigger>
              <TabsTrigger value="decisions">Decisions</TabsTrigger>
            </TabsList>
            <TabsContent value="summary" className="mt-4">
              <Card className="rounded-xl shadow-sm">
                <CardContent className="p-6 text-sm leading-relaxed text-foreground">
                  <p>{meeting.summary}</p>
                  <div className="mt-6 space-y-3">
                    <h4 className="text-sm font-semibold">Key topics</h4>
                    <ul className="list-inside list-disc space-y-1 text-muted-foreground">
                      <li>Q4 engineering priorities and capacity trade-offs</li>
                      <li>Enterprise SSO rollout plan</li>
                      <li>Mobile onboarding revamp timeline</li>
                      <li>AI Meeting Agent launch coordination</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="transcript" className="mt-4">
              <Card className="rounded-xl shadow-sm">
                <CardContent className="divide-y p-0">
                  {transcriptSample.map((line, i) => (
                    <div key={i} className="grid grid-cols-[minmax(0,140px)_1fr] gap-4 p-4">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold">{line.speaker}</p>
                        <p className="text-xs text-muted-foreground">{line.time}</p>
                      </div>
                      <p className="text-sm leading-relaxed text-foreground">{line.text}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="actions" className="mt-4 space-y-3">
              {meetingTasks.map((t) => (
                <Card key={t.id} className="rounded-xl shadow-sm">
                  <CardContent className="flex flex-wrap items-center gap-3 p-4">
                    <div className="min-w-0 flex-1">
                      <Link
                        to="/tasks/$taskId"
                        params={{ taskId: t.id }}
                        className="text-sm font-semibold hover:underline"
                      >
                        {t.title}
                      </Link>
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        {t.owner.name} · Due {t.deadline}
                      </p>
                    </div>
                    <PriorityBadge priority={t.priority} />
                    <StatusBadge status={t.status} />
                  </CardContent>
                </Card>
              ))}
            </TabsContent>
            <TabsContent value="decisions" className="mt-4 space-y-3">
              {meetingDecisions.length === 0 ? (
                <p className="text-sm text-muted-foreground">No decisions recorded.</p>
              ) : (
                meetingDecisions.map((d) => (
                  <Card key={d.id} className="rounded-xl shadow-sm">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <h4 className="text-sm font-semibold">{d.title}</h4>
                          <p className="mt-1 text-sm text-muted-foreground">{d.description}</p>
                        </div>
                        <Badge variant="outline" className="shrink-0 rounded-full">{d.timestamp}</Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </TabsContent>
          </Tabs>
        </div>

        <div className="space-y-6">
          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Participants</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {meeting.participants.map((p) => (
                <div key={p.id} className="flex items-center gap-3">
                  <Avatar className="h-9 w-9">
                    <AvatarFallback className="bg-primary/10 text-xs font-semibold text-primary">
                      {initials(p.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold">{p.name}</p>
                    <p className="truncate text-xs text-muted-foreground">{p.role}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Timeline</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {[
                { t: "Uploaded", d: "10:02 AM" },
                { t: "Transcribed", d: "10:04 AM" },
                { t: "Summary generated", d: "10:05 AM" },
                { t: "Tasks extracted", d: "10:06 AM" },
                { t: "Reminders scheduled", d: "10:07 AM" },
              ].map((s, i) => (
                <div key={i} className="flex gap-3">
                  <div className="mt-1 h-2 w-2 shrink-0 rounded-full bg-primary" />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold">{s.t}</p>
                    <p className="text-xs text-muted-foreground">{s.d}</p>
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
