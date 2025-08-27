export interface SarsaParams {
  mode: "user" | "optimized";
  alpha: number;
  gamma: number;
  eps: number;
  eps_decay: number;
  eps_min: number;
  training_runs: number;
  maxStepsPerEpisode: number;
  test_episodes: number;
}

export interface TrainingRun {
  run_id: string;
  user_id: number;
  algorithm: string;
  params: SarsaParams;
  training_metrics: any;
  test_metrics: any;
  system_metrics: any;
  learning_stability: any;
  brute_force_metrics: any;
  improvement_metrics: any;
  plots: string[];
  model_path: string;
  execution_time: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface TrainingRunSummary {
  run_id: string;
  algorithm: string;
  success_rate: number | null;
  avg_steps: number | null;
  execution_time: number | null;
  created_at: string;
}

export interface StatisticsResponse {
  total_runs: number;
  algorithms: string[];
  best_success_rate: number;
  best_avg_steps: number;
  total_execution_time: number;
}

export interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  message?: string;
}
