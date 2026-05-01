"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import type { BillUploadResponse } from "@/lib/types";

async function errorMessage(res: Response): Promise<string> {
  try {
    const data = await res.json();
    const d = data.detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) return d.map((x) => JSON.stringify(x)).join("; ");
    return JSON.stringify(data);
  } catch {
    return res.statusText || "Request failed";
  }
}

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [result, setResult] = useState<BillUploadResponse | null>(null);

  const localPreviewUrl = useMemo(
    () => (file ? URL.createObjectURL(file) : null),
    [file],
  );

  useEffect(() => {
    return () => {
      if (localPreviewUrl) URL.revokeObjectURL(localPreviewUrl);
    };
  }, [localPreviewUrl]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) {
      setFile(f);
      setErr(null);
      setResult(null);
    }
  }, []);

  const onFile = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setErr(null);
      setResult(null);
    }
  }, []);

  const submit = async () => {
    if (!file) {
      setErr("Choose an image first.");
      return;
    }
    setBusy(true);
    setErr(null);
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch("/api/bills/upload", { method: "POST", body: fd });
      if (!res.ok) {
        setErr(await errorMessage(res));
        return;
      }
      const data = (await res.json()) as BillUploadResponse;
      setResult(data);
    } catch {
      setErr("Network error — check the Next dev server and API proxy.");
    } finally {
      setBusy(false);
    }
  };

  const s = result?.record.structured;

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-semibold tracking-tight">Upload receipt</h1>
      <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        JPEG, PNG, WebP, TIFF, or BMP. Processing runs on your bills API (Tesseract +
        Ollama).
      </p>

      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        className="mt-8 rounded-xl border-2 border-dashed border-zinc-300 bg-zinc-50/50 p-10 text-center transition-colors hover:border-zinc-400 dark:border-zinc-700 dark:bg-zinc-900/40 dark:hover:border-zinc-600"
      >
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/tiff,image/bmp"
          onChange={onFile}
          className="hidden"
          id="file-input"
        />
        <label
          htmlFor="file-input"
          className="cursor-pointer text-sm font-medium text-zinc-700 underline-offset-4 hover:underline dark:text-zinc-300"
        >
          Choose file
        </label>
        <p className="mt-2 text-xs text-zinc-500">or drag and drop here</p>
        {file && (
          <p className="mt-4 truncate text-sm font-medium text-zinc-900 dark:text-zinc-100">
            {file.name}{" "}
            <span className="font-normal text-zinc-500">
              ({(file.size / 1024).toFixed(1)} KB)
            </span>
          </p>
        )}
      </div>

      {localPreviewUrl && (
        <div className="mt-6">
          <p className="mb-2 text-sm font-medium text-zinc-600 dark:text-zinc-400">
            Preview
          </p>
          <div className="overflow-hidden rounded-xl border border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={localPreviewUrl}
              alt=""
              className="mx-auto max-h-[min(55vh,480px)] w-full object-contain"
            />
          </div>
        </div>
      )}

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          type="button"
          disabled={busy || !file}
          onClick={submit}
          className="rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900"
        >
          {busy ? "Processing…" : "Upload & extract"}
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => {
            setFile(null);
            setErr(null);
            setResult(null);
          }}
          className="rounded-lg border border-zinc-300 px-4 py-2.5 text-sm font-medium dark:border-zinc-600"
        >
          Clear
        </button>
        <Link
          href="/bills"
          className="inline-flex items-center rounded-lg border border-zinc-300 px-4 py-2.5 text-sm font-medium dark:border-zinc-600"
        >
          View all records
        </Link>
      </div>

      {err && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-900 dark:border-red-900 dark:bg-red-950/50 dark:text-red-100">
          {err}
        </div>
      )}

      {result && s && (
        <div className="mt-8 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
          <div className="mb-6 overflow-hidden rounded-lg border border-zinc-100 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900">
            <p className="border-b border-zinc-100 px-3 py-2 text-xs font-medium uppercase tracking-wide text-zinc-500 dark:border-zinc-800">
              Stored image
            </p>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`/api/bills/${encodeURIComponent(result.record.id)}/image`}
              alt=""
              className="mx-auto max-h-[min(40vh,360px)] w-full object-contain"
            />
          </div>
          <h2 className="text-lg font-semibold">Extracted</h2>
          <dl className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-zinc-500">Vendor</dt>
              <dd className="font-medium">{s.vendor ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-zinc-500">Amount</dt>
              <dd className="font-medium">
                {s.amount != null ? s.amount : "—"}
              </dd>
            </div>
            <div>
              <dt className="text-zinc-500">Date</dt>
              <dd className="font-medium">{s.date ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-zinc-500">Category</dt>
              <dd className="font-medium capitalize">{s.category}</dd>
            </div>
          </dl>
          <div className="mt-6 flex flex-wrap gap-2">
            <Link
              href="/bills"
              className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white dark:bg-zinc-100 dark:text-zinc-900"
            >
              Open records
            </Link>
            <button
              type="button"
              className="rounded-lg border border-zinc-300 px-4 py-2 text-sm dark:border-zinc-600"
              onClick={() =>
                navigator.clipboard.writeText(
                  JSON.stringify(result.record.structured, null, 2),
                )
              }
            >
              Copy structured JSON
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
