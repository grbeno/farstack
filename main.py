from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pathlib import Path
import logging
import os

# # run: uvicorn main:app --reload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
ASSETS_DIR = STATIC_DIR / "assets"
INDEX_PATH = STATIC_DIR / "index.html"

def verify_paths() -> bool:
    """Verify that all required paths exist."""
    required_paths = [STATIC_DIR, ASSETS_DIR, INDEX_PATH]
    for path in required_paths:
        if not path.exists():
            logger.error(f"Required path does not exist: {path}")
            return False
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting up application... {os.cpu_count()}")
    if not verify_paths():
        logger.critical("Required paths are missing!")
        raise RuntimeError("Application cannot start: missing required paths")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down application...")
    # Add any cleanup code here if needed

# Initialize FastAPI with lifespan
app = FastAPI(
    title="FastAPI React App",
    description="FastAPI backend serving React frontend",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files with custom configuration
app.mount(
    "/assets",
    StaticFiles(
        directory=ASSETS_DIR,
        check_dir=True,  # Verify directory exists
        html=True  # Allow serving HTML files
    ),
    name="assets"
)

@app.get("/")
async def read_index():
    """Serve the index.html file."""
    try:
        if not INDEX_PATH.exists():
            raise HTTPException(
                status_code=404,
                detail="Index file not found"
            )
        return FileResponse(
            INDEX_PATH,
            media_type="text/html"
        )
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info",
#         workers=4  # Adjust based on your CPU cores
#     )


# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from pathlib import Path

# # run: uvicorn main:app --reload

# app = FastAPI()

# # Define the path to your static files and index.html
# static_files_path = Path(file).parent / "static" / "assets"
# index_file_path = Path(file).parent / "static" / "index.html"

# # Mount the static files to the '/assets' URL path
# app.mount("/assets", StaticFiles(directory=static_files_path), name="assets")

# # Route to serve the index.html file
# @app.get("/")
# async def read_index():
#     return FileResponse(index_file_path)

# # ...existing code...

# if name == "main":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
