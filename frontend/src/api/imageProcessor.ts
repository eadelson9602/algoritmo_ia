import axios from "axios";
import type { ProcessImagesResponse } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 300000, // 5 minutos para procesamiento de imágenes
});

export async function processImages(
  files: File[]
): Promise<ProcessImagesResponse> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await apiClient.post<ProcessImagesResponse>(
    "/api/v1/images/process",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

export async function downloadFile(filename: string): Promise<void> {
  const response = await apiClient.get(`/api/v1/files/download/${filename}`, {
    responseType: "blob",
  });

  const blob = response.data;
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
