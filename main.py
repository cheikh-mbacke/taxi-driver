from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pathlib

from app.schemas.sarsa import SarsaParams
from app.services.sarsa import run_sarsa

# Création de l'application FastAPI
app = FastAPI(
    title="Taxi Driver - Reinforcement Learning API",
    description="API pour l'apprentissage par renforcement avec différents algorithmes",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer selon vos besoins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage des fichiers statiques pour les images générées
ROOT_DIR = pathlib.Path(__file__).resolve().parent
ASSETS_DIR = ROOT_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Routes pour les algorithmes
@app.post("/sarsa")
def sarsa_endpoint(params: SarsaParams):
    """
    Endpoint pour l'algorithme SARSA
    
    Args:
        params: Paramètres d'entraînement SARSA
        
    Returns:
        Résultats de l'entraînement avec métriques et graphiques
    """
    return run_sarsa(params)

# Route de santé
@app.get("/health")
def health_check():
    """Vérification de l'état de l'API"""
    return {"status": "healthy", "message": "Taxi Driver RL API is running"}

# Route racine
@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Taxi Driver - Reinforcement Learning API",
        "version": "1.0.0",
        "available_algorithms": ["sarsa"],
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
