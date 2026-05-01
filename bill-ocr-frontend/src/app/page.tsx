import Link from "next/link";

export default function Home() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col items-center px-4 py-20 text-center">
      <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
        Bill OCR dashboard
      </h1>
      <p className="mt-4 max-w-lg text-zinc-600 dark:text-zinc-400">
        Upload receipt images to your Python API for OCR and structured extraction, then
        browse and export records to Excel.
      </p>
      <div className="mt-10 flex flex-wrap justify-center gap-3">
        <Link
          href="/upload"
          className="rounded-lg bg-zinc-900 px-6 py-3 text-sm font-medium text-white dark:bg-zinc-100 dark:text-zinc-900"
        >
          Upload receipt
        </Link>
        <Link
          href="/bills"
          className="rounded-lg border border-zinc-300 px-6 py-3 text-sm font-medium dark:border-zinc-600"
        >
          View records
        </Link>
      </div>
      <p className="mt-12 text-xs text-zinc-500">
        Ensure FastAPI is running (default{" "}
        <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-900">127.0.0.1:8000</code>
        ). Override with{" "}
        <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-900">BILLS_API_URL</code>.
      </p>
    </div>
  );
}
