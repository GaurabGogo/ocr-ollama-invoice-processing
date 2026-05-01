"use client";

import type { BillRecordPublic } from "@/lib/types";

type Props = {
  record: BillRecordPublic | null;
  onClose: () => void;
};

export function BillDetailPanel({ record, onClose }: Props) {
  if (!record) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="detail-title"
    >
      <button
        type="button"
        className="absolute inset-0 cursor-default"
        aria-label="Close"
        onClick={onClose}
      />
      <div className="relative max-h-[90vh] w-full max-w-2xl overflow-hidden rounded-xl border border-zinc-200 bg-background shadow-xl dark:border-zinc-800">
        <div className="flex items-center justify-between border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
          <h2 id="detail-title" className="truncate text-lg font-semibold">
            {record.structured.vendor ?? record.original_filename}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
          >
            Close
          </button>
        </div>
        <div className="max-h-[calc(90vh-3.5rem)] overflow-y-auto p-4 space-y-4">
          <div>
            <p className="mb-2 text-sm font-medium text-zinc-600 dark:text-zinc-400">
              Uploaded image
            </p>
            <div className="overflow-hidden rounded-lg border border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`/api/bills/${encodeURIComponent(record.id)}/image`}
                alt={`Receipt ${record.original_filename}`}
                className="mx-auto max-h-[min(50vh,420px)] w-full object-contain"
              />
            </div>
          </div>
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <Detail label="Date" value={record.structured.date ?? "—"} />
            <Detail label="Vendor" value={record.structured.vendor ?? "—"} />
            <Detail
              label="Amount"
              value={
                record.structured.amount != null
                  ? String(record.structured.amount)
                  : "—"
              }
            />
            <Detail
              label="Qty"
              value={
                record.structured.quantity != null
                  ? String(record.structured.quantity)
                  : "—"
              }
            />
            <Detail label="Purpose" value={record.structured.purpose ?? "—"} span />
            <Detail label="Category" value={record.structured.category} />
            <Detail label="Created" value={record.created_at} span />
          </dl>
          {record.validation_warnings.length > 0 && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-100">
              <p className="font-medium">Warnings</p>
              <ul className="mt-1 list-inside list-disc">
                {record.validation_warnings.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            </div>
          )}
          <div>
            <p className="mb-2 text-sm font-medium text-zinc-600 dark:text-zinc-400">
              OCR text
            </p>
            <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-zinc-100 p-3 text-xs dark:bg-zinc-900">
              {record.ocr_text || "(empty)"}
            </pre>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className={secondaryBtn}
              onClick={() =>
                navigator.clipboard.writeText(JSON.stringify(record, null, 2))
              }
            >
              Copy JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Detail({
  label,
  value,
  span,
}: {
  label: string;
  value: string;
  span?: boolean;
}) {
  return (
    <div className={span ? "col-span-2" : ""}>
      <dt className="text-xs uppercase tracking-wide text-zinc-500">{label}</dt>
      <dd className="mt-0.5 font-medium text-zinc-900 dark:text-zinc-100">
        {value}
      </dd>
    </div>
  );
}

const secondaryBtn =
  "rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-50 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800";
