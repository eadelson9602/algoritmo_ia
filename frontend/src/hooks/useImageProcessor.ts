import { useState, useCallback } from "react";
import { processImages, downloadFile } from "../api/imageProcessor";
import type { ImageFile, ProcessImagesResponse } from "../types";
import { toast } from "sonner";

export function useImageProcessor() {
  const [images, setImages] = useState<ImageFile[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ProcessImagesResponse | null>(null);

  const addImages = useCallback((files: File[]) => {
    const newImages: ImageFile[] = files.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
      status: "pending",
    }));

    setImages((prev) => [...prev, ...newImages]);
  }, []);

  const removeImage = useCallback((index: number) => {
    setImages((prev) => {
      const newImages = [...prev];
      const removed = newImages.splice(index, 1)[0];
      if (removed.preview) {
        URL.revokeObjectURL(removed.preview);
      }
      return newImages;
    });
  }, []);

  const clearImages = useCallback(() => {
    images.forEach((img) => {
      if (img.preview) {
        URL.revokeObjectURL(img.preview);
      }
    });
    setImages([]);
    setResult(null);
  }, [images]);

  const processImagesHandler = useCallback(async () => {
    if (images.length === 0) {
      toast.error("No hay imágenes para procesar");
      return;
    }

    setIsProcessing(true);
    setResult(null);

    setImages((prev) =>
      prev.map((img) => ({ ...img, status: "uploading" as const }))
    );

    try {
      const files = images.map((img) => img.file);
      const response = await processImages(files);

      setImages((prev) =>
        prev.map((img) => ({ ...img, status: "processed" as const }))
      );

      setResult(response);
      toast.success(response.message || "Imágenes procesadas correctamente");

      return response;
    } catch (error: unknown) {
      setImages((prev) =>
        prev.map((img) => ({
          ...img,
          status: "error" as const,
          error: "Error al procesar",
        }))
      );

      const message =
        error instanceof Error
          ? error.message
          : "Error al procesar las imágenes";
      toast.error(message);

      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [images]);

  const downloadCsv = useCallback(async (filename: string) => {
    try {
      await downloadFile(filename);
      toast.success("CSV descargado correctamente");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Error al descargar el CSV";
      toast.error(message);
    }
  }, []);

  return {
    images,
    isProcessing,
    result,
    addImages,
    removeImage,
    clearImages,
    processImages: processImagesHandler,
    downloadCsv,
  };
}
