"""Departements endpoints."""

from fastapi import APIRouter, Depends, Request, HTTPException

from app.core.rate_limit import limiter
from app.core.security import require_keycloak_token
from app.models.schemas import DepartementList, Departement
from app.services.opendatasoft_service import get_opendatasoft_service


router = APIRouter(
    prefix="/departements",
    tags=["Departements"],
    dependencies=[Depends(require_keycloak_token)],
)


@router.get("/", response_model=DepartementList, summary="List departements")
@limiter.limit("100/minute")
async def list_departements(request: Request) -> DepartementList:
    """
    Récupère la liste de tous les départements français.

    Cette endpoint retourne les informations sur tous les départements administratifs
    de France, avec leurs régions associées si disponibles.
    """
    try:
        service = get_opendatasoft_service()
        raw_depts = service.get_departements()

        departements = []
        for item in raw_depts:
            # Structure simplifiée directe
            departements.append(Departement(
                id=item.get("code", ""),
                name=item.get("nom", "Unknown"),
                code=item.get("code", ""),
                region_id=item.get("code_region"),
                region_name=item.get("nom_region")
            ))

        return DepartementList(departements=departements, total=len(departements))
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch departements data: {str(e)}"
        )
