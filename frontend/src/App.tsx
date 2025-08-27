import React from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Dashboard from "./components/Dashboard";

/**
 * Custom Material-UI theme configuration
 * Defines the color palette, typography, and component styling
 */
const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2", // Blue primary color
    },
    secondary: {
      main: "#dc004e", // Pink secondary color
    },
    background: {
      default: "#f5f5f5", // Light gray background
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h3: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    // Custom card styling
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          borderRadius: 12,
        },
      },
    },
    // Custom button styling
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: "none",
          fontWeight: 500,
        },
      },
    },
  },
});

/**
 * Main App component
 * Provides theme context and renders the dashboard
 */
function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Dashboard />
    </ThemeProvider>
  );
}

export default App;
