import { NextResponse } from "next/server";

import { backendUrl } from "@/lib/server-env";

export async function GET() {
  let res: Response;
  try {
    res = await fetch(`${backendUrl()}/bills`, { cache: "no-store" });
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
