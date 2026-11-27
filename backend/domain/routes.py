"""The station's JSON route families."""
from fastapi import APIRouter

from domain import baseline_routes, case_routes, fold_routes, intake_routes, trip_routes

router = APIRouter()
for endpoint in (intake_routes, baseline_routes, fold_routes, case_routes, trip_routes):
    router.include_router(endpoint.router)
