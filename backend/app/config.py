import os

class Settings:
    PROJECT_NAME: str = "FAWS - Firmware Analysis Workflow Simulator"
    API_V1_STR: str = "/api"
    
    # Mode can be 'simulation' or 'real'
    MODE: str = "simulation"
    
    # Base directory
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'faws.db')}"
    
    # Workspace/Artifact directories
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    UPLOAD_DIR: str = os.path.join(DATA_DIR, "uploads")
    ARTIFACTS_DIR: str = os.path.join(DATA_DIR, "projects")

# Ensure standard directories exist
settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.ARTIFACTS_DIR, exist_ok=True)
