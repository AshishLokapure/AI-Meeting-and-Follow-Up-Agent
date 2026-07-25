import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Sparkles,
  Mic,
  ListChecks,
  Bell,
  BarChart3,
  Bot,
  ArrowRight,
  Check,
  Video,
  Users,
  Zap,
  Shield,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Loop — AI Meeting & Follow-Up Agent" },
      {
        name: "description",
        content:
          "Loop turns every meeting into tracked decisions, owned action items, and autonomous follow-ups until work gets done.",
      },
      { property: "og:title", content: "Loop — AI Meeting & Follow-Up Agent" },
      {
        property: "og:description",
        content: "Autonomous meeting intelligence for modern operations teams.",
      },
    ],
  }),
  component: Landing,
});

const features = [
  { icon: Mic, title: "Transcribe any meeting", desc: "Upload MP3, MP4, WAV or M4A. Speaker-aware transcripts in minutes." },
  { icon: ListChecks, title: "Extract action items", desc: "Owners, deadlines, and priority — auto-detected from context." },
  { icon: Bell, title: "Autonomous follow-ups", desc: "Reminders on your cadence, escalations when items go dark." },
  { icon: BarChart3, title: "Analytics that matter", desc: "Completion rate, avg. delay, agent accuracy — at a glance." },
  { icon: Bot, title: "Six specialized agents", desc: "Speech, transcript, summary, extraction, reminder, escalation." },
  { icon: Shield, title: "Enterprise-ready", desc: "SSO, audit logs, role-based access, EU data residency." },
];

const steps = [
  { n: "01", t: "Upload a recording", d: "Drop the file — or connect Zoom, Meet, or Teams." },
  { n: "02", t: "Agents process it", d: "Six agents transcribe, summarize, and extract next steps." },
  { n: "03", t: "Owners get pinged", d: "Slack + email reminders on your cadence." },
  { n: "04", t: "Work gets done", d: "Escalate on delay. Auto-close when complete." },
];

const testimonials = [
  { name: "Sarah Chen", role: "Head of Product · Northwind", quote: "We went from losing action items in Notion to shipping them. Loop pays for itself in a week." },
  { name: "Marcus Reid", role: "VP Engineering · Atlas", quote: "The escalation agent alone saved us three at-risk launches last quarter." },
  { name: "Priya Patel", role: "COO · Lumen", quote: "It's the missing layer between meetings and execution. Feels inevitable." },
];

const faqs = [
  { q: "What file formats do you support?", a: "MP3, MP4, WAV, and M4A up to 500MB. Direct integrations with Zoom, Google Meet, and Teams are also available." },
  { q: "How accurate are the extracted tasks?", a: "Our task extraction agent hits 94%+ accuracy on structured meetings and improves as your team confirms or edits items." },
  { q: "Can I control reminder cadence?", a: "Yes — set frequency per workspace, and escalation rules per team or task priority." },
  { q: "Is my data secure?", a: "SOC 2 Type II, encryption at rest and in transit, and optional EU data residency." },
];

