from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

# Database session dependency
from app.shared.db.config.session import get_db

# Owner authentication dependency (adjust to your auth provider)
from app.core.dependencies import get_current_user  # Must verify caller has Owner ('O') role

# Schemas and Service
from app.services.properties.schema import PropertyCreateRequest, PropertyResponse
from app.services.properties.service import PropertyService

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post(
    "/add",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new property",
    description="Accessible by Owners ('O'). Creates a new property under the authenticated user.",
)
def add_property(
    payload: PropertyCreateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PropertyResponse:
    """Create a new property entity for the authenticated owner."""
    service = PropertyService(db=db)
    return service.add_property(owner_id=current_user.id, payload=payload)