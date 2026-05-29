from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.seed import seed_db
from app.routers import auth, medicines, cart, serviceability, orders, coupons

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("FastAPI Application Starting Up...")
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed the database
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
        
    yield
    # Shutdown actions
    print("FastAPI Application Shutting Down...")

app = FastAPI(
    title="Medicine Delivery Web App API",
    description="Backend API for local Medicine Delivery Web App - production ready.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS so our React frontend can query our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow easy cross-origin connection
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth.router)
app.include_router(medicines.router)
app.include_router(cart.router)
app.include_router(serviceability.router)
app.include_router(orders.router)
app.include_router(coupons.router)

@app.get("/")
def health_check():
    """Simple API health check endpoint."""
    return {
        "status": "online",
        "service": "Medicine Delivery API",
        "version": "1.0.0"
    }
