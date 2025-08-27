from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.api.database import get_db, init_db
from app.api.routes.database_routes import database_router
from app.api.schemas.sarsa import SarsaParams
from app.api.services.sarsa import run_sarsa

# Initialize FastAPI application
app = FastAPI(
    title="Taxi Driver RL API",
    description="Reinforcement Learning API for Taxi-v3 environment with PostgreSQL",
    version="2.0.0"
)

# CORS configuration for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving generated plots
app.mount("/assets", StaticFiles(directory="data/results"), name="assets")

# Include database routes
app.include_router(database_router, prefix="/database", tags=["database"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """API home page with documentation links"""
    return """
    <html>
        <head>
            <title>Taxi Driver RL API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .method { color: #007bff; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚕 Taxi Driver RL API</h1>
                <p>Reinforcement Learning API for Taxi-v3 environment</p>
                
                <h2>📚 Documentation</h2>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/docs">/docs</a> - Interactive documentation (Swagger)
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/redoc">/redoc</a> - Alternative documentation (ReDoc)
                </div>
                
                <h2>🔌 Main Endpoints</h2>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/health">/health</a> - API status
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> /sarsa - SARSA training
                </div>
                
                <h2>🗄️ Database</h2>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/database/runs">/database/runs</a> - Training runs list
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/database/statistics">/database/statistics</a> - Statistics
                </div>
                
                <h2>🚀 Quick Start</h2>
                <p>To test the API, use the SARSA endpoint:</p>
                <pre>
curl -X POST "http://localhost:8000/sarsa" \\
     -H "Content-Type: application/json" \\
     -d '{"mode": "optimized", "test_episodes": 10}'
                </pre>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "taxi-driver-api",
        "version": "2.0.0",
        "database": "postgresql"
    }

@app.post("/sarsa")
async def sarsa_endpoint(params: SarsaParams, db: Session = Depends(get_db)):
    """Main endpoint for SARSA training"""
    return run_sarsa(params, db)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
