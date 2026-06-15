export type IngestionStatus = "queued" | "processing" | "processed" | "failed";

export interface DocumentMetadata {
  title: string;
  author?: string;
  pageCount?: number;
  fileSize: number;
  mimeType: string;
  checksum: string;
}

export interface Document {
  id: string;
  name: string;
  storageUrl: string;
  status: "queued" | "UPLOADING" | "PARSING" | "CLEANING" | "CHUNKING" | "EMBEDDING" | "INDEXING" | "ANALYZING" | "COMPLETED" | "FAILED" | "processing" | "processed" | "failed";
  metadata: DocumentMetadata;
  createdAt: string;
  updatedAt: string;
  progress_percentage?: number;
  userId?: string;
  error?: string | null;
}

export interface UploadParams {
  name: string;
  fileSize: number;
  mimeType: string;
}

export interface IngestDocumentResponse {
  documentId: string;
  status: IngestionStatus;
  uploadUrl?: string; // Pre-signed S3/R2 upload URL
}
