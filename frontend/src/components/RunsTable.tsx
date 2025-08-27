import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  LinearProgress,
} from "@mui/material";
import {
  Visibility,
  Delete,
  Refresh,
  TrendingUp,
  Speed,
  Schedule,
} from "@mui/icons-material";
import type { TrainingRunSummary, TrainingRun } from "../types/api";
import { apiService } from "../services/api";

interface RunsTableProps {
  onRefresh: () => void;
}

const RunsTable: React.FC<RunsTableProps> = ({ onRefresh }) => {
  const [runs, setRuns] = useState<TrainingRunSummary[]>([]);
  const [selectedRun, setSelectedRun] = useState<TrainingRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    console.log("🚀 loadRuns appelée");
    try {
      console.log("📝 Début du try");
      setLoading(true);
      setError(null); // Réinitialiser l'erreur
      console.log("📞 Appel de l'API...");
      const data = await apiService.getTrainingRuns();
      console.log("🔍 Données reçues de l'API:", data);
      console.log("🔍 Type de data:", typeof data);
      console.log("🔍 Est-ce un tableau?", Array.isArray(data));

      // S'assurer que data est un tableau
      if (Array.isArray(data)) {
        console.log("✅ Data est un tableau, mise à jour du state");
        setRuns(data);
      } else {
        console.error("❌ L'API n'a pas retourné un tableau:", data);
        setRuns([]);
        setError("Format de données invalide");
      }
    } catch (err) {
      console.error("❌ Erreur dans loadRuns:", err);
      setError("Erreur lors du chargement des runs");
      console.error("❌ Erreur loadRuns:", err);
      setRuns([]);
    } finally {
      console.log("🏁 Fin de loadRuns");
      setLoading(false);
    }
  };

  const handleViewRun = async (runId: string) => {
    try {
      setError(null); // Réinitialiser l'erreur
      const run = await apiService.getTrainingRun(runId);
      setSelectedRun(run);
      setDialogOpen(true);
    } catch (err) {
      setError("Erreur lors du chargement du run");
      console.error(err);
    }
  };

  const handleDeleteRun = async (runId: string) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer ce run ?")) {
      try {
        setError(null); // Réinitialiser l'erreur
        await apiService.deleteTrainingRun(runId);
        loadRuns();
        onRefresh();
      } catch (err) {
        setError("Erreur lors de la suppression");
        console.error(err);
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("fr-FR");
  };

  const formatTime = (seconds: number | null) => {
    if (!seconds) return "N/A";
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}m ${secs}s`;
  };

  const formatPercentage = (value: number | null) => {
    if (value === null) return "N/A";
    return `${(value * 100).toFixed(1)}%`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "success";
      case "running":
        return "warning";
      case "failed":
        return "error";
      default:
        return "default";
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            📊 Historique des Entraînements
          </Typography>
          <LinearProgress />
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="h5">
              📊 Historique des Entraînements
            </Typography>
            <Button
              startIcon={<Refresh />}
              onClick={loadRuns}
              variant="outlined"
            >
              Actualiser
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {runs.length === 0 ? (
            <Box sx={{ textAlign: "center", py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                Aucun entraînement trouvé
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Lancez votre premier entraînement pour voir les résultats ici
              </Typography>
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Algorithme</TableCell>
                    <TableCell>Taux de Succès</TableCell>
                    <TableCell>Pas Moyens</TableCell>
                    <TableCell>Temps d'Exécution</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {runs.map((run) => (
                    <TableRow key={run.run_id} hover>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {run.run_id.slice(0, 8)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={run.algorithm.toUpperCase()}
                          size="small"
                          color="primary"
                        />
                      </TableCell>
                      <TableCell>
                        {run.success_rate
                          ? formatPercentage(run.success_rate)
                          : "N/A"}
                      </TableCell>
                      <TableCell>
                        {run.avg_steps ? run.avg_steps.toFixed(1) : "N/A"}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                          <Schedule
                            sx={{
                              fontSize: 16,
                              mr: 0.5,
                              color: "warning.main",
                            }}
                          />
                          {formatTime(run.execution_time)}
                        </Box>
                      </TableCell>
                      <TableCell>{formatDate(run.created_at)}</TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => handleViewRun(run.run_id)}
                          color="primary"
                        >
                          <Visibility />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteRun(run.run_id)}
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Run Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle
          sx={{
            background: "linear-gradient(135deg, #1976d2 0%, #1565c0 100%)",
            color: "white",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box>
            <Typography variant="h5" component="div">
              📊 Détails du Run d'Entraînement
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              {selectedRun?.algorithm.toUpperCase()} -{" "}
              {selectedRun?.run_id.slice(0, 8)}...
            </Typography>
          </Box>
          <IconButton
            onClick={() => {
              if (selectedRun) {
                handleDeleteRun(selectedRun.run_id);
                setDialogOpen(false);
              }
            }}
            sx={{ color: "white" }}
          >
            <Delete />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ p: 3 }}>
          {selectedRun && (
            <Box>
              {/* Informations Générales */}
              <Card sx={{ my: 3, border: "1px solid #e0e0e0" }}>
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      color: "#1976d2",
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    📋 Informations Générales
                  </Typography>
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: { xs: "column", sm: "row" },
                      gap: 2,
                    }}
                  >
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>ID:</strong> {selectedRun.run_id}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Algorithme:</strong>{" "}
                        {selectedRun.algorithm.toUpperCase()}
                      </Typography>
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Statut:</strong>
                        <Chip
                          label={selectedRun.status}
                          size="small"
                          color="success"
                          sx={{ ml: 1 }}
                        />
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Date:</strong>{" "}
                        {formatDate(selectedRun.created_at)}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>

              {/* Métriques de Test */}
              <Card sx={{ mb: 3, border: "1px solid #e0e0e0" }}>
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      color: "#1976d2",
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    📈 Métriques de Test
                  </Typography>
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: { xs: "column", sm: "row" },
                      gap: 2,
                    }}
                  >
                    <Box
                      sx={{
                        flex: 1,
                        textAlign: "center",
                        p: 2,
                        bgcolor: "#f5f5f5",
                        borderRadius: 2,
                        border: "1px solid #e0e0e0",
                      }}
                    >
                      <Typography
                        variant="h4"
                        sx={{ fontWeight: "bold", color: "#1976d2" }}
                      >
                        {formatPercentage(
                          selectedRun.test_metrics?.success_rate
                        )}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Taux de succès
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        flex: 1,
                        textAlign: "center",
                        p: 2,
                        bgcolor: "#f5f5f5",
                        borderRadius: 2,
                        border: "1px solid #e0e0e0",
                      }}
                    >
                      <Typography
                        variant="h4"
                        sx={{ fontWeight: "bold", color: "#1976d2" }}
                      >
                        {selectedRun.test_metrics?.avg_steps?.toFixed(1)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Pas moyens
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        flex: 1,
                        textAlign: "center",
                        p: 2,
                        bgcolor: "#f5f5f5",
                        borderRadius: 2,
                        border: "1px solid #e0e0e0",
                      }}
                    >
                      <Typography
                        variant="h4"
                        sx={{ fontWeight: "bold", color: "#1976d2" }}
                      >
                        {selectedRun.test_metrics?.avg_reward?.toFixed(2)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Récompense moyenne
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>

              {/* Paramètres */}
              <Card sx={{ mb: 3, border: "1px solid #e0e0e0" }}>
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      color: "#1976d2",
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    ⚙️ Paramètres
                  </Typography>
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: { xs: "column", sm: "row" },
                      gap: 2,
                    }}
                  >
                    <Box
                      sx={{
                        flex: 1,
                        textAlign: "center",
                        p: 2,
                        bgcolor: "#f5f5f5",
                        borderRadius: 2,
                        border: "1px solid #e0e0e0",
                      }}
                    >
                      <Typography variant="h6" color="#1976d2">
                        {selectedRun.params.alpha}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Alpha
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        flex: 1,
                        textAlign: "center",
                        p: 2,
                        bgcolor: "#f5f5f5",
                        borderRadius: 2,
                        border: "1px solid #e0e0e0",
                      }}
                    >
                      <Typography variant="h6" color="#1976d2">
                        {selectedRun.params.gamma}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Gamma
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        flex: 1,
                        textAlign: "center",
                        p: 2,
                        bgcolor: "#f5f5f5",
                        borderRadius: 2,
                        border: "1px solid #e0e0e0",
                      }}
                    >
                      <Typography variant="h6" color="#1976d2">
                        {selectedRun.params.training_runs}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Épisodes d'entraînement
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        flex: 1,
                        textAlign: "center",
                        p: 2,
                        bgcolor: "#f5f5f5",
                        borderRadius: 2,
                        border: "1px solid #e0e0e0",
                      }}
                    >
                      <Typography variant="h6" color="#1976d2">
                        {selectedRun.params.test_episodes}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Épisodes de test
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>

              {/* Graphiques Générés */}
              {selectedRun.plots && selectedRun.plots.length > 0 && (
                <Card sx={{ border: "1px solid #e0e0e0" }}>
                  <CardContent>
                    <Typography
                      variant="h6"
                      gutterBottom
                      sx={{
                        color: "#1976d2",
                        display: "flex",
                        alignItems: "center",
                      }}
                    >
                      📊 Graphiques Générés
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        flexDirection: { xs: "column", sm: "row" },
                        gap: 2,
                      }}
                    >
                      {selectedRun.plots.map((plot, index) => (
                        <Box key={index} sx={{ flex: 1 }}>
                          <Card
                            sx={{
                              cursor: "pointer",
                              transition: "transform 0.2s",
                              border: "1px solid #e0e0e0",
                              "&:hover": {
                                transform: "scale(1.02)",
                                boxShadow: 2,
                                borderColor: "#1976d2",
                              },
                            }}
                            onClick={() =>
                              window.open(
                                apiService.getPlotImage(plot),
                                "_blank"
                              )
                            }
                          >
                            <CardContent sx={{ p: 1 }}>
                              <img
                                src={apiService.getPlotImage(plot)}
                                alt={`Graphique ${index + 1}`}
                                style={{
                                  width: "100%",
                                  height: "250px",
                                  objectFit: "cover",
                                  borderRadius: "8px",
                                }}
                              />
                              <Typography
                                variant="body2"
                                sx={{
                                  mt: 1,
                                  textAlign: "center",
                                  color: "text.secondary",
                                }}
                              >
                                Cliquez pour agrandir
                              </Typography>
                            </CardContent>
                          </Card>
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button
            onClick={() => setDialogOpen(false)}
            variant="contained"
            sx={{
              background: "linear-gradient(135deg, #1976d2 0%, #1565c0 100%)",
              color: "white",
            }}
          >
            Fermer
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default RunsTable;
