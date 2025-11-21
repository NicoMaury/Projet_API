"""API router aggregation."""

from fastapi import APIRouter

from app.api.routes import alerts, departements, lines, regions, stations, stats, trains


api_router = APIRouter()

api_router.include_router(regions.router)
api_router.include_router(departements.router)
api_router.include_router(stations.router)
api_router.include_router(lines.router)
api_router.include_router(trains.router)
api_router.include_router(stats.router)
api_router.include_router(alerts.router)
