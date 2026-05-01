import { NextResponse } from "next/server";

import { backendUrl } from "@/lib/server-env";

type Ctx = { params: Promise<{ id: string }> };

export async function GET(_request: Request, context: Ctx) {
  const { id } = await context.params;
  if (!id) {
    return NextResponse.json({ detail: "Missing id" }, { status: 400 });
  }

  let res: Response;
  try {
    res = await fetch(`${backendUrl()}/bills/${encodeURIComponent(id)}`, {
      cache: "no-store",
    });
  } catch {
    return NextResponse.json(
      { detail: "Cannot reach bills API. Is the backend running?" },
      { status: 502 },
    );
  }

  const body = await res.text();
  return new NextResponse(body, {
    status: res.status,
    headers: {
      "Content-Type": res.headers.get("content-type") ?? "application/json",
    },
  });
}
