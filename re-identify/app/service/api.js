import axios from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const compareImages = async (
  sourceImage,
  targetImage,
  similarityThreshold = 70
) => {
  const formData = new FormData();
  formData.append(
    "image_source",
    sourceImage,
    sourceImage.name || "source.jpg"
  );
  formData.append(
    "image_target",
    targetImage,
    targetImage.name || "target.jpg"
  );

  try {
    const response = await api.post("/api/v1/compare-faces/", formData, {
      params: { similarity_threshold: similarityThreshold },
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    const axiosError = error;
    let errorMessage = "Une erreur inconnue est survenue";

    if (axiosError.response.data) {
      // Safely access error details with proper type checking
      errorMessage =
        axiosError.response.data.detail ||
        axiosError.response.data.error ||
        axiosError.response.data.message ||
        "Erreur du serveur";
    } else if (axiosError.request) {
      errorMessage = "Pas de réponse du serveur";
    } else {
      errorMessage = axiosError.message || "Erreur de configuration";
    }

    throw new Error(errorMessage);
  }
};
