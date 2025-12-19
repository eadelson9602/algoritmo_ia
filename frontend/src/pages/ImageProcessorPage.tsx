import { useState, useEffect, useRef } from "react";
import { Loader2, Sparkles, Github, RefreshCw, BarChart3 } from "lucide-react";
import { ImageUploader, ProcessingResult } from "../components";
import { useImageProcessor } from "../hooks/useImageProcessor";
import {
  getFeedbackStats,
  triggerRetraining,
  getRetrainingStatus,
  type RetrainingStatus,
} from "../api/imageProcessor";
import { toast } from "sonner";

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
  const [feedbackStats, setFeedbackStats] = useState<{
    total_images: number;
    corrections: number;
    accuracy_estimate: number;
  } | null>(null);
  const [isRetraining, setIsRetraining] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [autoRetrainEnabled, setAutoRetrainEnabled] = useState(() => {
    // Cargar preferencia desde localStorage
    const saved = localStorage.getItem("autoRetrainEnabled");
    return saved === "true";
  });
  const [retrainingStatus, setRetrainingStatus] =
    useState<RetrainingStatus | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Cargar estadísticas de feedback al montar el componente
  useEffect(() => {
    loadFeedbackStats();
  }, []); // Cargar al montar

  // Recargar estadísticas cuando hay nuevos resultados
  useEffect(() => {
    if (result && result.success) {
      // Esperar un momento para que el backend guarde el feedback
      const timer = setTimeout(() => {
        loadFeedbackStats();
      }, 1500); // 1.5 segundos para dar tiempo al backend

      return () => clearTimeout(timer);
    }
  }, [result]);

  // Polling del estado del reentrenamiento
  useEffect(() => {
    if (isRetraining || retrainingStatus?.status === "running") {
      // Iniciar polling cada 2 segundos
      pollingIntervalRef.current = setInterval(async () => {
        try {
          const status = await getRetrainingStatus();
          setRetrainingStatus(status);

          if (status.status === "completed") {
            setIsRetraining(false);
            toast.success("Reentrenamiento completado exitosamente");
            await loadFeedbackStats();
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }
          } else if (status.status === "error") {
            setIsRetraining(false);
            toast.error(`Error en reentrenamiento: ${status.message}`);
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }
          }
        } catch (error) {
          console.error("Error obteniendo estado de reentrenamiento:", error);
        }
      }, 2000);
    } else {
      // Limpiar polling si no hay reentrenamiento en curso
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [isRetraining, retrainingStatus?.status]);

  // Verificar si se debe reentrenar automáticamente después de procesar imágenes
  useEffect(() => {
    const checkAutoRetrain = async () => {
      if (!autoRetrainEnabled || !result || !result.success) return;

      // Esperar un momento para que las estadísticas se actualicen
      setTimeout(async () => {
        // Recargar estadísticas primero
        const stats = await getFeedbackStats();
        setFeedbackStats(stats);

        if (stats && stats.total_images >= 10) {
          // Verificar que no haya un reentrenamiento en curso
          try {
            const currentStatus = await getRetrainingStatus();
            if (currentStatus.status === "running") {
              console.log("Ya hay un reentrenamiento en curso, omitiendo...");
              return;
            }

            // Iniciar reentrenamiento automático
            console.log("Iniciando reentrenamiento automático...");
            setIsRetraining(true);
            const retrainResult = await triggerRetraining(10, 10);

            if (retrainResult.success) {
              toast.info(
                "Reentrenamiento automático iniciado. Esto puede tomar varios minutos..."
              );
              // El polling se encargará de actualizar el estado
            } else {
              setIsRetraining(false);
              toast.warning(
                `No se pudo iniciar reentrenamiento automático: ${retrainResult.message}`
              );
            }
          } catch (error) {
            console.error("Error en reentrenamiento automático:", error);
            setIsRetraining(false);
          }
        }
      }, 2000); // Esperar 2 segundos para que el backend guarde el feedback
    };

    checkAutoRetrain();
  }, [result, autoRetrainEnabled]); // Ejecutar cuando hay nuevos resultados

  const loadFeedbackStats = async () => {
    setIsLoadingStats(true);
    try {
      const stats = await getFeedbackStats();
      setFeedbackStats(stats);
    } catch (error) {
      console.error("Error cargando estadísticas:", error);
    } finally {
      setIsLoadingStats(false);
    }
  };

  const handleRetrain = async () => {
    if (!feedbackStats || feedbackStats.total_images < 10) {
      toast.error(
        `Se necesitan al menos 10 imágenes procesadas para reentrenar. Actualmente hay: ${
          feedbackStats?.total_images || 0
        }`
      );
      return;
    }

    // Verificar estado actual
    try {
      const currentStatus = await getRetrainingStatus();
      if (currentStatus.status === "running") {
        toast.warning("Ya hay un reentrenamiento en curso");
        return;
      }
    } catch (error) {
      console.error("Error verificando estado:", error);
    }

    const confirmed = window.confirm(
      `¿Deseas reentrenar el modelo con ${feedbackStats.total_images} imágenes procesadas?\n\nEsto puede tomar varios minutos.`
    );

    if (!confirmed) return;

    setIsRetraining(true);
    try {
      const result = await triggerRetraining(10, 10);
      if (result.success) {
        toast.info(
          "Reentrenamiento iniciado. Esto puede tomar varios minutos..."
        );
        // El polling se encargará de actualizar el estado
      } else {
        toast.error(result.message || "Error durante el reentrenamiento");
        setIsRetraining(false);
      }
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail || "Error al iniciar el reentrenamiento"
      );
      setIsRetraining(false);
    }
  };

  const toggleAutoRetrain = () => {
    const newValue = !autoRetrainEnabled;
    setAutoRetrainEnabled(newValue);
    localStorage.setItem("autoRetrainEnabled", String(newValue));
    toast.info(
      newValue
        ? "Reentrenamiento automático activado"
        : "Reentrenamiento automático desactivado"
    );
  };

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

      // Recargar estadísticas después de procesar (con delay para que el backend guarde)
      setTimeout(() => {
        loadFeedbackStats();
      }, 2000);
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
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold text-blue-600">
                Procesador de Imágenes con IA
              </h1>
            </div>
            <a
              href="https://github.com/eadelson9602/algoritmo_ia"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              title="Ver código en GitHub"
            >
              <Github className="w-5 h-5" />
              <span className="text-sm font-medium">GitHub</span>
            </a>
          </div>
          <div className="space-y-2">
            <p className="text-gray-700 text-lg">
              Sistema de clasificación automática de imágenes de gatos usando
              inteligencia artificial
            </p>
            <p className="text-gray-600">
              Sube imágenes de gatos y el sistema las clasificará
              automáticamente como{" "}
              <span className="font-semibold text-green-600">sanos</span> o{" "}
              <span className="font-semibold text-red-600">enfermos</span>.
              Obtén resultados detallados con nivel de confianza, visualízalos
              en tabla o lista, y descarga un archivo CSV con todos los datos
              procesados.
            </p>
          </div>
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

          {/* Panel de Aprendizaje Continuo */}
          {feedbackStats !== null && (
            <div className="bg-white rounded-lg border p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  <h3 className="text-lg font-semibold text-gray-800">
                    Aprendizaje Continuo
                  </h3>
                </div>
                <div className="flex items-center gap-3">
                  {/* Toggle de Reentrenamiento Automático */}
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">Automático</span>
                    <button
                      onClick={toggleAutoRetrain}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        autoRetrainEnabled ? "bg-purple-600" : "bg-gray-300"
                      }`}
                      title={
                        autoRetrainEnabled
                          ? "Desactivar reentrenamiento automático"
                          : "Activar reentrenamiento automático"
                      }
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          autoRetrainEnabled ? "translate-x-6" : "translate-x-1"
                        }`}
                      />
                    </button>
                  </div>
                  <button
                    onClick={loadFeedbackStats}
                    disabled={isLoadingStats}
                    className="text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
                    title="Actualizar estadísticas"
                  >
                    <RefreshCw
                      className={`w-4 h-4 ${
                        isLoadingStats ? "animate-spin" : ""
                      }`}
                    />
                  </button>
                </div>
              </div>

              {/* Estado del reentrenamiento */}
              {retrainingStatus && retrainingStatus.status === "running" && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                      <span className="text-sm font-medium text-blue-800">
                        Reentrenamiento en curso...
                      </span>
                    </div>
                    <span className="text-xs text-blue-600">
                      {retrainingStatus.progress}%
                    </span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${retrainingStatus.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-blue-700 mt-1">
                    {retrainingStatus.message}
                  </p>
                </div>
              )}

              {feedbackStats && feedbackStats.total_images > 0 ? (
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="bg-blue-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">
                      Imágenes Procesadas
                    </p>
                    <p className="text-2xl font-bold text-blue-600">
                      {feedbackStats.total_images}
                    </p>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">Correcciones</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {feedbackStats.corrections}
                    </p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">
                      Precisión Estimada
                    </p>
                    <p className="text-2xl font-bold text-green-600">
                      {(feedbackStats.accuracy_estimate * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              ) : (
                <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-sm text-gray-600 text-center">
                    {feedbackStats === null
                      ? "Cargando estadísticas..."
                      : "Aún no hay imágenes procesadas. El reentrenamiento automático se activará cuando proceses 10+ imágenes."}
                  </p>
                </div>
              )}

              <div className="pt-4 border-t">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 mb-1">
                      Reentrenar Modelo (Manual)
                    </p>
                    <p className="text-xs text-gray-500">
                      {autoRetrainEnabled
                        ? "El reentrenamiento automático está activado. Se ejecutará automáticamente después de procesar 10+ imágenes."
                        : "Mejora el modelo con las imágenes procesadas y correcciones. Se requiere mínimo 10 imágenes."}
                    </p>
                  </div>
                  <button
                    onClick={handleRetrain}
                    disabled={
                      isRetraining ||
                      retrainingStatus?.status === "running" ||
                      !feedbackStats ||
                      feedbackStats.total_images < 10 ||
                      isProcessing
                    }
                    className="ml-4 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {isRetraining || retrainingStatus?.status === "running" ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Reentrenando...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-4 h-4" />
                        Reentrenar Modelo
                      </>
                    )}
                  </button>
                </div>
                {feedbackStats && feedbackStats.total_images < 10 && (
                  <p className="text-xs text-orange-600 mt-2">
                    ⚠️ Se necesitan al menos 10 imágenes procesadas para
                    reentrenar. Actualmente: {feedbackStats.total_images}{" "}
                    <button
                      onClick={loadFeedbackStats}
                      className="underline text-orange-700 hover:text-orange-900"
                      disabled={isLoadingStats}
                    >
                      {isLoadingStats ? "Actualizando..." : "Actualizar"}
                    </button>
                  </p>
                )}
                {feedbackStats &&
                  autoRetrainEnabled &&
                  feedbackStats.total_images >= 10 && (
                    <p className="text-xs text-green-600 mt-2">
                      ✓ Reentrenamiento automático activado. Se ejecutará
                      automáticamente después de procesar imágenes.
                    </p>
                  )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
