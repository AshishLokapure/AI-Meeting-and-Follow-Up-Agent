export type TaskStatus = "pending" | "in_progress" | "completed" | "overdue";
export type Priority = "low" | "medium" | "high" | "urgent";
export type MeetingStatus = "processed" | "processing" | "scheduled" | "failed";

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: string;
}

export interface Meeting {
  id: string;
  title: string;
  date: string;
  duration: number; // minutes
  status: MeetingStatus;
  participants: User[];
  summary: string;
  actionItems: number;
  decisions: number;
  recordingUrl?: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  owner: User;
  priority: Priority;
  deadline: string;
  status: TaskStatus;
  meetingId: string;
  meetingTitle: string;
  createdAt: string;
  remindersSent: number;
}

export interface Decision {
  id: string;
  title: string;
  description: string;
  meetingId: string;
  timestamp: string;
}

export interface Notification {
  id: string;
  type: "reminder" | "escalation" | "assignment" | "completion";
  title: string;
  message: string;
  recipient: string;
  timestamp: string;
  status: "sent" | "scheduled" | "failed";
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: "active" | "idle" | "error";
  runsToday: number;
  successRate: number;
  lastRun: string;
  icon: string;
}

export const users: User[] = [
  { id: "u1", name: "Sarah Chen", email: "sarah@acme.io", role: "Product Manager" },
  { id: "u2", name: "Marcus Reid", email: "marcus@acme.io", role: "Engineering Lead" },
  { id: "u3", name: "Priya Patel", email: "priya@acme.io", role: "Designer" },
  { id: "u4", name: "Diego Alvarez", email: "diego@acme.io", role: "Data Scientist" },
  { id: "u5", name: "Emily Watson", email: "emily@acme.io", role: "Marketing" },
  { id: "u6", name: "Kenji Tanaka", email: "kenji@acme.io", role: "CTO" },
];

export const currentUser: User = {
  id: "me",
  name: "Alex Morgan",
  email: "alex@acme.io",
  role: "Operations Lead",
};

export const meetings: Meeting[] = [
  {
    id: "m1",
    title: "Q4 Product Roadmap Sync",
    date: "2026-07-24T10:00:00Z",
    duration: 62,
    status: "processed",
    participants: [users[0], users[1], users[2], users[5]],
    summary:
      "Aligned on Q4 priorities focused on the AI assistant launch, enterprise SSO rollout, and mobile onboarding revamp. Marcus flagged capacity concerns for the SSO workstream.",
    actionItems: 7,
    decisions: 4,
  },
  {
    id: "m2",
    title: "Design Review — Onboarding v3",
    date: "2026-07-23T15:30:00Z",
    duration: 45,
    status: "processed",
    participants: [users[2], users[0], users[4]],
    summary:
      "Reviewed onboarding v3 prototypes. Approved the split-screen variant. Priya to iterate on empty states and ship handoff by Friday.",
    actionItems: 5,
    decisions: 2,
  },
  {
    id: "m3",
    title: "Weekly Engineering Standup",
    date: "2026-07-25T09:00:00Z",
    duration: 30,
    status: "processing",
    participants: [users[1], users[3], users[5]],
    summary: "Processing transcript…",
    actionItems: 0,
    decisions: 0,
  },
  {
    id: "m4",
    title: "Enterprise Customer QBR — Northwind",
    date: "2026-07-22T14:00:00Z",
    duration: 55,
    status: "processed",
    participants: [users[0], users[4], users[5]],
    summary:
      "Northwind renewed for 24 months with expansion into 3 new business units. Requested tighter Salesforce integration and dedicated support channel.",
    actionItems: 6,
    decisions: 3,
  },
  {
    id: "m5",
    title: "Hiring Panel — Senior ML Engineer",
    date: "2026-07-26T11:00:00Z",
    duration: 60,
    status: "scheduled",
    participants: [users[3], users[1], users[5]],
    summary: "Scheduled — awaiting recording.",
    actionItems: 0,
    decisions: 0,
  },
  {
    id: "m6",
    title: "Marketing Launch War Room",
    date: "2026-07-21T13:00:00Z",
    duration: 40,
    status: "processed",
    participants: [users[4], users[0], users[2]],
    summary:
      "Locked launch date for AI Meeting Agent to Aug 12. Emily driving press outreach; Priya finalizing launch site by Aug 5.",
    actionItems: 8,
    decisions: 5,
  },
];

