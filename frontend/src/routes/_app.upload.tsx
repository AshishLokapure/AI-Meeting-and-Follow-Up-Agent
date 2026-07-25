import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef } from "react";
import { UploadCloud, FileAudio, X, CheckCircle2 } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useUploadMeeting } from "@/lib/services";

export const Route = createFileRoute("/_app/upload")({
  head: () => ({
    meta: [
      { title: "Upload meeting — Loop" },
      { name: "description", content: "Upload a recording to extract tasks and decisions." },
    ],
  }),
  component: UploadPage,
});

interface UploadItem {
  id: string;
  name: string;
  size: number;
  progress: number;
  done: boolean;
}

function formatBytes(b: number) {
  if (b < 1024) return `${b} B`;
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / 1024 / 1024).toFixed(1)} MB`;
}

function UploadPage() {
  const [dragging, setDragging] = useState(false);
  const [items, setItems] = useState<UploadItem[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const uploadMeetingMutation = useUploadMeeting();

  const addFiles = (files: FileList | null) => {
    if (!files) return;
    Array.from(files).forEach((f) => {
      const id = crypto.randomUUID();
      const item: UploadItem = { id, name: f.name, size: f.size, progress: 10, done: false };
      setItems((prev) => [item, ...prev]);

      // Simple upload progress simulation during fetch
      const interval = setInterval(() => {
        setItems((prev) =>
          prev.map((it) => {
            if (it.id !== id) return it;
            if (it.done) return it;
            const next = Math.min(95, it.progress + Math.random() * 15);
            return { ...it, progress: next };
          })
        );
      }, 200);

      // Call real API
      uploadMeetingMutation.mutate(
        { file: f, title: f.name.substring(0, f.name.lastIndexOf('.')) || f.name },
        {
          onSuccess: () => {
            clearInterval(interval);
            setItems((prev) =>
              prev.map((it) => {
                if (it.id !== id) return it;
                return { ...it, progress: 100, done: true };
              })
            );
            toast.success(`Uploaded ${f.name}`, { description: "Processing has started." });
          },
          onError: (err) => {
            clearInterval(interval);
            setItems((prev) => prev.filter((x) => x.id !== id));
            toast.error(`Upload failed: ${err.message}`);
          }
        }
      );
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Upload meeting"
        description="Drop a recording or transcript to extract decisions and action items."
      />

      <Card className="rounded-xl shadow-sm">
        <CardContent className="p-6">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              addFiles(e.dataTransfer.files);
            }}
            className={cn(
              "flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-border p-10 text-center transition-colors",
              dragging && "border-primary bg-primary/5",
            )}
          >
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-primary/10 text-primary">
              <UploadCloud className="h-7 w-7" />
            </div>
            <div>
              <p className="text-base font-semibold">Drag & drop your recording</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Supports MP3, MP4, WAV, M4A, or TXT transcripts up to 100MB
              </p>
            </div>
            <input
              ref={inputRef}
              type="file"
              multiple
              accept=".mp3,.mp4,.wav,.m4a,.txt,.md,audio/*,video/*,text/plain"
              className="hidden"
              onChange={(e) => addFiles(e.target.files)}
            />
            <Button onClick={() => inputRef.current?.click()} className="mt-2">
              Choose files
            </Button>
          </div>
        </CardContent>
      </Card>

      {items.length > 0 && (
        <Card className="rounded-xl shadow-sm">
          <CardContent className="space-y-3 p-4">
            {items.map((it) => (
              <div key={it.id} className="flex items-center gap-3 rounded-lg border border-border/60 p-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-muted">
                  <FileAudio className="h-5 w-5 text-muted-foreground" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="truncate text-sm font-semibold">{it.name}</p>
                    <span className="shrink-0 text-xs text-muted-foreground">{formatBytes(it.size)}</span>
                  </div>
                  <Progress value={it.progress} className="mt-2 h-1.5" />
                  <p className="mt-1 text-xs text-muted-foreground">
                    {it.done ? "Ready · agents processing…" : `Uploading… ${Math.round(it.progress)}%`}
                  </p>
                </div>
                {it.done ? (
                  <CheckCircle2 className="h-5 w-5 shrink-0 text-success" />
                ) : (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setItems((prev) => prev.filter((x) => x.id !== it.id))}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
