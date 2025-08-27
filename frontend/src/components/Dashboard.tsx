import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  Chip,
  LinearProgress,
  Alert,
} from "@mui/material";
import {
  TrendingUp,
  Speed,
  Psychology,
  Storage,
  Timeline,
  CheckCircle,
} from "@mui/icons-material";
import type { StatisticsResponse } from "../types/api";
import { apiService } from "../services/api";
import TrainingForm from "./TrainingForm";
import RunsTable from "./RunsTable";
import StatisticsCards from "./StatisticsCards";

const Dashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<StatisticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isTraining, setIsTraining] = useState(false);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      const stats = await apiService.getStatistics();
      setStatistics(stats);
    } catch (err) {
      setError("Erreur lors du chargement des statistiques");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTrainingStart = () => {
    setIsTraining(true);
  };

  const handleTrainingComplete = () => {
    setIsTraining(false);
    loadStatistics(); // Recharger les stats
  };

  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mt: 4 }}>
          <LinearProgress />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Chargement des statistiques...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            🚕 Taxi Driver RL Dashboard
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Interface d'apprentissage par renforcement pour l'environnement
            Taxi-v3
          </Typography>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Statistics Cards */}
        {statistics && <StatisticsCards statistics={statistics} />}

        {/* Training Section */}
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  🚀 Nouvel Entraînement
                </Typography>
                <TrainingForm
                  onTrainingStart={handleTrainingStart}
                  onTrainingComplete={handleTrainingComplete}
                  isTraining={isTraining}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  📊 État du Système
                </Typography>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircle color="success" />
                    <Typography>API Backend: Connecté</Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Storage color="primary" />
                    <Typography>Base de données: PostgreSQL</Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Psychology color="secondary" />
                    <Typography>Algorithme: SARSA</Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Timeline color="info" />
                    <Typography>Environnement: Taxi-v3</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Runs Table */}
        <Box sx={{ mt: 4 }}>
          <RunsTable onRefresh={loadStatistics} />
        </Box>
      </Box>
    </Container>
  );
};

export default Dashboard;
