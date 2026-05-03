"""
LokMat — Election Calendar Router

Exposes India's election calendar as REST endpoints.
Data is sourced from the ECI-synced election calendar service.

Endpoints:
    GET /elections/live     — Returns the currently live election (if any)
    GET /elections/upcoming — Returns upcoming elections
"""

import logging

from fastapi import APIRouter

from api.services.election_calendar import get_live_election, get_upcoming_elections

logger = logging.getLogger("lokmat")
router = APIRouter(prefix="/elections", tags=["Elections"])


@router.get("/live")
async def live_election():
    """
    Returns the currently live election ticker data.

    An election is live when it's in NOMINATION, POLLING, or COUNTING phase.
    Returns `is_live: false` if no election is currently active.

    Used by the frontend to conditionally show the live election banner
    at the bottom of the home screen.
    """
    result = get_live_election()
    return result.model_dump()


@router.get("/upcoming")
async def upcoming_elections():
    """
    Returns a list of upcoming and currently active elections
    sorted by polling start date.

    Excludes completed elections.
    """
    upcoming = get_upcoming_elections(limit=5)
    return {
        "elections": [
            {
                "id": item["election"].id,
                "name_en": item["election"].name_en,
                "name_hi": item["election"].name_hi,
                "election_type": item["election"].election_type.value,
                "polling_start": item["election"].polling_start.isoformat(),
                "polling_end": item["election"].polling_end.isoformat(),
                "counting_date": item["election"].counting_date.isoformat(),
                "total_phases": item["election"].total_phases,
                "total_seats": item["election"].total_seats,
                "states": item["election"].states,
                "status": item["status"],
                "progress_percent": item["progress_percent"],
            }
            for item in upcoming
        ]
    }
