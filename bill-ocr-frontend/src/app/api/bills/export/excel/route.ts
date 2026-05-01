import { NextResponse } from "next/server";

import { backendUrl } from "@/lib/server-env";

export async function GET() {
  let res: Response;
  try {
    res = await fetch(`${backendUrl()}/bills/export/excel`, { cache: "no-store" });
  } catch {
    return NextResponse.json(
      { detail: "Cannot reach bills API. Is the backend running?" },
      { status: 502 },
    );
  }

  if (!res.ok) {
    const text = await res.text();
    return NextResponse.json(
      { detail: text || res.statusText },
      { status: res.status },
    );
  }

  const buf = await res.arrayBuffer();
  return new NextResponse(buf, {
    status: 200,
    headers: {
      "Content-Type":
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "Content-Disposition": 'attachment; filename="bills_export.xlsx"',
    },
  });
}
