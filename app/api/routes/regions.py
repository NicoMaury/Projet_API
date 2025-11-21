"""Regions endpoints."""

from fastapi import APIRouter, Depends, Request, HTTPException

from app.core.rate_limit import limiter
from app.core.security import require_keycloak_token
from app.models.schemas import RegionList, Region
from app.services.opendatasoft_service import get_opendatasoft_service


router = APIRouter(
    prefix="/regions",
    tags=["Regions"],
    dependencies=[Depends(require_keycloak_token)],
)


@router.get("/", response_model=RegionList, summary="List available regions")
@limiter.limit("100/minute")
async def list_regions(request: Request) -> RegionList:
    """
    Récupère la liste de toutes les régions françaises.

    Cette endpoint retourne les informations sur toutes les régions administratives
    de France, utile pour filtrer les données ferroviaires par région.
    """
    try:
        service = get_opendatasoft_service()
        raw_regions = service.get_regions()

        regions = []
        for item in raw_regions:
            # Structure simplifiée directe
            regions.append(Region(
                id=item.get("code", ""),
                name=item.get("nom", "Unknown"),
                code=item.get("code")
            ))

        return RegionList(regions=regions, total=len(regions))
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch regions data: {str(e)}"
        )
