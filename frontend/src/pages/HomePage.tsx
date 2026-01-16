import { useEffect, useMemo, useState } from "react";
import {
  type Journal,
  type JournalFilters,
  closeJournal,
  createJournal,
  deleteJournal,
  fetchJournals,
} from "../api/journals";
import {
  type Attachment,
  listAttachments,
  uploadAttachment,
  deleteAttachment as removeAttachment,
} from "../api/attachments";

export default function HomePage() {
  const [filters, setFilters] = useState<JournalFilters>({});
  const [journals, setJournals] = useState<Journal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imagesOpen, setImagesOpen] = useState<Record<number, boolean>>({});
  const [attachments, setAttachments] = useState<Record<number, Attachment[]>>({});
  const [attachmentsLoading, setAttachmentsLoading] = useState<Record<number, boolean>>({});
  const [attachmentsError, setAttachmentsError] = useState<Record<number, string | null>>({});
  const [lightboxUrl, setLightboxUrl] = useState<string | null>(null);

  const [form, setForm] = useState({
    symbol: "",
    side: "buy" as "buy" | "sell",
    price: "",
    quantity: "",
    note: "",
  });
  const [newFiles, setNewFiles] = useState<FileList | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchJournals(filters);
      setJournals(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load journals");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(filters)]);

  const openCount = useMemo(
    () => journals.filter((j) => j.exit_price == null).length,
    [journals]
  );

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      const createRes = await createJournal({
        symbol: form.symbol.trim(),
        side: form.side,
        price: Number(form.price),
        quantity: Number(form.quantity),
        note: form.note.trim() ? form.note.trim() : undefined,
      });
      const newId = (createRes as any).journal_id as number | undefined;
      // Upload selected images (if any) after journal is created
      if (newId && newFiles && newFiles.length > 0) {
        for (const f of Array.from(newFiles)) {
          await uploadAttachment(newId, f);
        }
      }
      setForm({ symbol: "", side: "buy", price: "", quantity: "", note: "" });
      setNewFiles(null);
      await load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Create failed");
    }
  }

  async function onDelete(id: number) {
    if (!confirm("Delete this record?")) return;
    try {
      await deleteJournal(id);
      await load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Delete failed");
    }
  }

  async function onClose(id: number) {
    const v = prompt("Exit price:");
    if (!v) return;
    const price = Number(v);
    if (!isFinite(price) || price <= 0) {
      alert("Invalid price");
      return;
    }
    try {
      await closeJournal(id, price);
      await load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Close failed");
    }
  }

  async function loadAttachments(journalId: number) {
    setAttachmentsLoading((s) => ({ ...s, [journalId]: true }));
    setAttachmentsError((s) => ({ ...s, [journalId]: null }));
    try {
      const data = await listAttachments(journalId);
      setAttachments((s) => ({ ...s, [journalId]: data }));
    } catch (e) {
      setAttachmentsError((s) => ({
        ...s,
        [journalId]: e instanceof Error ? e.message : "Failed to load attachments",
      }));
    } finally {
      setAttachmentsLoading((s) => ({ ...s, [journalId]: false }));
    }
  }

  function toggleImages(journalId: number) {
    setImagesOpen((s) => {
      const next = !s[journalId];
      if (next && !attachments[journalId]) {
        void loadAttachments(journalId);
      }
      return { ...s, [journalId]: next };
    });
  }

  async function onUploadFiles(journalId: number, files: FileList | null) {
    if (!files || files.length === 0) return;
    for (const file of Array.from(files)) {
      try {
        await uploadAttachment(journalId, file);
      } catch (e) {
        alert(e instanceof Error ? e.message : "Upload failed");
        break;
      }
    }
    await loadAttachments(journalId);
  }

  async function onDeleteAttachment(journalId: number, attachmentId: number) {
    if (!confirm("Delete this image?")) return;
    try {
      await removeAttachment(journalId, attachmentId);
      await loadAttachments(journalId);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Delete image failed");
    }
  }

  return (
    <div style={{ display: "grid", gap: 16 }}>
      {/* Lightbox overlay */}
      {lightboxUrl ? (
        <div
          onClick={() => setLightboxUrl(null)}
          role="dialog"
          aria-modal="true"
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.75)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
          onKeyDown={(e) => {
            if (e.key === "Escape") setLightboxUrl(null)
          }}
          tabIndex={-1}
        >
          <img
            src={lightboxUrl}
            alt=""
            style={{
              maxWidth: "90vw",
              maxHeight: "90vh",
              boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
              borderRadius: 6,
            }}
          />
        </div>
      ) : null}

      <section>
        <h2 style={{ marginBottom: 8 }}>Filters</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(5, minmax(0, 1fr)) auto",
            gap: 8,
            alignItems: "end",
          }}
        >
          <div>
            <label>Symbol</label>
            <input
              value={filters.symbol ?? ""}
              onChange={(e) =>
                setFilters((f) => ({ ...f, symbol: e.target.value || undefined }))
              }
              placeholder="AAPL"
            />
          </div>
          <div>
            <label>Status</label>
            <select
              value={filters.status ?? ""}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  status: (e.target.value || undefined) as any,
                }))
              }
            >
              <option value="">All</option>
              <option value="open">Open</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div>
            <label>Side</label>
            <select
              value={filters.side ?? ""}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  side: (e.target.value || undefined) as any,
                }))
              }
            >
              <option value="">All</option>
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>
          <div>
            <label>Start</label>
            <input
              type="date"
              value={filters.start_date ?? ""}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  start_date: e.target.value || undefined,
                }))
              }
            />
          </div>
          <div>
            <label>End</label>
            <input
              type="date"
              value={filters.end_date ?? ""}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  end_date: e.target.value || undefined,
                }))
              }
            />
          </div>
          <button onClick={load} disabled={loading}>
            Apply
          </button>
        </div>
      </section>

      <section>
        <h2 style={{ marginBottom: 8 }}>New Trade</h2>
        <form
          onSubmit={onCreate}
          style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 8 }}
        >
          <input
            placeholder="Symbol"
            value={form.symbol}
            onChange={(e) => setForm((s) => ({ ...s, symbol: e.target.value }))}
            required
          />
          <select
            value={form.side}
            onChange={(e) => setForm((s) => ({ ...s, side: e.target.value as any }))}
          >
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
          <input
            type="number"
            step="0.01"
            placeholder="Price"
            value={form.price}
            onChange={(e) => setForm((s) => ({ ...s, price: e.target.value }))}
            required
          />
          <input
            type="number"
            step="1"
            placeholder="Qty"
            value={form.quantity}
            onChange={(e) => setForm((s) => ({ ...s, quantity: e.target.value }))}
            required
          />
          <input
            placeholder="Note (optional)"
            value={form.note}
            onChange={(e) => setForm((s) => ({ ...s, note: e.target.value }))}
          />
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp,image/avif"
            multiple
            onChange={(e) => setNewFiles(e.target.files)}
          />
          <button type="submit" disabled={loading}>
            Add
          </button>
        </form>
      </section>

      <section>
        <h2 style={{ marginBottom: 8 }}>
          Journals ({journals.length}) — Open: {openCount}
        </h2>
        {loading ? <p>Loading...</p> : null}
        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
        <div style={{ overflowX: "auto" }}>
          <table
            style={{ width: "100%", borderCollapse: "collapse" }}
          >
            <thead>
              <tr>
                <th align="left">ID</th>
                <th align="left">Symbol</th>
                <th align="left">Side</th>
                <th align="right">Price</th>
                <th align="right">Qty</th>
                <th align="left">Note</th>
                <th align="right">Exit</th>
                <th align="right">PnL</th>
                <th align="left">Created</th>
                <th align="left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {journals.map((j) => (
                <>
                  <tr key={j.journal_id}>
                    <td>{j.journal_id}</td>
                    <td>{j.symbol}</td>
                    <td>{j.side}</td>
                    <td align="right">{j.price}</td>
                    <td align="right">{j.quantity}</td>
                    <td>{j.note ?? ""}</td>
                    <td align="right">{j.exit_price ?? ""}</td>
                    <td align="right">
                      {typeof j.pnl === "number" ? j.pnl.toFixed(2) : ""}
                    </td>
                    <td>{new Date(j.created_at).toLocaleString()}</td>
                    <td>
                      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                        <button onClick={() => toggleImages(j.journal_id)}>
                          {imagesOpen[j.journal_id] ? "Hide Images" : "Images"}
                        </button>
                        {j.exit_price == null ? (
                          <button onClick={() => onClose(j.journal_id)}>Close</button>
                        ) : null}
                        <button onClick={() => onDelete(j.journal_id)}>Delete</button>
                      </div>
                    </td>
                  </tr>
                  {imagesOpen[j.journal_id] ? (
                    <tr>
                      <td colSpan={10}>
                        <div style={{ display: "grid", gap: 8 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                            <input
                              type="file"
                              accept="image/jpeg,image/png,image/webp,image/avif"
                              multiple
                              onChange={(e) =>
                                onUploadFiles(j.journal_id, e.target.files)
                              }
                            />
                            {attachmentsLoading[j.journal_id] ? <span>Loading...</span> : null}
                            {attachmentsError[j.journal_id] ? (
                              <span style={{ color: "crimson" }}>
                                {attachmentsError[j.journal_id]}
                              </span>
                            ) : null}
                          </div>
                          <div
                            style={{
                              display: "grid",
                              gridTemplateColumns: "repeat(auto-fill, minmax(100px, 1fr))",
                              gap: 8,
                            }}
                          >
                            {(attachments[j.journal_id] ?? []).map((a) => (
                              <div
                                key={a.attachment_id}
                                style={{
                                  border: "1px solid #eee",
                                  padding: 6,
                                  display: "grid",
                                  gap: 6,
                                }}
                              >
                                <img
                                  src={a.public_url}
                                  alt=""
                                  onClick={() => setLightboxUrl(a.public_url)}
                                  style={{
                                    width: "100%",
                                    height: 100,
                                    objectFit: "cover",
                                    cursor: "zoom-in",
                                  }}
                                />
                                <button
                                  onClick={() =>
                                    onDeleteAttachment(j.journal_id, a.attachment_id)
                                  }
                                >
                                  Delete
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      </td>
                    </tr>
                  ) : null}
                </>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

