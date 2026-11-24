from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.upstream_service import get_upstream_basin_status

router = APIRouter(
    prefix="/upstream",
    tags=["Upstream Conditions"]
)


@router.get("")
@router.get("/")
def get_upstream_conditions(db: Session = Depends(get_db)):
    """
    Get upstream monitoring conditions for all Karnataka river basins.
    Examines Maharashtra -> Krishna/Bhima, Kerala -> Cauvery/Kabini,
    and border catchments.
    """
    return get_upstream_basin_status(db)