export const tasks: Task[] = [
  {
    id: "t1",
    title: "Draft SSO rollout plan for enterprise customers",
    description:
      "Coordinate with security to draft a phased rollout plan for SAML SSO covering top 20 accounts.",
    owner: users[1],
    priority: "high",
    deadline: "2026-07-29",
    status: "in_progress",
    meetingId: "m1",
    meetingTitle: "Q4 Product Roadmap Sync",
    createdAt: "2026-07-24",
    remindersSent: 1,
  },
  {
    id: "t2",
    title: "Iterate on onboarding empty states",
    description: "Revise Figma flows based on design review feedback.",
    owner: users[2],
    priority: "medium",
    deadline: "2026-07-25",
    status: "overdue",
    meetingId: "m2",
    meetingTitle: "Design Review — Onboarding v3",
    createdAt: "2026-07-23",
    remindersSent: 3,
  },
  {
    id: "t3",
    title: "Send Northwind Salesforce integration scoping doc",
    description: "Compile requirements and send to Northwind's IT team by EOW.",
    owner: users[0],
    priority: "urgent",
    deadline: "2026-07-25",
    status: "pending",
    meetingId: "m4",
    meetingTitle: "Enterprise QBR — Northwind",
    createdAt: "2026-07-22",
    remindersSent: 2,
  },
  {
    id: "t4",
    title: "Confirm launch date with PR agency",
    description: "Lock Aug 12 launch date with external PR partners.",
    owner: users[4],
    priority: "high",
    deadline: "2026-07-24",
    status: "completed",
    meetingId: "m6",
    meetingTitle: "Marketing Launch War Room",
    createdAt: "2026-07-21",
    remindersSent: 0,
  },
  {
    id: "t5",
    title: "Prepare capacity plan for Q4",
    description: "Break down engineering capacity across SSO, AI, and Mobile workstreams.",
    owner: users[1],
    priority: "high",
    deadline: "2026-07-31",
    status: "pending",
    meetingId: "m1",
    meetingTitle: "Q4 Product Roadmap Sync",
    createdAt: "2026-07-24",
    remindersSent: 0,
  },
  {
    id: "t6",
    title: "Finalize launch landing site",
    description: "Ship approved copy and visuals to the marketing site.",
    owner: users[2],
    priority: "medium",
    deadline: "2026-08-05",
    status: "in_progress",
    meetingId: "m6",
    meetingTitle: "Marketing Launch War Room",
    createdAt: "2026-07-21",
    remindersSent: 0,
  },
  {
    id: "t7",
    title: "Publish ML model evaluation report",
    description: "Circulate v2 evaluation numbers across the AI team.",
    owner: users[3],
    priority: "low",
    deadline: "2026-08-02",
    status: "pending",
    meetingId: "m1",
    meetingTitle: "Q4 Product Roadmap Sync",
    createdAt: "2026-07-24",
    remindersSent: 0,
  },
  {
    id: "t8",
    title: "Schedule dedicated support Slack channel for Northwind",
    description: "Provision shared Slack Connect channel with named CSMs.",
    owner: users[0],
    priority: "medium",
    deadline: "2026-07-28",
    status: "in_progress",
    meetingId: "m4",
    meetingTitle: "Enterprise QBR — Northwind",
    createdAt: "2026-07-22",
    remindersSent: 1,
  },
];

export const decisions: Decision[] = [
  {
    id: "d1",
    title: "Approve split-screen onboarding variant",
    description: "Design team will move forward with split-screen layout for onboarding v3.",
    meetingId: "m2",
    timestamp: "00:24:12",
  },
  {
    id: "d2",
    title: "Lock AI Meeting Agent launch to Aug 12",
    description: "Cross-functional launch date confirmed with marketing, product, and PR.",
    meetingId: "m6",
    timestamp: "00:18:45",
  },
  {
    id: "d3",
    title: "Prioritize SSO for enterprise segment in Q4",
    description: "SSO workstream elevated above mobile onboarding for Q4.",
    meetingId: "m1",
    timestamp: "00:41:03",
  },
];

export const notifications: Notification[] = [
  {
    id: "n1",
    type: "reminder",
    title: "Reminder sent to Priya Patel",
    message: "Task \"Iterate on onboarding empty states\" is overdue.",
    recipient: "priya@acme.io",
    timestamp: "2026-07-25T08:00:00Z",
    status: "sent",
  },
  {
    id: "n2",
    type: "escalation",
    title: "Escalated to Kenji Tanaka",
    message: "Northwind Salesforce integration scoping doc is at risk.",
    recipient: "kenji@acme.io",
    timestamp: "2026-07-25T07:30:00Z",
    status: "sent",
  },
  {
    id: "n3",
    type: "assignment",
    title: "New task assigned to Marcus Reid",
    message: "Draft SSO rollout plan for enterprise customers.",
    recipient: "marcus@acme.io",
    timestamp: "2026-07-24T11:15:00Z",
    status: "sent",
  },
  {
    id: "n4",
    type: "reminder",
    title: "Upcoming reminder for Sarah Chen",
    message: "Task deadline tomorrow: Send Northwind scoping doc.",
    recipient: "sarah@acme.io",
    timestamp: "2026-07-25T18:00:00Z",
    status: "scheduled",
  },
  {
    id: "n5",
    type: "completion",
    title: "Task completed by Emily Watson",
    message: "Confirm launch date with PR agency marked as complete.",
    recipient: "team@acme.io",
    timestamp: "2026-07-24T16:22:00Z",
    status: "sent",
  },
];

