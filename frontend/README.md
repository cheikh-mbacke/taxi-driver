# Taxi Driver RL Frontend

A modern React-based frontend for the Taxi Driver Reinforcement Learning project, providing an intuitive interface for training and monitoring SARSA algorithms on the Taxi-v3 environment.

## 🚀 Features

- **Real-time Training Interface**: Start and monitor RL training sessions
- **Statistics Dashboard**: View comprehensive training statistics and metrics
- **Training History**: Browse and analyze past training runs
- **Interactive Visualizations**: View generated plots and performance graphs
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Built with Material-UI for a professional look and feel

## 🛠️ Tech Stack

- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **Material-UI (MUI)**: Component library for consistent UI
- **Vite**: Fast build tool and development server
- **Axios**: HTTP client for API communication

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Dashboard.tsx    # Main dashboard component
│   │   ├── StatisticsCards.tsx  # Statistics display cards
│   │   ├── TrainingForm.tsx     # Training configuration form
│   │   └── RunsTable.tsx        # Training runs history table
│   ├── services/            # API services
│   │   └── api.ts          # API client and endpoints
│   ├── types/              # TypeScript type definitions
│   │   └── api.ts          # API response types
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # App entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
└── tsconfig.json           # TypeScript configuration
```

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running (see backend README)

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## 🔧 Configuration

### API Configuration

The frontend connects to the backend API. Update the API base URL in `src/services/api.ts` if needed:

```typescript
const API_BASE_URL = ""; // Default: connects to localhost:8000 via Vite proxy
```

### Vite Proxy Configuration

The development server is configured to proxy API requests to the backend. See `vite.config.ts`:

```typescript
server: {
  proxy: {
    "/database": "http://localhost:8000",
    "/sarsa": "http://localhost:8000",
    "/assets": "http://localhost:8000",
  },
}
```

## 📱 Components Overview

### Dashboard
The main dashboard component that orchestrates all other components and manages the application state.

### StatisticsCards
Displays key training metrics in colorful, gradient cards:
- Total training runs
- Best success rate
- Best average steps
- Total execution time

### TrainingForm
Provides a form to configure and start new training sessions with SARSA parameters.

### RunsTable
Shows a comprehensive table of all training runs with:
- Run details and metrics
- Action buttons (view details, delete)
- Real-time updates

## 🎨 Styling

The application uses Material-UI with a custom theme defined in `App.tsx`:

- **Primary Color**: Blue (#1976d2)
- **Secondary Color**: Pink (#dc004e)
- **Background**: Light gray (#f5f5f5)
- **Typography**: Roboto font family
- **Components**: Customized cards and buttons with rounded corners

## 🔄 State Management

The application uses React hooks for state management:
- `useState` for local component state
- `useEffect` for side effects and API calls
- Props for component communication

## 📊 API Integration

The frontend communicates with the backend through RESTful APIs:

- **GET /database/statistics** - Fetch training statistics
- **GET /database/runs** - Get training runs list
- **GET /database/runs/{id}** - Get specific run details
- **POST /sarsa** - Start new training session
- **DELETE /database/runs/{id}** - Delete training run

## 🐛 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

- Use TypeScript for type safety
- Follow React functional component patterns
- Use Material-UI components for consistency
- Add JSDoc comments for complex functions

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Add TypeScript types for new features
3. Test your changes thoroughly
4. Update documentation as needed

## 📄 License

This project is part of the Taxi Driver RL project. See the main project README for license information.
