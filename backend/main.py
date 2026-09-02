import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from database import init_db

# Import Routers
from routes import auth, students, subjects, marks, attendance, performance, analytics

app = FastAPI(
    title="EduTrack - Student Academic Performance Tracker",
    description="RESTful API & Web Application Backend for Student Academic Tracker built with Python & MySQL",
    version="1.0.0"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handler for consistent JSON format
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred",
            "error": str(exc)
        }
    )

# Register Routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(subjects.router)
app.include_router(marks.router)
app.include_router(attendance.router)
app.include_router(performance.router)
app.include_router(analytics.router)

@app.on_event("startup")
def on_startup():
    """Initializes database schema and seed data on startup."""
    try:
        init_db()
    except Exception as e:
        print(f"DB startup init warning: {e}")

# Serve Static Web Frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "android_app"))
if not os.path.exists(STATIC_DIR):
    STATIC_DIR = os.path.abspath(os.path.join(os.getcwd(), "android_app"))

if os.path.exists(STATIC_DIR):
    css_dir = os.path.join(STATIC_DIR, "css")
    js_dir = os.path.join(STATIC_DIR, "js")
    img_dir = os.path.join(STATIC_DIR, "img")

    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
    if os.path.exists(img_dir):
        app.mount("/img", StaticFiles(directory=img_dir), name="img")

    @app.get("/")
    async def serve_index():
        index_file = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"success": True, "message": "EduTrack API is running", "documentation": "/docs"}
else:
    @app.get("/")
    def root():
        return {
            "success": True,
            "message": "EduTrack API is running",
            "documentation": "/docs"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
