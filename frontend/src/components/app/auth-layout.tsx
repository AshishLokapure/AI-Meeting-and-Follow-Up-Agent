import type { ReactNode } from "react";
import { Link } from "@tanstack/react-router";
import { Sparkles } from "lucide-react";

export function AuthLayout({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md">
          <Link to="/" className="mb-8 flex items-center gap-2">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground">
              <Sparkles className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold">Loop</span>
          </Link>
          <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
          <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
          <div className="mt-8">{children}</div>
          {footer ? <div className="mt-6 text-center text-sm text-muted-foreground">{footer}</div> : null}
        </div>
      </div>
      <div className="hidden bg-gradient-to-br from-primary to-[oklch(0.42_0.22_270)] p-12 lg:flex lg:flex-col lg:justify-between">
        <div className="text-primary-foreground/90 text-sm font-medium">
          <Sparkles className="mb-4 h-6 w-6" />
          Autonomous meeting intelligence
        </div>
        <div className="text-primary-foreground">
          <p className="text-2xl font-semibold leading-snug">
            "We stopped chasing action items three days after we deployed Loop. It just closes the loop."
          </p>
          <p className="mt-4 text-sm text-primary-foreground/80">— Sarah Chen, Head of Product · Northwind</p>
        </div>
      </div>
    </div>
  );
}
