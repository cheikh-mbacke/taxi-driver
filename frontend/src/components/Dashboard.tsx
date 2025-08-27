import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Alert,
} from "@mui/material";
import {
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

/**
 * Main Dashboard component
 * Displays the complete RL training interface with statistics, training form, and runs history
 */
const Dashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<StatisticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isTraining, setIsTraining] = useState(false);

  useEffect(() => {
    loadStatistics();
  }, []);

  /**
   * Load training statistics from the API
   */
  const loadStatistics = async () => {
    try {
      setLoading(true);
      const stats = await apiService.getStatistics();
      setStatistics(stats);
    } catch (err) {
      setError("Error loading statistics");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle training start event
   */
  const handleTrainingStart = () => {
    setIsTraining(true);
  };

  /**
   * Handle training completion event
   */
  const handleTrainingComplete = () => {
    setIsTraining(false);
    loadStatistics(); // Reload statistics after training
  };

  // Loading state
  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mt: 1 }}>
          <LinearProgress />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading statistics...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ px: 2, py: 2 }}>
        {/* Page Header */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            🚕 Taxi Driver RL Dashboard
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Interface d'apprentissage par renforcement pour l'environnement
          </Typography>
        </Box>

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Statistics Cards */}
        {statistics && <StatisticsCards statistics={statistics} />}

        {/* Training and System Status Section */}
        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            gap: 2,
            mt: 1,
          }}
        >
          {/* Training Form Card */}
          <Box sx={{ flex: 1 }}>
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
          </Box>

          {/* System Status Card */}
          <Box sx={{ flex: 1 }}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  📊 System Status
                </Typography>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircle color="success" />
                    <Typography>API Backend: Connected</Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Storage color="primary" />
                    <Typography>Database: PostgreSQL</Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Psychology color="secondary" />
                    <Typography>Algorithm: SARSA</Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Timeline color="info" />
                    <Typography>Environment: Taxi-v3</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>

        {/* Training Runs History */}
        <Box sx={{ mt: 2 }}>
          <RunsTable onRefresh={loadStatistics} />
        </Box>
      </Box>
    </Container>
  );
};

export default Dashboard;
