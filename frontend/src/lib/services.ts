import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest, apiUpload } from "./api";
import { saveAuthSession, getAuthSession } from "./auth";

// --- TYPES ---
export interface ApiUser {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  email_verified: boolean;
  avatar_url?: string | null;
}

export interface ApiMeeting {
  id: string;
  title: string;
  status: string;
  recording_url?: string | null;
  duration_minutes?: number | null;
  meeting_date?: string | null;
  start_time?: string | null;
  agenda?: string | null;
  participants: Array<{ id: string; name: string; email?: string | null; role?: string | null }>;
  summary_text?: string | null;
  action_items_count: number;
  decisions_count: number;
  created_at: string;
}

export interface ApiTask {
  id: string;
  meeting_id: string;
  assignee_id?: string | null;
  title: string;
  description?: string | null;
  priority: string;
  status: string;
  due_date?: string | null;
  source_excerpt?: string | null;
  created_at: string;
}

export interface DashboardStatsData {
  total_meetings: number;
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  overdue_tasks: number;
  in_progress_tasks: number;
}

// --- HOOKS ---

// Dashboard Stats
export function useDashboardStats() {
  return useQuery<DashboardStatsData>({
    queryKey: ["dashboard", "stats"],
    queryFn: () => apiRequest<DashboardStatsData>("/dashboard/stats"),
  });
}

// Meetings Queries & Mutations
export function useMeetings(status?: string, q?: string) {
  return useQuery<{ meetings: ApiMeeting[]; total: number }>({
    queryKey: ["meetings", { status, q }],
    queryFn: () => {
      const params = new URLSearchParams();
      if (status && status !== "all") params.append("status", status);
      if (q) params.append("q", q);
      const queryStr = params.toString() ? `?${params.toString()}` : "";
      return apiRequest<{ meetings: ApiMeeting[]; total: number }>(`/meetings${queryStr}`);
    },
  });
}

export function useMeeting(id: string) {
  return useQuery<ApiMeeting>({
    queryKey: ["meetings", id],
    queryFn: () => apiRequest<ApiMeeting>(`/meetings/${id}`),
    enabled: !!id,
  });
}

export function useMeetingTranscript(id: string) {
  return useQuery<{ message: string; transcript: { content: string }; meeting_status: string }>({
    queryKey: ["meetings", id, "transcript"],
    queryFn: () => apiRequest(`/meetings/${id}/transcript`),
    enabled: !!id,
  });
}

export function useMeetingAnalysis(id: string) {
  return useQuery<{ message: string; analysis: { summary: string; action_items: any[]; decisions: any[] }; meeting_status: string }>({
    queryKey: ["meetings", id, "analysis"],
    queryFn: () => apiRequest(`/meetings/${id}/analysis`),
    enabled: !!id,
  });
}

export function useUploadMeeting() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variables: { file: File; title?: string }) => {
      const formData = new FormData();
      formData.append("file", variables.file);
      if (variables.title) {
        formData.append("title", variables.title);
      }
      return apiUpload<any>("/meetings/upload", formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard", "stats"] });
    },
  });
}

// Tasks Queries & Mutations
export function useTasks(status?: string, priority?: string, q?: string) {
  return useQuery<{ tasks: ApiTask[]; total: number }>({
    queryKey: ["tasks", { status, priority, q }],
    queryFn: () => {
      const params = new URLSearchParams();
      if (status && status !== "all") params.append("status", status);
      if (priority && priority !== "all") params.append("priority", priority);
      if (q) params.append("q", q);
      const queryStr = params.toString() ? `?${params.toString()}` : "";
      return apiRequest<{ tasks: ApiTask[]; total: number }>(`/tasks${queryStr}`);
    },
  });
}

export function useTask(id: string) {
  return useQuery<ApiTask>({
    queryKey: ["tasks", id],
    queryFn: () => apiRequest<ApiTask>(`/tasks/${id}`),
    enabled: !!id,
  });
}

export function useUpdateTaskStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variables: { id: string; status: string }) =>
      apiRequest<ApiTask>(`/tasks/${variables.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: variables.status }),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["tasks", data.id] });
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard", "stats"] });
    },
  });
}

// User Profile Queries & Mutations
export function useUserProfile() {
  return useQuery<ApiUser>({
    queryKey: ["users", "me"],
    queryFn: () => apiRequest<ApiUser>("/users/me"),
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variables: { name?: string; email?: string }) =>
      apiRequest<any>("/users/me", {
        method: "PATCH",
        body: JSON.stringify(variables),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["users", "me"] });
      // Update local storage too if session matches
      const session = getAuthSession();
      if (session) {
        session.user = { ...session.user, ...data.user };
        saveAuthSession(session);
      }
    },
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: (variables: { current_password: string; new_password: string }) =>
      apiRequest<any>("/users/me/change-password", {
        method: "POST",
        body: JSON.stringify(variables),
      }),
  });
}
