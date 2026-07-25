import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Users, Phone, Mail, Building2 } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";
import { apiRequest } from "@/lib/api";

export const Route = createFileRoute("/_app/employees")({
  head: () => ({
    meta: [{ title: "Employees — Loop" }],
  }),
  component: EmployeesPage,
});

interface Employee {
  id: string;
  name: string;
  first_name?: string;
  last_name?: string;
  email: string;
  phone: string | null;
  department: string | null;
  designation: string | null;
  is_active: boolean;
  status?: string;
  created_at: string;
}

interface EmployeeForm {
  name: string;
  email: string;
  phone: string;
  department: string;
  designation: string;
}

const EMPTY_FORM: EmployeeForm = { name: "", email: "", phone: "", department: "", designation: "" };

function splitEmployeeName(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length < 2) return null;
  return {
    first_name: parts[0],
    last_name: parts.slice(1).join(" "),
  };
}

function useEmployees() {
  return useQuery<Employee[]>({
    queryKey: ["employees"],
    queryFn: async () => {
      const payload = await apiRequest<
        Employee[] | { employees?: Employee[] }
      >("/employees");

      const employees = Array.isArray(payload) ? payload : payload?.employees;
      if (!Array.isArray(employees)) return [];

      return employees.map((employee) => ({
        ...employee,
        name:
          employee.name ||
          [employee.first_name, employee.last_name].filter(Boolean).join(" "),
        is_active: employee.status
          ? employee.status === "active"
          : employee.is_active,
      }));
    },
  });
}

function EmployeeFormDialog({
  open,
  onClose,
  initial,
  employeeId,
}: {
  open: boolean;
  onClose: () => void;
  initial: EmployeeForm;
  employeeId?: string;
}) {
  const qc = useQueryClient();
  const [form, setForm] = useState<EmployeeForm>(initial);
  const [loading, setLoading] = useState(false);

  const set = (k: keyof EmployeeForm) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (ev: React.FormEvent) => {
    ev.preventDefault();
    const name = splitEmployeeName(form.name);
    if (!name || !form.email.trim()) {
      toast.error("Enter a first and last name, plus an email address");
      return;
    }
    setLoading(true);
    try {
      const body = {
        ...name,
        email: form.email.trim(),
        phone: form.phone.trim() || null,
        department: form.department.trim() || null,
        designation: form.designation.trim() || null,
      };
      if (employeeId) {
        await apiRequest(`/employees/${employeeId}`, { method: "PATCH", body: JSON.stringify(body) });
        toast.success("Employee updated");
      } else {
        await apiRequest("/employees", { method: "POST", body: JSON.stringify(body) });
        toast.success("Employee added");
      }
      qc.invalidateQueries({ queryKey: ["employees"] });
      onClose();
    } catch (err: any) {
      toast.error(err.message ?? "Failed to save employee");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{employeeId ? "Edit Employee" : "Add Employee"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="emp-name">Full Name *</Label>
            <Input id="emp-name" placeholder="Rahul Mehta" value={form.name} onChange={set("name")} required />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="emp-email">Email Address *</Label>
            <Input id="emp-email" type="email" placeholder="rahul@company.com" value={form.email} onChange={set("email")} required disabled={!!employeeId} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="emp-phone">Phone Number</Label>
            <Input id="emp-phone" placeholder="+91 98765 43210" value={form.phone} onChange={set("phone")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="emp-dept">Department</Label>
              <Input id="emp-dept" placeholder="Engineering" value={form.department} onChange={set("department")} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="emp-desig">Designation</Label>
              <Input id="emp-desig" placeholder="Developer" value={form.designation} onChange={set("designation")} />
            </div>
          </div>
          <DialogFooter className="pt-2">
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>Cancel</Button>
            <Button type="submit" disabled={loading}>{loading ? "Saving…" : employeeId ? "Update" : "Add Employee"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function EmployeesPage() {
  const { data: employees = [], isLoading } = useEmployees();
  const qc = useQueryClient();

  const [addOpen, setAddOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Employee | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Employee | null>(null);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await apiRequest(`/employees/${deleteTarget.id}`, { method: "DELETE" });
      toast.success(`${deleteTarget.name} removed`);
      qc.invalidateQueries({ queryKey: ["employees"] });
    } catch (err: any) {
      toast.error(err.message ?? "Failed to delete");
    } finally {
      setDeleting(false);
      setDeleteTarget(null);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Employees"
        description="Manage your team. Task assignment emails are sent to these employees after meeting analysis."
        actions={
          <Button onClick={() => setAddOpen(true)} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Employee
          </Button>
        }
      />

      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-xl bg-muted" />
          ))}
        </div>
      ) : employees.length === 0 ? (
        <Card className="rounded-xl shadow-sm">
          <CardContent className="flex flex-col items-center gap-3 py-16 text-center">
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-muted">
              <Users className="h-7 w-7 text-muted-foreground" />
            </div>
            <p className="text-base font-semibold">No employees yet</p>
            <p className="text-sm text-muted-foreground max-w-xs">
              Add employees so the AI can assign tasks to them automatically after meeting analysis.
            </p>
            <Button onClick={() => setAddOpen(true)} className="mt-2 gap-2">
              <Plus className="h-4 w-4" /> Add First Employee
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {employees.map((emp) => (
            <Card key={emp.id} className="rounded-xl shadow-sm hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-primary/10 text-primary font-bold text-sm">
                      {emp.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-sm">{emp.name}</p>
                      {emp.designation && (
                        <p className="truncate text-xs text-muted-foreground">{emp.designation}</p>
                      )}
                    </div>
                  </div>
                  <Badge variant={emp.is_active ? "default" : "secondary"} className="shrink-0 text-xs">
                    {emp.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>

                <div className="mt-4 space-y-1.5">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Mail className="h-3.5 w-3.5 shrink-0" />
                    <span className="truncate">{emp.email}</span>
                  </div>
                  {emp.phone && (
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Phone className="h-3.5 w-3.5 shrink-0" />
                      <span>{emp.phone}</span>
                    </div>
                  )}
                  {emp.department && (
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Building2 className="h-3.5 w-3.5 shrink-0" />
                      <span>{emp.department}</span>
                    </div>
                  )}
                </div>

                <div className="mt-4 flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 gap-1.5 text-xs"
                    onClick={() => setEditTarget(emp)}
                  >
                    <Pencil className="h-3.5 w-3.5" /> Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 gap-1.5 text-xs text-destructive hover:text-destructive"
                    onClick={() => setDeleteTarget(emp)}
                  >
                    <Trash2 className="h-3.5 w-3.5" /> Remove
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add dialog */}
      <EmployeeFormDialog
        open={addOpen}
        onClose={() => setAddOpen(false)}
        initial={EMPTY_FORM}
      />

      {/* Edit dialog */}
      {editTarget && (
        <EmployeeFormDialog
          open={!!editTarget}
          onClose={() => setEditTarget(null)}
          initial={{
            name: editTarget.name,
            email: editTarget.email,
            phone: editTarget.phone ?? "",
            department: editTarget.department ?? "",
            designation: editTarget.designation ?? "",
          }}
          employeeId={editTarget.id}
        />
      )}

      {/* Delete confirm */}
      <AlertDialog open={!!deleteTarget} onOpenChange={(o) => !o && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove {deleteTarget?.name}?</AlertDialogTitle>
            <AlertDialogDescription>
              This will remove the employee from your team. They will no longer receive task assignment emails.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} disabled={deleting} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              {deleting ? "Removing…" : "Remove"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
