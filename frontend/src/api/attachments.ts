import { getToken } from "../auth/token";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export type Attachment = {
  attachment_id: number;
  journal_id: number;
  user_id: number;
  storage_key: string;
  public_url: string;
  mime: string;
  size: number;
  width?: number | null;
  height?: number | null;
  created_at?: string;
};

export async function listAttachments(journalId: number): Promise<Attachment[]> {
  const res = await fetch(`${API_BASE}/journals/${journalId}/attachments`, {
    method: "GET",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || res.statusText);
  }
  return (await res.json()) as Attachment[];
}

export async function uploadAttachment(
  journalId: number,
  file: File
): Promise<Attachment> {
  const user_id = getToken();
  if (!user_id) throw new Error("Not logged in");
  const form = new FormData();
  form.append("user_id", user_id);
  form.append("file", file, file.name);
  const res = await fetch(`${API_BASE}/journals/${journalId}/attachments`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || res.statusText);
  }
  return (await res.json()) as Attachment;
}

export async function deleteAttachment(
  journalId: number,
  attachmentId: number
): Promise<void> {
  const user_id = getToken();
  if (!user_id) throw new Error("Not logged in");
  const res = await fetch(
    `${API_BASE}/journals/${journalId}/attachments/${attachmentId}`,
    {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: Number(user_id) }),
    }
  );
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || res.statusText);
  }
}

