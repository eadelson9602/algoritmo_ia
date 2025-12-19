import type { ProcessedFileInfo } from "../types";
import { CheckCircle2, XCircle } from "lucide-react";

interface ResultsTableProps {
  files: ProcessedFileInfo[];
}

export function ResultsTable({ files }: ResultsTableProps) {
  if (files.length === 0) return null;

  return (
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
                  <span className="text-xs text-gray-400">No clasificado</span>
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
