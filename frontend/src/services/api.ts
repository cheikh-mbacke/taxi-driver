import axios from "axios";
import type {
  SarsaParams,
  TrainingRun,
  TrainingRunSummary,
  StatisticsResponse,
} from "../types/api";

const API_BASE_URL = ""; // Retirer le préfixe /api car le proxy Vite s'en charge

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const apiService = {
  // Health check
  health: async () => {
    const response = await api.get("/health");
    return response.data;
  },

  // SARSA training
  runSarsa: async (params: SarsaParams) => {
    const response = await api.post("/sarsa", params);
    return response.data;
  },

  // Database routes
  getTrainingRuns: async (
    skip = 0,
    limit = 100
  ): Promise<TrainingRunSummary[]> => {
    const response = await api.get(
      `/database/runs?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  getTrainingRun: async (runId: string): Promise<TrainingRun> => {
    const response = await api.get(`/database/runs/${runId}`);
    return response.data;
  },

  getBestRuns: async (limit = 10): Promise<TrainingRunSummary[]> => {
    const response = await api.get(`/database/runs/best?limit=${limit}`);
    return response.data;
  },

  getStatistics: async (): Promise<StatisticsResponse> => {
    const response = await api.get("/database/statistics");
    return response.data;
  },

  deleteTrainingRun: async (runId: string) => {
    const response = await api.delete(`/database/runs/${runId}`);
    return response.data;
  },

  // Get plot images
  getPlotImage: (plotPath: string) => {
    return `http://localhost:8000${plotPath}`;
  },
};

export default apiService;
