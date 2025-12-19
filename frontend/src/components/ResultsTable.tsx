import type { ProcessedFileInfo } from "../types";
import { CheckCircle2, XCircle, Edit } from "lucide-react";
import { useState } from "react";
import { CorrectionModal } from "./CorrectionModal";

interface ResultsTableProps {
  files: ProcessedFileInfo[];
}

interface CorrectionState {
  isOpen: boolean;
  file: ProcessedFileInfo | null;
}

export function ResultsTable({ files }: ResultsTableProps) {
  const [correction, setCorrection] = useState<CorrectionState>({
    isOpen: false,
    file: null,
  });

  if (files.length === 0) return null;

  const handleCorrect = (file: ProcessedFileInfo) => {
    if (!file.path) {
      alert("No se puede corregir: falta la ruta de la imagen");
      return;
    }
    setCorrection({ isOpen: true, file });
  };

  const handleCorrectionClose = () => {
    setCorrection({ isOpen: false, file: null });
  };

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse bg-white rounded-lg border">
          <thead>
            <tr className="bg-gray-50 border-b">
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Imagen
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Tamaño
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Clasificación
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Confianza
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Acción
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {files.map((file, index) => (
              <tr key={index} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">
                  {file.filename}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {(file.size / 1024).toFixed(2)} KB
                </td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {file.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {file.classification && !file.classification.error ? (
                    <div className="flex items-center gap-2">
                      {file.classification.label === 0 ? (
                        <CheckCircle2 className="w-4 h-4 text-green-600" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-600" />
                      )}
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          file.classification.label === 0
                            ? "bg-green-100 text-green-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {file.classification.label_name_es.toUpperCase()}
                      </span>
                    </div>
                  ) : file.classification?.error ? (
                    <span className="text-xs text-orange-600">
                      Error en clasificación
                    </span>
                  ) : (
                    <span className="text-xs text-gray-400">
                      No clasificado
                    </span>
                  )}
                </td>
                <td className="px-4 py-3">
                  {file.classification && !file.classification.error ? (
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${
                            file.classification.label === 0
                              ? "bg-green-600"
                              : "bg-red-600"
                          }`}
                          style={{
                            width: `${file.classification.confidence * 100}%`,
                          }}
                        />
                      </div>
                      <span className="text-xs text-gray-600 min-w-[3rem]">
                        {(file.classification.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  ) : (
                    <span className="text-xs text-gray-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  {file.classification &&
                  !file.classification.error &&
                  file.path ? (
                    <button
                      onClick={() => handleCorrect(file)}
                      className="flex items-center gap-1 px-2 py-1 text-xs text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                      title="Corregir clasificación"
                    >
                      <Edit className="w-3 h-3" />
                      Corregir
                    </button>
                  ) : (
                    <span className="text-xs text-gray-400">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {correction.file && correction.file.classification && (
        <CorrectionModal
          isOpen={correction.isOpen}
          onClose={handleCorrectionClose}
          imagePath={correction.file.path!}
          filename={correction.file.filename}
          currentLabel={correction.file.classification.label}
          currentLabelName={correction.file.classification.label_name_es}
          onCorrected={() => {
            // Recargar o actualizar la vista si es necesario
            handleCorrectionClose();
          }}
        />
      )}
    </>
  );
}
