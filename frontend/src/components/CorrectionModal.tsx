import { useState } from "react";
import { X, AlertCircle } from "lucide-react";
import {
  correctClassification,
  type CorrectionRequest,
} from "../api/imageProcessor";
import { toast } from "sonner";

interface CorrectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  imagePath: string;
  filename: string;
  currentLabel: number;
  currentLabelName: string;
  onCorrected: () => void;
}

export function CorrectionModal({
  isOpen,
  onClose,
  imagePath,
  filename,
  currentLabel,
  currentLabelName,
  onCorrected,
}: CorrectionModalProps) {
  const [selectedLabel, setSelectedLabel] = useState<number | null>(null);
  const [feedback, setFeedback] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (selectedLabel === null) {
      toast.error("Por favor selecciona la clasificación correcta");
      return;
    }

    setIsSubmitting(true);
    try {
      const correction: CorrectionRequest = {
        image_path: imagePath,
        corrected_label: selectedLabel,
        corrected_label_name: selectedLabel === 0 ? "sano" : "enfermo",
        user_feedback: feedback || undefined,
      };

      await correctClassification(correction);
      toast.success(
        "Corrección guardada. El modelo se mejorará con este feedback."
      );
      onCorrected();
      onClose();
      setSelectedLabel(null);
      setFeedback("");
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail || "Error al guardar la corrección"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Corregir Clasificación</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Imagen:</p>
            <p className="font-medium">{filename}</p>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-2">
              Clasificación actual:{" "}
              <span
                className={`font-semibold ${
                  currentLabel === 0 ? "text-green-600" : "text-red-600"
                }`}
              >
                {currentLabelName}
              </span>
            </p>
          </div>

          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">
              ¿Cuál es la clasificación correcta?
            </p>
            <div className="space-y-2">
              <label className="flex items-center gap-2 p-3 border rounded-md cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="label"
                  value="0"
                  checked={selectedLabel === 0}
                  onChange={() => setSelectedLabel(0)}
                  className="w-4 h-4 text-green-600"
                />
                <span className="font-semibold text-green-600">Sano</span>
              </label>
              <label className="flex items-center gap-2 p-3 border rounded-md cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="label"
                  value="1"
                  checked={selectedLabel === 1}
                  onChange={() => setSelectedLabel(1)}
                  className="w-4 h-4 text-red-600"
                />
                <span className="font-semibold text-red-600">Enfermo</span>
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Comentario (opcional):
            </label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Describe por qué esta corrección es necesaria..."
              className="w-full px-3 py-2 border rounded-md resize-none"
              rows={3}
            />
          </div>

          <div className="flex items-start gap-2 p-3 bg-blue-50 rounded-md">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-blue-800">
              Esta corrección ayudará a mejorar la precisión del modelo. El
              sistema reentrenará automáticamente cuando haya suficientes
              correcciones.
            </p>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border rounded-md hover:bg-gray-50 disabled:opacity-50"
              disabled={isSubmitting}
            >
              Cancelar
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || selectedLabel === null}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isSubmitting ? "Guardando..." : "Guardar Corrección"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
