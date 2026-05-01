import Link from "next/link";

const link =
  "rounded-lg px-3 py-2 text-sm font-medium text-zinc-600 transition-colors hover:bg-zinc-100 hover:text-zinc-950 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-50";

export function Nav() {
  return (
    <header className="border-b border-zinc-200 bg-white/80 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/80">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link
          href="/"
          className="font-semibold tracking-tight text-zinc-950 dark:text-zinc-50"
        >
          Bill OCR
        </Link>
        <nav className="flex gap-1">
          <Link href="/upload" className={link}>
            Upload
          </Link>
          <Link href="/bills" className={link}>
            Records
          </Link>
        </nav>
      </div>
    </header>
  );
}
