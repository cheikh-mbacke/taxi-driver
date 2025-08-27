import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Alert,
  LinearProgress,
  Grid,
  Switch,
  FormControlLabel,
} from "@mui/material";
import { PlayArrow, Stop } from "@mui/icons-material";
import type { SarsaParams } from "../types/api";
import { apiService } from "../services/api";

interface TrainingFormProps {
  onTrainingStart: () => void;
  onTrainingComplete: () => void;
  isTraining: boolean;
}

const TrainingForm: React.FC<TrainingFormProps> = ({
  onTrainingStart,
  onTrainingComplete,
  isTraining,
}) => {
  const [params, setParams] = useState<SarsaParams>({
    mode: "optimized",
    alpha: 0.12,
    gamma: 0.99,
    eps: 1.0,
    eps_decay: 0.9995,
    eps_min: 0.001,
    training_runs: 1000,
    maxStepsPerEpisode: 200,
    test_episodes: 100,
  });

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleModeChange = (mode: "user" | "optimized") => {
    setParams((prev) => ({
      ...prev,
      mode,
      // Apply optimized params if mode is optimized
      ...(mode === "optimized" && {
        alpha: 0.12,
        gamma: 0.99,
        eps: 1.0,
        eps_decay: 0.9995,
        eps_min: 0.001,
        training_runs: 6000,
        test_episodes: 250,
      }),
    }));
  };

  const handleParamChange = (field: keyof SarsaParams, value: any) => {
    setParams((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      onTrainingStart();
      const result = await apiService.runSarsa(params);

      if (result.status === "success") {
        setSuccess(
          `Entraînement terminé avec succès! Run ID: ${result.run_id}`
        );
        onTrainingComplete();
      } else {
        setError(result.message || "Erreur lors de l'entraînement");
        onTrainingComplete();
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Erreur de connexion");
      onTrainingComplete();
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      {/* Mode Selection */}
      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Mode d'entraînement</InputLabel>
        <Select
          value={params.mode}
          label="Mode d'entraînement"
          onChange={(e) =>
            handleModeChange(e.target.value as "user" | "optimized")
          }
          disabled={isTraining}
        >
          <MenuItem value="optimized">
            🎯 Optimisé (Paramètres validés - Recommandé)
          </MenuItem>
          <MenuItem value="user">⚙️ Personnalisé (Paramètres manuels)</MenuItem>
        </Select>
      </FormControl>

      {/* Training Progress */}
      {isTraining && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Entraînement en cours...
          </Typography>
          <LinearProgress />
        </Box>
      )}

      {/* Parameters Grid */}
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Épisodes d'entraînement"
            type="number"
            value={params.training_runs}
            onChange={(e) =>
              handleParamChange("training_runs", parseInt(e.target.value))
            }
            disabled={isTraining || params.mode === "optimized"}
            inputProps={{ min: 100, max: 10000 }}
            helperText="Nombre d'épisodes pour l'entraînement"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Épisodes de test"
            type="number"
            value={params.test_episodes}
            onChange={(e) =>
              handleParamChange("test_episodes", parseInt(e.target.value))
            }
            disabled={isTraining || params.mode === "optimized"}
            inputProps={{ min: 10, max: 1000 }}
            helperText="Nombre d'épisodes pour le test"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Taux d'apprentissage (α)"
            type="number"
            value={params.alpha}
            onChange={(e) =>
              handleParamChange("alpha", parseFloat(e.target.value))
            }
            disabled={isTraining || params.mode === "optimized"}
            inputProps={{ min: 0.01, max: 1, step: 0.01 }}
            helperText="Vitesse d'apprentissage"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Facteur d'actualisation (γ)"
            type="number"
            value={params.gamma}
            onChange={(e) =>
              handleParamChange("gamma", parseFloat(e.target.value))
            }
            disabled={isTraining || params.mode === "optimized"}
            inputProps={{ min: 0.1, max: 1, step: 0.01 }}
            helperText="Importance des récompenses futures"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Epsilon initial (ε)"
            type="number"
            value={params.eps}
            onChange={(e) =>
              handleParamChange("eps", parseFloat(e.target.value))
            }
            disabled={isTraining || params.mode === "optimized"}
            inputProps={{ min: 0, max: 1, step: 0.1 }}
            helperText="Taux d'exploration initial"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Décroissance epsilon"
            type="number"
            value={params.eps_decay}
            onChange={(e) =>
              handleParamChange("eps_decay", parseFloat(e.target.value))
            }
            disabled={isTraining || params.mode === "optimized"}
            inputProps={{ min: 0.9, max: 1, step: 0.0001 }}
            helperText="Vitesse de décroissance de l'exploration"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Epsilon minimum"
            type="number"
            value={params.eps_min}
            onChange={(e) =>
              handleParamChange("eps_min", parseFloat(e.target.value))
            }
            disabled={isTraining || params.mode === "optimized"}
            inputProps={{ min: 0, max: 0.1, step: 0.001 }}
            helperText="Taux d'exploration minimum"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Pas max par épisode"
            type="number"
            value={params.maxStepsPerEpisode}
            onChange={(e) =>
              handleParamChange("maxStepsPerEpisode", parseInt(e.target.value))
            }
            disabled={isTraining || params.mode === "optimized"}
            inputProps={{ min: 50, max: 500 }}
            helperText="Limite de pas par épisode"
          />
        </Grid>
      </Grid>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mt: 2 }}>
          {success}
        </Alert>
      )}

      {/* Submit Button */}
      <Box sx={{ mt: 3 }}>
        <Button
          type="submit"
          variant="contained"
          size="large"
          startIcon={isTraining ? <Stop /> : <PlayArrow />}
          disabled={isTraining}
          fullWidth
          sx={{ py: 1.5 }}
        >
          {isTraining
            ? "Entraînement en cours..."
            : "🚀 Démarrer l'entraînement"}
        </Button>
      </Box>

      {/* Info Text */}
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        💡 Le mode optimisé utilise des paramètres validés expérimentalement
        pour de meilleures performances.
      </Typography>
    </Box>
  );
};

export default TrainingForm;
