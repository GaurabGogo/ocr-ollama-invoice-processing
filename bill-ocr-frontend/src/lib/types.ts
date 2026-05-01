export type BillCategory =
  | "food"
  | "transport"
  | "office"
  | "utilities"
  | "healthcare"
  | "entertainment"
  | "shopping"
  | "other";

export interface BillStructured {
  date: string | null;
  vendor: string | null;
  amount: number | null;
  quantity: number | null;
  purpose: string | null;
  category: BillCategory;
}

export interface BillRecordPublic {
  id: string;
  created_at: string;
  original_filename: string;
  ocr_text: string;
  structured: BillStructured;
  validation_warnings: string[];
}

export interface BillUploadResponse {
  record: BillRecordPublic;
}

export interface BillListResponse {
  records: BillRecordPublic[];
}
