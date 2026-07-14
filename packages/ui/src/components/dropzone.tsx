import * as React from "react";
import { Upload, AlertCircle } from "lucide-react";
import { cn } from "../utils/cn.js";

export interface DropzoneProps {
  onFileSelect: (files: File[]) => void;
  maxSize?: number; // In bytes (default 10MB)
  accept?: string[]; // e.g., ["application/pdf", "text/plain"]
  disabled?: boolean;
  className?: string;
}

export const Dropzone: React.FC<DropzoneProps> = ({
  onFileSelect,
  maxSize = 10 * 1024 * 1024,
  accept = [
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ],
  disabled = false,
  className,
}) => {
  const [isDragActive, setIsDragActive] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled) return;
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const validateFiles = (files: File[]): File[] => {
    const validFiles: File[] = [];
    setError(null);

    for (const file of files) {
      if (file.size > maxSize) {
        setError(
          `File ${file.name} exceeds the max size limit of ${(maxSize / (1024 * 1024)).toFixed(0)}MB.`,
        );
        continue;
      }
      if (accept.length > 0 && !accept.includes(file.type) && !file.name.endsWith(".docx")) {
        setError(`File type ${file.type || "unknown"} is not supported.`);
        continue;
      }
      validFiles.push(file);
    }

    return validFiles;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      const validated = validateFiles(droppedFiles);
      if (validated.length > 0) {
        onFileSelect(validated);
      }
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled) return;
    if (e.target.files && e.target.files[0]) {
      const selectedFiles = Array.from(e.target.files);
      const validated = validateFiles(selectedFiles);
      if (validated.length > 0) {
        onFileSelect(validated);
      }
    }
  };

  const triggerFileInput = () => {
    if (disabled) return;
    fileInputRef.current?.click();
  };

  return (
    <div className={cn("w-full", className)}>
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileInput}
        className={cn(
          "relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-zinc-800 bg-zinc-950/50 p-8 text-center cursor-pointer transition-all duration-300 hover:bg-zinc-950 hover:border-violet-500/50",
          {
            "border-violet-500 bg-violet-950/10 scale-[1.01]": isDragActive,
            "opacity-50 pointer-events-none": disabled,
          },
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          multiple
          accept={accept.join(",")}
          onChange={handleFileInputChange}
          disabled={disabled}
        />

        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 mb-4 transition-transform duration-300 group-hover:scale-110">
          <Upload className="h-6 w-6 text-zinc-300" />
        </div>

        <h3 className="text-base font-semibold text-zinc-200 mb-1">Drag & drop your files here</h3>
        <p className="text-xs text-zinc-500 max-w-xs mb-3">
          Support for PDF, Word (.docx), or plain text files up to 10MB
        </p>
        <div className="inline-flex items-center rounded-md bg-zinc-900 border border-zinc-800 px-3 py-1 text-xs text-zinc-300">
          Or browse files
        </div>
      </div>

      {error && (
        <div className="mt-3 flex items-center gap-2 rounded-lg bg-red-950/20 border border-red-900/50 p-3 text-xs text-red-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