function Landing() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Nav */}
      <header className="sticky top-0 z-30 border-b bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground">
              <Sparkles className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold">Loop</span>
          </Link>
          <nav className="hidden items-center gap-6 text-sm font-medium text-muted-foreground md:flex">
            <a href="#features" className="hover:text-foreground">Features</a>
            <a href="#workflow" className="hover:text-foreground">Workflow</a>
            <a href="#pricing" className="hover:text-foreground">Pricing</a>
            <a href="#faq" className="hover:text-foreground">FAQ</a>
          </nav>
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost"><Link to="/login">Sign in</Link></Button>
            <Button asChild><Link to="/register">Get started</Link></Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden border-b">
        <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_50%_at_50%_0%,rgba(37,99,235,0.12),transparent_70%)]" />
        <div className="mx-auto max-w-7xl px-4 py-20 text-center sm:px-6 lg:py-28 lg:px-8">
          <Badge variant="outline" className="rounded-full border-primary/30 bg-primary/5 text-primary">
            <Sparkles className="mr-1 h-3 w-3" /> Now in general availability
          </Badge>
          <h1 className="mx-auto mt-6 max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl">
            Meetings in. <span className="text-primary">Follow-through</span> out.
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-muted-foreground">
            Loop turns every recording into decisions tracked, owners assigned, and reminders sent —
            until each action item is done.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Button asChild size="lg"><Link to="/register">Start free trial <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
            <Button asChild size="lg" variant="outline"><Link to="/dashboard">See live demo</Link></Button>
          </div>
          <div className="mt-14 grid gap-3 rounded-2xl border bg-card p-4 shadow-xl sm:grid-cols-3">
            {[
              { icon: Video, k: "128", v: "Meetings processed" },
              { icon: ListChecks, k: "342", v: "Tasks auto-created" },
              { icon: Zap, k: "97.8%", v: "AI accuracy" },
            ].map((s) => (
              <div key={s.v} className="flex items-center gap-3 rounded-xl bg-muted/40 p-4">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary">
                  <s.icon className="h-5 w-5" />
                </div>
                <div className="text-left">
                  <p className="text-2xl font-bold">{s.k}</p>
                  <p className="text-xs text-muted-foreground">{s.v}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="border-b py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Everything after the meeting</h2>
            <p className="mt-3 text-muted-foreground">Six purpose-built agents handle the tedious follow-through so your team can focus on execution.</p>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <Card key={f.title} className="rounded-xl shadow-sm">
                <CardContent className="p-6">
                  <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary/10 text-primary">
                    <f.icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-4 text-base font-semibold">{f.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{f.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section id="workflow" className="border-b bg-muted/30 py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">How Loop works</h2>
            <p className="mt-3 text-muted-foreground">From recording to resolved — end-to-end automation.</p>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {steps.map((s) => (
              <Card key={s.n} className="rounded-xl shadow-sm">
                <CardContent className="p-6">
                  <span className="text-xs font-bold text-primary">{s.n}</span>
                  <h3 className="mt-2 text-base font-semibold">{s.t}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{s.d}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="border-b py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">The agent stack</h2>
            <p className="mt-3 text-muted-foreground">A pipeline of specialized agents, each observable and controllable.</p>
          </div>
          <div className="mt-12 grid gap-3 md:grid-cols-6">
            {["Speech", "Transcript", "Summary", "Task Extraction", "Reminder", "Escalation"].map((a, i) => (
              <div key={a} className="relative rounded-xl border bg-card p-4 shadow-sm">
                <span className="text-xs font-bold text-primary">Agent {i + 1}</span>
                <p className="mt-1 text-sm font-semibold">{a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="border-b bg-muted/30 py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Loved by operators</h2>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            {testimonials.map((t) => (
              <Card key={t.name} className="rounded-xl shadow-sm">
                <CardContent className="p-6">
                  <p className="text-sm leading-relaxed">"{t.quote}"</p>
                  <div className="mt-4 flex items-center gap-3">
                    <Avatar className="h-9 w-9">
                      <AvatarFallback className="bg-primary/10 text-xs font-semibold text-primary">
                        {t.name.split(" ").map((x) => x[0]).join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="text-sm font-semibold">{t.name}</p>
                      <p className="text-xs text-muted-foreground">{t.role}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="border-b py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Pricing that scales with you</h2>
            <p className="mt-3 text-muted-foreground">Start free. Upgrade when your team is ready.</p>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            {[
              { name: "Starter", price: "$0", desc: "For small teams trying Loop out.", features: ["5 meetings / month", "Basic analytics", "Email reminders"] },
              { name: "Growth", price: "$29", desc: "Per user / month, billed annually.", features: ["Unlimited meetings", "Slack + email reminders", "Escalation agent", "Analytics dashboard"], featured: true },
              { name: "Enterprise", price: "Custom", desc: "For orgs with security requirements.", features: ["SSO / SAML", "Audit logs", "EU data residency", "Dedicated support"] },
            ].map((p) => (
              <Card key={p.name} className={`rounded-xl shadow-sm ${p.featured ? "border-primary shadow-lg ring-2 ring-primary/20" : ""}`}>
                <CardContent className="p-6">
                  <p className="text-sm font-semibold">{p.name}</p>
                  <p className="mt-2 text-3xl font-bold">{p.price}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{p.desc}</p>
                  <ul className="mt-5 space-y-2 text-sm">
                    {p.features.map((f) => (
                      <li key={f} className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-success" /> {f}
                      </li>
                    ))}
                  </ul>
                  <Button asChild className="mt-6 w-full" variant={p.featured ? "default" : "outline"}>
                    <Link to="/register">Get started</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="border-b py-20">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Frequently asked</h2>
          </div>
          <Accordion type="single" collapsible className="mt-10">
            {faqs.map((f, i) => (
              <AccordionItem key={i} value={`i${i}`}>
                <AccordionTrigger className="text-left text-base font-semibold">{f.q}</AccordionTrigger>
                <AccordionContent className="text-sm text-muted-foreground">{f.a}</AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="rounded-2xl border bg-gradient-to-br from-primary to-[oklch(0.46_0.24_265)] p-10 text-center text-primary-foreground shadow-xl">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Stop losing action items.
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-primary-foreground/80">
              Two minutes to set up. Your next meeting will already be tracked.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <Button asChild size="lg" variant="secondary"><Link to="/register">Start free</Link></Button>
              <Button asChild size="lg" variant="outline" className="border-white/40 bg-transparent text-primary-foreground hover:bg-white/10">
                <Link to="/dashboard">See the demo</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-muted/30 py-12">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:grid-cols-2 sm:px-6 lg:grid-cols-4 lg:px-8">
          <div>
            <div className="flex items-center gap-2">
              <div className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-primary-foreground">
                <Sparkles className="h-4 w-4" />
              </div>
              <span className="font-bold">Loop</span>
            </div>
            <p className="mt-3 text-sm text-muted-foreground">Autonomous meeting intelligence.</p>
          </div>
          {[
            { t: "Product", l: ["Features", "Pricing", "Integrations", "Changelog"] },
            { t: "Company", l: ["About", "Careers", "Blog", "Contact"] },
            { t: "Legal", l: ["Privacy", "Terms", "Security", "DPA"] },
          ].map((c) => (
            <div key={c.t}>
              <p className="text-sm font-semibold">{c.t}</p>
              <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                {c.l.map((x) => <li key={x}><a href="#" className="hover:text-foreground">{x}</a></li>)}
              </ul>
            </div>
          ))}
        </div>
        <div className="mx-auto mt-8 max-w-7xl border-t px-4 pt-6 text-xs text-muted-foreground sm:px-6 lg:px-8">
          © 2026 Loop, Inc. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
