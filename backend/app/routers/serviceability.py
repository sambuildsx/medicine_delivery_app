from fastapi import APIRouter, status
from app.schemas import ServiceabilityCheck, ServiceabilityResponse

router = APIRouter(prefix="/serviceability", tags=["Serviceability"])

@router.post("/check", response_model=ServiceabilityResponse)
def check_serviceability(check: ServiceabilityCheck):
    """
    Check if the user's distance and pincode are serviceable by the store.
    Serviceable limit: distance <= 5000 meters.
    Estimated Delivery Time:
    - <= 2000 meters: 30 minutes
    - 2001 - 5000 meters: 45 minutes
    """
    distance = check.distance
    
    if distance <= 5000:
        if distance <= 2000:
            est_minutes = 30
        else:
            est_minutes = 45
            
        return ServiceabilityResponse(
            serviceable=True,
            distance=distance,
            estimated_delivery_minutes=est_minutes,
            message=f"Store is serviceable. Estimated delivery time: {est_minutes} minutes."
        )
    else:
        return ServiceabilityResponse(
            serviceable=False,
            distance=distance,
            estimated_delivery_minutes=None,
            message="Store is unserviceable. Distance exceeds the maximum limit of 5000 meters."
        )
