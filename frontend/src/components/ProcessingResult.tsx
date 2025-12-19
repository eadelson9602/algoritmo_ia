import { Download, CheckCircle2, AlertCircle, Table2 } from "lucide-react";
import type { ProcessImagesResponse } from "../types";
import { ResultsTable } from "./ResultsTable";
import { useState } from "react";

interface ProcessingResultProps {
  result: ProcessImagesResponse;
  onDownload: (filename: string) => void;
}

export function ProcessingResult({
  result,
  onDownload,
}: ProcessingResultProps) {
  const [viewMode, setViewMode] = useState<"list" | "table">("table");

  return (
    <div className="bg-white rounded-lg border p-6 shadow-sm">
      <div className="mb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          {result.success ? (
            <>
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              Procesamiento Completado
            </>
          ) : (
            <>
              <AlertCircle className="w-5 h-5 text-red-600" />
              Error en el Procesamiento
            </>
          )}
        </h2>
      </div>

      <div className="space-y-4">
        <p className="text-gray-700">{result.message}</p>

        {result.processed_files && result.processed_files.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold">
                Archivos procesados ({result.processed_files.length}):
              </h4>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode("table")}
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors flex items-center gap-1.5 ${
                    viewMode === "table"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  <Table2 className="w-4 h-4" />
                  Tabla
                </button>
                <button
                  onClick={() => setViewMode("list")}
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    viewMode === "list"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  Lista
                </button>
              </div>
            </div>

            {viewMode === "table" ? (
              <ResultsTable files={result.processed_files} />
            ) : (
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                {result.processed_files.map((file, index) => (
                  <li key={index} className="mb-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium">{file.filename}</span>
                      <span className="text-gray-400">
                        - {(file.size / 1024).toFixed(2)} KB
                      </span>
                      <span className="text-green-600">- {file.status}</span>
                      {file.classification && !file.classification.error && (
                        <span
                          className={`px-2 py-1 rounded text-xs font-semibold ${
                            file.classification.label === 0
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {file.classification.label_name_es.toUpperCase()} (
                          {(file.classification.confidence * 100).toFixed(1)}%)
                        </span>
                      )}
                      {file.classification?.error && (
                        <span className="text-xs text-orange-600">
                          (Error en clasificación)
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {result.errors && result.errors.length > 0 && (
          <div>
            <h4 className="font-semibold mb-2 text-red-600">Errores:</h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-red-600">
              {result.errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}

        {result.csv_url && result.csv_filename && (
          <div className="pt-4 border-t">
            <button
              onClick={() => onDownload(result.csv_filename)}
              className="w-full bg-primary text-white px-4 py-2 rounded-md hover:bg-primary/90 flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
              Descargar CSV: {result.csv_filename}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