export const agents: Agent[] = [
  {
    id: "a1",
    name: "Speech Agent",
    description: "Transcribes meeting recordings with speaker diarization.",
    status: "active",
    runsToday: 12,
    successRate: 99.1,
    lastRun: "2m ago",
    icon: "Mic",
  },
  {
    id: "a2",
    name: "Transcript Agent",
    description: "Cleans and structures raw transcripts into readable segments.",
    status: "active",
    runsToday: 12,
    successRate: 98.4,
    lastRun: "2m ago",
    icon: "FileText",
  },
  {
    id: "a3",
    name: "Summary Agent",
    description: "Generates executive summaries and key discussion topics.",
    status: "active",
    runsToday: 12,
    successRate: 97.8,
    lastRun: "3m ago",
    icon: "Sparkles",
  },
  {
    id: "a4",
    name: "Task Extraction Agent",
    description: "Extracts action items, owners, and deadlines from context.",
    status: "active",
    runsToday: 12,
    successRate: 94.2,
    lastRun: "3m ago",
    icon: "ListChecks",
  },
  {
    id: "a5",
    name: "Reminder Agent",
    description: "Sends smart reminders across email and Slack.",
    status: "active",
    runsToday: 48,
    successRate: 99.7,
    lastRun: "12m ago",
    icon: "Bell",
  },
  {
    id: "a6",
    name: "Escalation Agent",
    description: "Escalates overdue items to managers with context.",
    status: "idle",
    runsToday: 3,
    successRate: 96.0,
    lastRun: "1h ago",
    icon: "AlertTriangle",
  },
];

export const meetingTrends = [
  { week: "W1", meetings: 8, tasks: 32 },
  { week: "W2", meetings: 12, tasks: 41 },
  { week: "W3", meetings: 10, tasks: 38 },
  { week: "W4", meetings: 14, tasks: 52 },
  { week: "W5", meetings: 11, tasks: 44 },
  { week: "W6", meetings: 16, tasks: 61 },
  { week: "W7", meetings: 18, tasks: 68 },
];

export const completionTrend = [
  { day: "Mon", completed: 12, pending: 4 },
  { day: "Tue", completed: 18, pending: 6 },
  { day: "Wed", completed: 14, pending: 8 },
  { day: "Thu", completed: 22, pending: 5 },
  { day: "Fri", completed: 28, pending: 9 },
  { day: "Sat", completed: 6, pending: 2 },
  { day: "Sun", completed: 4, pending: 1 },
];

export const priorityBreakdown = [
  { name: "Urgent", value: 8, color: "#DC2626" },
  { name: "High", value: 22, color: "#F59E0B" },
  { name: "Medium", value: 34, color: "#3B82F6" },
  { name: "Low", value: 16, color: "#16A34A" },
];

export const agentPerformance = [
  { agent: "Speech", accuracy: 99 },
  { agent: "Transcript", accuracy: 98 },
  { agent: "Summary", accuracy: 97 },
  { agent: "Task", accuracy: 94 },
  { agent: "Reminder", accuracy: 99 },
  { agent: "Escalation", accuracy: 96 },
];

export const transcriptSample = [
  { speaker: "Sarah Chen", time: "00:00:12", text: "Thanks everyone for joining. Let's start with the Q4 roadmap. Marcus, can you kick us off with engineering priorities?" },
  { speaker: "Marcus Reid", time: "00:00:34", text: "Sure. We have three big rocks: the AI assistant launch, enterprise SSO, and the mobile onboarding revamp. Capacity-wise, SSO is going to be tight." },
  { speaker: "Sarah Chen", time: "00:01:02", text: "Let's dig into that. What's the ask?" },
  { speaker: "Marcus Reid", time: "00:01:10", text: "Ideally another two engineers for four weeks. Otherwise SSO slips into Q1." },
  { speaker: "Kenji Tanaka", time: "00:01:41", text: "SSO is a top enterprise blocker. Let's prioritize it. Marcus, put together a capacity plan by end of week." },
  { speaker: "Priya Patel", time: "00:02:15", text: "For mobile onboarding, I'll have the redesigned flows ready for review next week." },
  { speaker: "Sarah Chen", time: "00:02:38", text: "Great. Let's also make sure the ML evaluation report goes out to the wider team." },
];
