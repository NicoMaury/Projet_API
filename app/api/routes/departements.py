"""Departements endpoints."""

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.core.security import require_keycloak_token
from app.core.database import get_db
from app.models.db import Departement as DBDepartement
from app.models.schemas import DepartementList, Departement


router = APIRouter(
    prefix="/departements",
    tags=["Departements"],
    dependencies=[Depends(require_keycloak_token)],
)


@router.get("/", response_model=DepartementList, summary="List departements")
@limiter.limit("100/minute")
async def list_departements(request: Request, db: Session = Depends(get_db)) -> DepartementList:
    """
    Récupère la liste de tous les départements français depuis la base de données.

    Cette endpoint retourne les informations sur tous les départements administratifs
    de France, avec leurs régions associées si disponibles.
    """
    try:
        db_departements = db.query(DBDepartement).order_by(DBDepartement.nom).all()

        departements = []
        for db_dept in db_departements:
            departements.append(Departement(
                id=db_dept.code,
                name=db_dept.nom,
                code=db_dept.code,
                region_id=db_dept.region_code,
                region_name=db_dept.region.nom if db_dept.region else None
            ))

        return DepartementList(departements=departements, total=len(departements))
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch departements data: {str(e)}"
        )
