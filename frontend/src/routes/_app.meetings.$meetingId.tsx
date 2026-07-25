import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, Download, Share2, Clock, Users, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { MeetingStatusBadge, PriorityBadge, StatusBadge } from "@/components/app/badges";
import {
  useMeeting,
  useMeetingTranscript,
  useMeetingAnalysis,
  useTasks,
} from "@/lib/services";
import { meetings as mockMeetings, tasks as mockTasks, decisions as mockDecisions, transcriptSample } from "@/lib/mock-data";
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

  // Queries
  const { data: realMeeting, isLoading: isMeetingLoading } = useMeeting(meetingId);
  const { data: transcriptData, isLoading: isTranscriptLoading } = useMeetingTranscript(meetingId);
  const { data: analysisData, isLoading: isAnalysisLoading } = useMeetingAnalysis(meetingId);
  const { data: tasksData } = useTasks();

  const isLoading = isMeetingLoading;

  // Fallback to mock data if meeting isn't found in real database
  const isMock = !realMeeting && !isLoading;
  const meeting = realMeeting || mockMeetings.find((m) => m.id === meetingId);

  if (isLoading) {
    return (
      <div className="flex h-60 items-center justify-center">
        <p className="text-muted-foreground animate-pulse">Loading meeting details...</p>
      </div>
    );
  }

  if (!meeting) {
    throw notFound();
  }

  const date = meeting.meeting_date || meeting.created_at || (meeting as any).date;
  const duration = meeting.duration_minutes !== undefined ? meeting.duration_minutes : ((meeting as any).duration ?? 0);
  const participants = meeting.participants ?? [];

  // Decisions
  let meetingDecisions = [];
  if (isMock) {
    meetingDecisions = mockDecisions.filter((d) => d.meetingId === meeting.id);
  } else {
    // Extract from analysis payload
    meetingDecisions = analysisData?.analysis?.decisions ?? [];
  }

  // Action items
  let meetingTasks = [];
  if (isMock) {
    meetingTasks = mockTasks.filter((t) => t.meetingId === meeting.id);
  } else {
    // Filter real tasks belonging to this meeting
    meetingTasks = tasksData?.tasks.filter((t) => t.meeting_id === meeting.id) ?? [];
  }

  // Summary
  const summaryText = meeting.summary_text || (meeting as any).summary || "No summary generated yet.";

  // Action items count
  const actionItemsCount = meeting.action_items_count !== undefined ? meeting.action_items_count : ((meeting as any).actionItems ?? 0);
  const decisionsCount = meeting.decisions_count !== undefined ? meeting.decisions_count : ((meeting as any).decisions ?? 0);

  return (
    <div className="space-y-6">
      {isMock && (
        <div className="flex items-center gap-2 rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm text-muted-foreground">
          <Sparkles className="h-4 w-4 text-primary" />
          <span>Showing sample meeting details. Real uploaded meetings will display transcript timeline and extracted tasks dynamically.</span>
        </div>
      )}

      <Button variant="ghost" size="sm" asChild className="-ml-2">
        <Link to="/meetings"><ArrowLeft className="mr-1 h-4 w-4" /> Back to meetings</Link>
      </Button>

      <PageHeader
        title={meeting.title}
        description={format(new Date(date), "EEEE, MMMM d, yyyy · h:mm a")}
        actions={
          <>
            <Button variant="outline"><Share2 className="mr-2 h-4 w-4" /> Share</Button>
            <Button><Download className="mr-2 h-4 w-4" /> Download</Button>
          </>
        }
      />

      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <MeetingStatusBadge status={meeting.status} />
        <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{duration} min</span>
        <span className="flex items-center gap-1"><Users className="h-4 w-4" />{participants.length} participants</span>
        <Badge variant="outline" className="rounded-full">{actionItemsCount} action items</Badge>
        <Badge variant="outline" className="rounded-full">{decisionsCount} decisions</Badge>
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
                  <p>{summaryText}</p>
                  {meeting.agenda && (
                    <div className="mt-6 space-y-3">
                      <h4 className="text-sm font-semibold">Agenda</h4>
                      <p className="text-muted-foreground">{meeting.agenda}</p>
                    </div>
                  )}
                  {!meeting.agenda && isMock && (
                    <div className="mt-6 space-y-3">
                      <h4 className="text-sm font-semibold">Key topics</h4>
                      <ul className="list-inside list-disc space-y-1 text-muted-foreground">
                        <li>Q4 engineering priorities and capacity trade-offs</li>
                        <li>Enterprise SSO rollout plan</li>
                        <li>Mobile onboarding revamp timeline</li>
                        <li>AI Meeting Agent launch coordination</li>
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="transcript" className="mt-4">
              <Card className="rounded-xl shadow-sm">
                <CardContent className="divide-y p-0">
                  {isMock ? (
                    transcriptSample.map((line, i) => (
                      <div key={i} className="grid grid-cols-[minmax(0,140px)_1fr] gap-4 p-4">
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold">{line.speaker}</p>
                          <p className="text-xs text-muted-foreground">{line.time}</p>
                        </div>
                        <p className="text-sm leading-relaxed text-foreground">{line.text}</p>
                      </div>
                    ))
                  ) : isTranscriptLoading ? (
                    <p className="p-4 text-sm text-muted-foreground">Loading transcript...</p>
                  ) : transcriptData?.transcript?.content ? (
                    <div className="p-4 text-sm leading-relaxed whitespace-pre-wrap">
                      {transcriptData.transcript.content}
                    </div>
                  ) : (
                    <p className="p-4 text-sm text-muted-foreground">No transcript content available.</p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="actions" className="mt-4 space-y-3">
              {meetingTasks.length === 0 ? (
                <p className="text-sm text-muted-foreground">No action items found.</p>
              ) : (
                meetingTasks.map((t: any) => {
                  const assigneeName = t.owner?.name || "Assigned User";
                  const deadline = t.deadline || (t.due_date ? new Date(t.due_date).toLocaleDateString() : "No deadline");
                  return (
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
                            {assigneeName} · Due {deadline}
                          </p>
                        </div>
                        <PriorityBadge priority={t.priority} />
                        <StatusBadge status={t.status} />
                      </CardContent>
                    </Card>
                  );
                })
              )}
            </TabsContent>
            <TabsContent value="decisions" className="mt-4 space-y-3">
              {meetingDecisions.length === 0 ? (
                <p className="text-sm text-muted-foreground">No decisions recorded.</p>
              ) : (
                meetingDecisions.map((d: any, idx: number) => {
                  const title = d.title || `Decision ${idx + 1}`;
                  const description = d.description || d.text || d;
                  const timestamp = d.timestamp || d.time || "";
                  return (
                    <Card key={d.id || idx} className="rounded-xl shadow-sm">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <h4 className="text-sm font-semibold">{title}</h4>
                            {typeof description === "string" && (
                              <p className="mt-1 text-sm text-muted-foreground">{description}</p>
                            )}
                          </div>
                          {timestamp && (
                            <Badge variant="outline" className="shrink-0 rounded-full">{timestamp}</Badge>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })
              )}
            </TabsContent>
          </Tabs>
        </div>

        <div className="space-y-6">
          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Participants</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {participants.length === 0 ? (
                <p className="text-xs text-muted-foreground">No participants listed.</p>
              ) : (
                participants.map((p: any) => (
                  <div key={p.id} className="flex items-center gap-3">
                    <Avatar className="h-9 w-9">
                      <AvatarFallback className="bg-primary/10 text-xs font-semibold text-primary">
                        {initials(p.name)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold">{p.name}</p>
                      {p.role && <p className="truncate text-xs text-muted-foreground">{p.role}</p>}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card className="rounded-xl shadow-sm">
            <CardHeader><CardTitle>Timeline</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {[
                { t: "Uploaded", d: isMock ? "10:02 AM" : "Complete" },
                { t: "Transcribed", d: isMock ? "10:04 AM" : (meeting.status === "processing" ? "Pending..." : "Complete") },
                { t: "Summary generated", d: isMock ? "10:05 AM" : (meeting.status === "processing" ? "Pending..." : "Complete") },
                { t: "Tasks extracted", d: isMock ? "10:06 AM" : (meeting.status === "processing" ? "Pending..." : "Complete") },
                { t: "Reminders scheduled", d: isMock ? "10:07 AM" : (meeting.status === "processing" ? "Pending..." : "Complete") },
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
