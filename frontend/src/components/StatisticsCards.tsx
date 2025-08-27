import React from "react";
import { Grid, Card, CardContent, Typography, Box } from "@mui/material";
import { TrendingUp, Speed, Psychology, Timeline } from "@mui/icons-material";
import type { StatisticsResponse } from "../types/api";

interface StatisticsCardsProps {
  statistics: StatisticsResponse;
}

const StatisticsCards: React.FC<StatisticsCardsProps> = ({ statistics }) => {
  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // Vérifications de sécurité pour éviter les erreurs
  const totalRuns = statistics?.total_runs ?? 0;
  const bestSuccessRate = statistics?.best_success_rate ?? 0;
  const bestAvgSteps = statistics?.best_avg_steps ?? 0;
  const totalExecutionTime = statistics?.total_execution_time ?? 0;

  return (
    <Grid container spacing={2}>
      {/* Total Runs */}
      <Grid item xs={12} sm={6} md={3}>
        <Card
          sx={{
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
          }}
        >
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <Timeline sx={{ fontSize: 40, mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {totalRuns}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Entraînements
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Total des runs d'entraînement
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Best Success Rate */}
      <Grid item xs={12} sm={6} md={3}>
        <Card
          sx={{
            background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
            color: "white",
          }}
        >
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <TrendingUp sx={{ fontSize: 40, mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {formatPercentage(bestSuccessRate)}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Taux de succès
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Meilleur taux de réussite
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Best Average Steps */}
      <Grid item xs={12} sm={6} md={3}>
        <Card
          sx={{
            background: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
            color: "white",
          }}
        >
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <Speed sx={{ fontSize: 40, mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {bestAvgSteps.toFixed(1)}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Pas moyens
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Meilleure performance
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Total Execution Time */}
      <Grid item xs={12} sm={6} md={3}>
        <Card
          sx={{
            background: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
            color: "white",
          }}
        >
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <Psychology sx={{ fontSize: 40, mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {formatTime(totalExecutionTime)}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Temps total
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Temps d'exécution total
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default StatisticsCards;
