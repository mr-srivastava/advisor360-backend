from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import commissions, partners, routes_goals, routes_users, dashboard

app = FastAPI(title="Advisor360 API")

# Allow origins (React dev server, etc.)
origins = [
    "https://advisor360.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],          # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)

# include routers
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(partners.router, prefix="/partners", tags=["partners"])
app.include_router(commissions.router, prefix="/commissions", tags=["commissions"])
app.include_router(routes_goals.router, prefix="/goals", tags=["goals"])
app.include_router(routes_users.router, prefix="/users", tags=["users"])