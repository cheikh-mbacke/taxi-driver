from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.api.database import get_db, init_db
from app.api.routes.database_routes import database_router
from app.api.schemas.sarsa import SarsaParams
from app.api.services.sarsa import run_sarsa

app = FastAPI(
    title="Taxi Driver RL API",
    description="API d'apprentissage par renforcement pour l'environnement Taxi-v3 avec PostgreSQL",
    version="2.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monter les fichiers statiques
app.mount("/assets", StaticFiles(directory="data/results"), name="assets")

# Inclure les routes de base de données
app.include_router(database_router, prefix="/database", tags=["database"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil de l'API"""
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
                <p>API d'apprentissage par renforcement pour l'environnement Taxi-v3</p>
                
                <h2>📚 Documentation</h2>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/docs">/docs</a> - Documentation interactive (Swagger)
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/redoc">/redoc</a> - Documentation alternative (ReDoc)
                </div>
                
                <h2>🔌 Endpoints Principaux</h2>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/health">/health</a> - Statut de l'API
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> /sarsa - Entraînement SARSA
                </div>
                
                <h2>🗄️ Base de Données</h2>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/database/runs">/database/runs</a> - Liste des entraînements
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> <a href="/database/statistics">/database/statistics</a> - Statistiques
                </div>
                
                <h2>🚀 Démarrage Rapide</h2>
                <p>Pour tester l'API, utilisez l'endpoint SARSA :</p>
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
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "service": "taxi-driver-api",
        "version": "2.0.0",
        "database": "postgresql"
    }

@app.post("/sarsa")
async def sarsa_endpoint(params: SarsaParams, db: Session = Depends(get_db)):
    """Endpoint principal pour l'entraînement SARSA"""
    return run_sarsa(params, db)

# Initialiser la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'application"""
    try:
        init_db()
        print("✅ Base de données initialisée avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
