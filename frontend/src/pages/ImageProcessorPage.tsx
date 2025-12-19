import { useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { ImageUploader, ProcessingResult } from "../components";
import { useImageProcessor } from "../hooks/useImageProcessor";

export default function ImageProcessorPage() {
  const {
    images,
    isProcessing,
    result,
    addImages,
    removeImage,
    clearImages,
    processImages,
    downloadCsv,
  } = useImageProcessor();

  const [progress, setProgress] = useState(0);

  const handleProcess = async () => {
    setProgress(0);

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 500);

    try {
      await processImages();
      setProgress(100);
    } catch (error) {
      clearInterval(progressInterval);
      setProgress(0);
    } finally {
      setTimeout(() => clearInterval(progressInterval), 1000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8 px-4 max-w-6xl">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold">
              Procesador de Imágenes con IA
            </h1>
          </div>
          <p className="text-gray-600">
            Sube imágenes para procesarlas con inteligencia artificial y genera
            un CSV con los resultados
          </p>
        </div>

        <div className="space-y-6">
          <ImageUploader
            images={images}
            onAddImages={addImages}
            onRemoveImage={removeImage}
            disabled={isProcessing}
          />

          {images.length > 0 && (
            <div className="bg-white rounded-lg border p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">
                    {images.length} imagen{images.length !== 1 ? "es" : ""}{" "}
                    lista
                    {images.length !== 1 ? "s" : ""} para procesar
                  </p>
                </div>
                <div className="flex gap-3">
                  <button
                    className="px-4 py-2 border text-black rounded-md hover:bg-gray-50 disabled:opacity-50"
                    onClick={clearImages}
                    disabled={isProcessing}
                  >
                    Limpiar
                  </button>
                  <button
                    onClick={handleProcess}
                    disabled={isProcessing || images.length === 0}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Procesando...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Procesar Imágenes
                      </>
                    )}
                  </button>
                </div>
              </div>

              {isProcessing && (
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-sm text-gray-600 mt-2 text-center">
                    {progress}% completado
                  </p>
                </div>
              )}
            </div>
          )}

          {result && (
            <ProcessingResult result={result} onDownload={downloadCsv} />
          )}
        </div>
      </div>
    </div>
  );
}
