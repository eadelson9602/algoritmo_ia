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

export interface CorrectionRequest {
  image_path: string;
  corrected_label: number; // 0=sano, 1=enfermo
  corrected_label_name?: string;
  user_feedback?: string;
}

export async function correctClassification(
  correction: CorrectionRequest
): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.post("/api/v1/feedback/correct", correction);
  return response.data;
}

export interface FeedbackStats {
  total_images: number;
  corrections: number;
  accuracy_estimate: number;
}

export async function getFeedbackStats(): Promise<FeedbackStats> {
  const response = await apiClient.get<FeedbackStats>("/api/v1/feedback/stats");
  return response.data;
}

export async function triggerRetraining(
  epochs: number = 10,
  minFeedback: number = 10
): Promise<{
  success: boolean;
  message: string;
  state?: any;
  output?: string;
  error?: string;
}> {
  const response = await apiClient.post("/api/v1/model/retrain", null, {
    params: { epochs, min_feedback: minFeedback },
  });
  return response.data;
}

export interface RetrainingStatus {
  status: "idle" | "running" | "completed" | "error";
  progress: number;
  message: string;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export async function getRetrainingStatus(): Promise<RetrainingStatus> {
  const response = await apiClient.get<RetrainingStatus>(
    "/api/v1/model/retrain/status"
  );
  return response.data;
}
