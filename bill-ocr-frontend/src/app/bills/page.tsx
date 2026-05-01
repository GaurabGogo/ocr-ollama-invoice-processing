"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { BillDetailPanel } from "@/components/BillDetailPanel";
import type { BillListResponse, BillRecordPublic } from "@/lib/types";

async function errorMessage(res: Response): Promise<string> {
  try {
    const data = await res.json();
    const d = data.detail;
    if (typeof d === "string") return d;
    return JSON.stringify(data);
  } catch {
    return res.statusText || "Request failed";
  }
}

async function fetchBillRecords(): Promise<
  { ok: true; records: BillRecordPublic[] } | { ok: false; message: string }
> {
  try {
    const res = await fetch("/api/bills");
    if (!res.ok) {
      return { ok: false, message: await errorMessage(res) };
    }
    const data = (await res.json()) as BillListResponse;
    return { ok: true, records: data.records ?? [] };
  } catch {
    return { ok: false, message: "Network error — is Next.js running?" };
  }
}

export default function BillsPage() {
  const [records, setRecords] = useState<BillRecordPublic[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [detail, setDetail] = useState<BillRecordPublic | null>(null);
  const [exportBusy, setExportBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchBillRecords().then((r) => {
      if (cancelled) return;
      setLoading(false);
      if (r.ok) {
        setRecords(r.records);
        setErr(null);
      } else {
        setErr(r.message);
        setRecords([]);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const refresh = async () => {
    setLoading(true);
    setErr(null);
    const r = await fetchBillRecords();
    setLoading(false);
    if (r.ok) {
      setRecords(r.records);
      setErr(null);
    } else {
      setErr(r.message);
      setRecords([]);
    }
  };

  const exportExcel = async () => {
    setExportBusy(true);
    try {
      const res = await fetch("/api/bills/export/excel");
      if (!res.ok) {
        setErr(await errorMessage(res));
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "bills_export.xlsx";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setErr("Export failed.");
    } finally {
      setExportBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Bill records</h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Data from your FastAPI store (SQLite).
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => void refresh()}
            disabled={loading}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
          >
            {loading ? "Loading…" : "Refresh"}
          </button>
          <button
            type="button"
            onClick={() => void exportExcel()}
            disabled={exportBusy || records.length === 0}
            className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium disabled:opacity-40 dark:border-zinc-600"
          >
            {exportBusy ? "Exporting…" : "Export Excel"}
          </button>
          <Link
            href="/upload"
            className="inline-flex items-center rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium dark:border-zinc-600"
          >
            New upload
          </Link>
        </div>
      </div>

      {err && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-900 dark:border-red-900 dark:bg-red-950/50 dark:text-red-100">
          {err}
        </div>
      )}

      <div className="mt-8 overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead className="border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900/80">
            <tr>
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium">Vendor</th>
              <th className="px-4 py-3 font-medium">Amount</th>
              <th className="px-4 py-3 font-medium">Category</th>
              <th className="px-4 py-3 font-medium">File</th>
              <th className="px-4 py-3 font-medium">Flags</th>
              <th className="px-4 py-3 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && records.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-zinc-500">
                  Loading…
                </td>
              </tr>
            ) : records.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-zinc-500">
                  No bills yet.{" "}
                  <Link href="/upload" className="font-medium underline">
                    Upload one
                  </Link>
                  .
                </td>
              </tr>
            ) : (
              records.map((r) => (
                <tr
                  key={r.id}
                  className="border-b border-zinc-100 dark:border-zinc-800/80"
                >
                  <td className="whitespace-nowrap px-4 py-3 text-zinc-600 dark:text-zinc-300">
                    {r.structured.date ?? "—"}
                  </td>
                  <td className="max-w-[140px] truncate px-4 py-3 font-medium">
                    {r.structured.vendor ?? "—"}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3">
                    {r.structured.amount != null ? r.structured.amount : "—"}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 capitalize">
                    {r.structured.category}
                  </td>
                  <td className="max-w-[160px] truncate px-4 py-3 text-zinc-600 dark:text-zinc-400">
                    {r.original_filename}
                  </td>
                  <td className="px-4 py-3">
                    {r.validation_warnings.length > 0 ? (
                      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-900 dark:bg-amber-950 dark:text-amber-100">
                        {r.validation_warnings.length} warning
                        {r.validation_warnings.length !== 1 ? "s" : ""}
                      </span>
                    ) : (
                      <span className="text-zinc-400">—</span>
                    )}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-right">
                    <button
                      type="button"
                      onClick={() => setDetail(r)}
                      className="rounded-lg border border-zinc-300 px-3 py-1.5 text-xs font-medium hover:bg-zinc-50 dark:border-zinc-600 dark:hover:bg-zinc-900"
                    >
                      Details
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <BillDetailPanel record={detail} onClose={() => setDetail(null)} />
    </div>
  );
}
