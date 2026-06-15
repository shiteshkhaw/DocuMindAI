export interface Workspace {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  organization_id?: string | null;
}
