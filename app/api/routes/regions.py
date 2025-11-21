"""Regions endpoints."""

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.core.security import require_keycloak_token
from app.core.database import get_db
from app.models.db import Region as DBRegion
from app.models.schemas import RegionList, Region


router = APIRouter(
    prefix="/regions",
    tags=["Regions"],
    dependencies=[Depends(require_keycloak_token)],
)


@router.get("/", response_model=RegionList, summary="List available regions")
@limiter.limit("100/minute")
async def list_regions(request: Request, db: Session = Depends(get_db)) -> RegionList:
    """
    Récupère la liste de toutes les régions françaises depuis la base de données.

    Cette endpoint retourne les informations sur toutes les régions administratives
    de France, utile pour filtrer les données ferroviaires par région.
    """
    try:
        db_regions = db.query(DBRegion).order_by(DBRegion.nom).all()

        regions = []
        for db_region in db_regions:
            regions.append(Region(
                id=db_region.code,
                name=db_region.nom,
                code=db_region.code
            ))

        return RegionList(regions=regions, total=len(regions))
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch regions data: {str(e)}"
        )
