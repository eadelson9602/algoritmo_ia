export interface ImageFile {
  file: File;
  preview?: string;
  status?: "pending" | "uploading" | "processed" | "error";
  error?: string;
}

export interface Classification {
  label: number; // 0 para healthy, 1 para sick
  label_name: string; // "healthy" o "sick"
  label_name_es: string; // "sano" o "enfermo"
  confidence: number; // 0-1
  error?: string;
}

export interface ProcessedFileInfo {
  filename: string;
  size: number;
  status: string;
  classification?: Classification | null;
  path?: string; // Ruta de la imagen en el servidor (necesaria para correcciones)
}

export interface ProcessImagesResponse {
  success: boolean;
  message: string;
  processed_files: ProcessedFileInfo[];
  errors?: string[];
  csv_url: string;
  csv_filename: string;
}
