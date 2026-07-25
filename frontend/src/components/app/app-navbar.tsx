import { Bell, Search, Settings } from "lucide-react";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Link } from "@tanstack/react-router";
import { useUserProfile } from "@/lib/services";
import { getAuthSession } from "@/lib/auth";

export function AppNavbar() {
  const { data: userProfile } = useUserProfile();
  const session = getAuthSession();

  const name = userProfile?.name || session?.user?.name || "User";
  const role = userProfile?.role || session?.user?.role || "Member";

  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase();

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-2 border-b bg-background/80 px-4 backdrop-blur-md">
      <SidebarTrigger className="shrink-0" />
      <div className="relative hidden max-w-md flex-1 md:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search meetings, tasks, people…"
          className="h-10 rounded-lg border-border bg-muted/40 pl-9 focus-visible:bg-background"
        />
      </div>
      <div className="ml-auto flex items-center gap-2">
        <Button variant="ghost" size="icon" className="relative" aria-label="Notifications" asChild>
          <Link to="/notifications">
            <Bell className="h-5 w-5" />
            <Badge className="absolute -right-0.5 -top-0.5 h-4 min-w-4 justify-center rounded-full bg-destructive px-1 text-[10px] text-destructive-foreground">
              3
            </Badge>
          </Link>
        </Button>
        <Button variant="ghost" size="icon" aria-label="Settings" asChild>
          <Link to="/settings">
            <Settings className="h-5 w-5" />
          </Link>
        </Button>
        <Link to="/profile" className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-muted">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-primary/10 text-xs font-semibold text-primary">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div className="hidden min-w-0 flex-col text-left sm:flex">
            <span className="truncate text-sm font-semibold leading-tight">{name}</span>
            <span className="truncate text-xs text-muted-foreground">{role}</span>
          </div>
        </Link>
      </div>
    </header>
  );
}
