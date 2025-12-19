import { useRef, useCallback } from "react";
import { Upload, X, Image as ImageIcon } from "lucide-react";
import type { ImageFile } from "../types";

interface ImageUploaderProps {
  images: ImageFile[];
  onAddImages: (files: File[]) => void;
  onRemoveImage: (index: number) => void;
  disabled?: boolean;
}

export function ImageUploader({
  images,
  onAddImages,
  onRemoveImage,
  disabled = false,
}: ImageUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const files = event.target.files;
      if (files && files.length > 0) {
        const fileArray = Array.from(files);
        onAddImages(fileArray);
      }
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
    [onAddImages]
  );

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      const files = event.dataTransfer.files;
      if (files && files.length > 0) {
        const fileArray = Array.from(files).filter((file) =>
          file.type.startsWith("image/")
        );
        onAddImages(fileArray);
      }
    },
    [onAddImages]
  );

  const handleDragOver = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
    },
    []
  );

  return (
    <div className="bg-white rounded-lg border p-6 shadow-sm">
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => !disabled && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
          disabled={disabled}
        />

        <div className="flex flex-col items-center gap-4">
          <div className="p-4 bg-gray-100 rounded-full">
            <Upload className="w-8 h-8 text-gray-600" />
          </div>
          <div>
            <p className="text-lg font-medium text-gray-700">
              Arrastra imágenes aquí o haz clic para seleccionar
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Formatos soportados: JPG, PNG, GIF, BMP, WEBP, TIFF, SVG y más
              (máx. 10MB por archivo)
            </p>
          </div>
        </div>
      </div>

      {images.length > 0 && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              Imágenes seleccionadas ({images.length})
            </h3>
            <button
              className="px-3 py-1.5 text-sm border rounded-md hover:bg-gray-50 disabled:opacity-50"
              onClick={() => {
                images.forEach((_) => onRemoveImage(0));
              }}
              disabled={disabled}
            >
              Limpiar todo
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {images.map((image, index) => (
              <div
                key={index}
                className="relative group border rounded-lg overflow-hidden"
              >
                {image.preview ? (
                  <img
                    src={image.preview}
                    alt={image.file.name}
                    className="w-full h-32 object-cover"
                  />
                ) : (
                  <div className="w-full h-32 flex items-center justify-center bg-gray-100">
                    <ImageIcon className="w-8 h-8 text-gray-400" />
                  </div>
                )}

                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center">
                  <button
                    className="opacity-0 group-hover:opacity-100 transition-opacity bg-red-500 text-white p-2 rounded"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveImage(index);
                    }}
                    disabled={disabled}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div className="p-2 bg-white">
                  <p
                    className="text-xs text-gray-600 truncate"
                    title={image.file.name}
                  >
                    {image.file.name}
                  </p>
                  <p className="text-xs text-gray-400">
                    {(image.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  {image.status && (
                    <span
                      className={`text-xs mt-1 inline-block px-2 py-1 rounded ${
                        image.status === "processed"
                          ? "bg-green-100 text-green-800"
                          : image.status === "uploading"
                          ? "bg-blue-100 text-blue-800"
                          : image.status === "error"
                          ? "bg-red-100 text-red-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {image.status === "processed"
                        ? "Procesada"
                        : image.status === "uploading"
                        ? "Subiendo..."
                        : image.status === "error"
                        ? "Error"
                        : "Pendiente"}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
