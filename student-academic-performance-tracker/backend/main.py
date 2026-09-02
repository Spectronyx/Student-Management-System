import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import init_db

# Import Routers
from routes import auth, students, subjects, marks, attendance, performance, analytics

app = FastAPI(
    title="Student Academic Performance Tracker API",
    description="RESTful API Backend for Student Academic Tracker Android App built with Python & MySQL",
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
    init_db()

@app.get("/")
def root():
    return {
        "success": True,
        "message": "Student Academic Performance Tracker API is running",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
