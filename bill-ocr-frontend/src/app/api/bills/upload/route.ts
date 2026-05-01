import { NextResponse } from "next/server";

import { backendUrl } from "@/lib/server-env";

export async function POST(request: Request) {
  let incoming: FormData;
  try {
    incoming = await request.formData();
  } catch {
    return NextResponse.json({ detail: "Invalid form data" }, { status: 400 });
  }

  const file = incoming.get("file");
  if (!(file instanceof File) || file.size === 0) {
    return NextResponse.json({ detail: "Missing or empty file" }, { status: 400 });
  }

  const forward = new FormData();
  forward.append("file", file, file.name);

  let res: Response;
  try {
    res = await fetch(`${backendUrl()}/bills/upload`, {
      method: "POST",
      body: forward,
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
