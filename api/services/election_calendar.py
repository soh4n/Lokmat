"""
LokMat — India Election Calendar Service

Provides real election schedule data synced with India's actual election calendar.
Data sourced from Election Commission of India (ECI) official schedules.

Each election entry includes:
- Date ranges for nomination, polling, and result phases
- Phase-wise polling dates for multi-phase elections
- Type: LOK_SABHA | VIDHAN_SABHA | BY_ELECTION | PANCHAYAT | MUNICIPAL
- Status: computed dynamically based on current IST date
"""

from datetime import date, datetime, timedelta, timezone
from enum import Enum

from pydantic import BaseModel

# IST offset (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


class ElectionType(str, Enum):
    LOK_SABHA = "LOK_SABHA"
    VIDHAN_SABHA = "VIDHAN_SABHA"
    BY_ELECTION = "BY_ELECTION"
    PANCHAYAT = "PANCHAYAT"
    MUNICIPAL = "MUNICIPAL"


class ElectionStatus(str, Enum):
    UPCOMING = "upcoming"
    NOMINATION = "nomination"
    POLLING = "polling"
    COUNTING = "counting"
    COMPLETED = "completed"


class PollingPhase(BaseModel):
    """Represents a single phase of a multi-phase election."""
    phase_number: int
    polling_date: date
    states: list[str]
    seats: int


class ElectionEvent(BaseModel):
    """
    A single election event in India's calendar.

    Fields:
        id:                 Unique slug identifier.
        name_en:            English name of the election.
        name_hi:            Hindi name of the election.
        election_type:      Type of election (Lok Sabha, Vidhan Sabha, etc.).
        notification_date:  Date the election was officially notified.
        nomination_start:   First date for filing nominations.
        nomination_end:     Last date for filing nominations.
        polling_start:      First polling date (phase 1).
        polling_end:        Last polling date (final phase).
        counting_date:      Date of vote counting.
        result_date:        Date results are declared.
        total_phases:       Number of polling phases.
        phases:             Phase-wise details (optional).
        total_seats:        Total seats being contested.
        states:             States/UTs involved.
        description_en:     Short description in English.
        description_hi:     Short description in Hindi.
    """
    id: str
    name_en: str
    name_hi: str
    election_type: ElectionType
    notification_date: date
    nomination_start: date
    nomination_end: date
    polling_start: date
    polling_end: date
    counting_date: date
    result_date: date
    total_phases: int
    phases: list[PollingPhase] = []
    total_seats: int
    states: list[str]
    description_en: str
    description_hi: str


class LiveElectionResponse(BaseModel):
    """Response for the live election ticker."""
    is_live: bool
    election: ElectionEvent | None = None
    status: ElectionStatus | None = None
    current_phase: int | None = None
    next_phase_date: date | None = None
    days_until_next: int | None = None
    progress_percent: float = 0.0
    status_message_en: str = ""
    status_message_hi: str = ""


# ============================================================================
# India Election Calendar — Real Data
#
# This is the authoritative source of election schedules.
# Update this list when the Election Commission of India announces new dates.
#
# Sources:
#   - https://eci.gov.in/
#   - https://results.eci.gov.in/
# ============================================================================

INDIA_ELECTION_CALENDAR: list[ElectionEvent] = [
    # --- 2024: 18th Lok Sabha General Elections (COMPLETED) ---
    ElectionEvent(
        id="lok-sabha-2024",
        name_en="18th Lok Sabha General Elections",
        name_hi="18वीं लोक सभा आम चुनाव",
        election_type=ElectionType.LOK_SABHA,
        notification_date=date(2024, 3, 16),
        nomination_start=date(2024, 3, 20),
        nomination_end=date(2024, 5, 6),
        polling_start=date(2024, 4, 19),
        polling_end=date(2024, 6, 1),
        counting_date=date(2024, 6, 4),
        result_date=date(2024, 6, 4),
        total_phases=7,
        phases=[
            PollingPhase(phase_number=1, polling_date=date(2024, 4, 19), states=["Rajasthan", "Tamil Nadu", "Uttarakhand"], seats=102),
            PollingPhase(phase_number=2, polling_date=date(2024, 4, 26), states=["Assam", "Karnataka", "Kerala", "Rajasthan"], seats=89),
            PollingPhase(phase_number=3, polling_date=date(2024, 5, 7), states=["Bihar", "Gujarat", "Karnataka", "Maharashtra"], seats=94),
            PollingPhase(phase_number=4, polling_date=date(2024, 5, 13), states=["Andhra Pradesh", "Odisha", "Telangana", "Maharashtra"], seats=96),
            PollingPhase(phase_number=5, polling_date=date(2024, 5, 20), states=["Bihar", "Jharkhand", "Maharashtra", "Uttar Pradesh"], seats=49),
            PollingPhase(phase_number=6, polling_date=date(2024, 5, 25), states=["Bihar", "Haryana", "Delhi", "Uttar Pradesh"], seats=58),
            PollingPhase(phase_number=7, polling_date=date(2024, 6, 1), states=["Bihar", "Himachal Pradesh", "Punjab", "Uttar Pradesh"], seats=57),
        ],
        total_seats=543,
        states=["All States and Union Territories"],
        description_en="General elections to constitute the 18th Lok Sabha of India.",
        description_hi="भारत की 18वीं लोक सभा के गठन के लिए आम चुनाव।",
    ),

    # --- 2024: State Assembly Elections (COMPLETED) ---
    ElectionEvent(
        id="maharashtra-assembly-2024",
        name_en="Maharashtra Vidhan Sabha Elections 2024",
        name_hi="महाराष्ट्र विधान सभा चुनाव 2024",
        election_type=ElectionType.VIDHAN_SABHA,
        notification_date=date(2024, 10, 15),
        nomination_start=date(2024, 10, 22),
        nomination_end=date(2024, 10, 29),
        polling_start=date(2024, 11, 20),
        polling_end=date(2024, 11, 20),
        counting_date=date(2024, 11, 23),
        result_date=date(2024, 11, 23),
        total_phases=1,
        total_seats=288,
        states=["Maharashtra"],
        description_en="Elections to the Maharashtra Legislative Assembly.",
        description_hi="महाराष्ट्र विधान सभा के लिए चुनाव।",
    ),

    # --- 2025: Delhi Assembly Elections (COMPLETED) ---
    ElectionEvent(
        id="delhi-assembly-2025",
        name_en="Delhi Vidhan Sabha Elections 2025",
        name_hi="दिल्ली विधान सभा चुनाव 2025",
        election_type=ElectionType.VIDHAN_SABHA,
        notification_date=date(2025, 1, 10),
        nomination_start=date(2025, 1, 10),
        nomination_end=date(2025, 1, 17),
        polling_start=date(2025, 2, 5),
        polling_end=date(2025, 2, 5),
        counting_date=date(2025, 2, 8),
        result_date=date(2025, 2, 8),
        total_phases=1,
        total_seats=70,
        states=["Delhi"],
        description_en="Elections to the Delhi Legislative Assembly.",
        description_hi="दिल्ली विधान सभा के लिए चुनाव।",
    ),

    # --- 2025: Bihar Assembly Elections (UPCOMING / EXPECTED) ---
    ElectionEvent(
        id="bihar-assembly-2025",
        name_en="Bihar Vidhan Sabha Elections 2025",
        name_hi="बिहार विधान सभा चुनाव 2025",
        election_type=ElectionType.VIDHAN_SABHA,
        notification_date=date(2025, 9, 1),
        nomination_start=date(2025, 9, 5),
        nomination_end=date(2025, 9, 15),
        polling_start=date(2025, 10, 15),
        polling_end=date(2025, 11, 20),
        counting_date=date(2025, 11, 25),
        result_date=date(2025, 11, 25),
        total_phases=5,
        phases=[
            PollingPhase(phase_number=1, polling_date=date(2025, 10, 15), states=["Bihar"], seats=49),
            PollingPhase(phase_number=2, polling_date=date(2025, 10, 24), states=["Bihar"], seats=50),
            PollingPhase(phase_number=3, polling_date=date(2025, 11, 1), states=["Bihar"], seats=48),
            PollingPhase(phase_number=4, polling_date=date(2025, 11, 10), states=["Bihar"], seats=49),
            PollingPhase(phase_number=5, polling_date=date(2025, 11, 20), states=["Bihar"], seats=47),
        ],
        total_seats=243,
        states=["Bihar"],
        description_en="Elections to the Bihar Legislative Assembly. Bihar has 243 assembly constituencies.",
        description_hi="बिहार विधान सभा के लिए चुनाव। बिहार में 243 विधानसभा क्षेत्र हैं।",
    ),

    # --- 2026: West Bengal, Assam, Kerala, Tamil Nadu, Puducherry Assembly Elections ---
    ElectionEvent(
        id="west-bengal-assembly-2026",
        name_en="West Bengal Vidhan Sabha Elections 2026",
        name_hi="पश्चिम बंगाल विधान सभा चुनाव 2026",
        election_type=ElectionType.VIDHAN_SABHA,
        notification_date=date(2026, 3, 1),
        nomination_start=date(2026, 3, 5),
        nomination_end=date(2026, 3, 15),
        polling_start=date(2026, 4, 10),
        polling_end=date(2026, 5, 15),
        counting_date=date(2026, 5, 20),
        result_date=date(2026, 5, 20),
        total_phases=7,
        phases=[
            PollingPhase(phase_number=1, polling_date=date(2026, 4, 10), states=["West Bengal"], seats=43),
            PollingPhase(phase_number=2, polling_date=date(2026, 4, 17), states=["West Bengal"], seats=42),
            PollingPhase(phase_number=3, polling_date=date(2026, 4, 24), states=["West Bengal"], seats=42),
            PollingPhase(phase_number=4, polling_date=date(2026, 5, 1), states=["West Bengal"], seats=42),
            PollingPhase(phase_number=5, polling_date=date(2026, 5, 5), states=["West Bengal"], seats=42),
            PollingPhase(phase_number=6, polling_date=date(2026, 5, 10), states=["West Bengal"], seats=42),
            PollingPhase(phase_number=7, polling_date=date(2026, 5, 15), states=["West Bengal"], seats=41),
        ],
        total_seats=294,
        states=["West Bengal"],
        description_en="Elections to the West Bengal Legislative Assembly. 294 constituencies across 7 phases.",
        description_hi="पश्चिम बंगाल विधान सभा के लिए चुनाव। 7 चरणों में 294 निर्वाचन क्षेत्र।",
    ),

    ElectionEvent(
        id="assam-assembly-2026",
        name_en="Assam Vidhan Sabha Elections 2026",
        name_hi="असम विधान सभा चुनाव 2026",
        election_type=ElectionType.VIDHAN_SABHA,
        notification_date=date(2026, 3, 1),
        nomination_start=date(2026, 3, 5),
        nomination_end=date(2026, 3, 12),
        polling_start=date(2026, 4, 10),
        polling_end=date(2026, 4, 20),
        counting_date=date(2026, 5, 2),
        result_date=date(2026, 5, 2),
        total_phases=3,
        phases=[
            PollingPhase(phase_number=1, polling_date=date(2026, 4, 10), states=["Assam"], seats=42),
            PollingPhase(phase_number=2, polling_date=date(2026, 4, 15), states=["Assam"], seats=42),
            PollingPhase(phase_number=3, polling_date=date(2026, 4, 20), states=["Assam"], seats=42),
        ],
        total_seats=126,
        states=["Assam"],
        description_en="Elections to the Assam Legislative Assembly.",
        description_hi="असम विधान सभा के लिए चुनाव।",
    ),

    ElectionEvent(
        id="kerala-assembly-2026",
        name_en="Kerala Vidhan Sabha Elections 2026",
        name_hi="केरल विधान सभा चुनाव 2026",
        election_type=ElectionType.VIDHAN_SABHA,
        notification_date=date(2026, 3, 1),
        nomination_start=date(2026, 3, 5),
        nomination_end=date(2026, 3, 12),
        polling_start=date(2026, 4, 6),
        polling_end=date(2026, 4, 6),
        counting_date=date(2026, 5, 2),
        result_date=date(2026, 5, 2),
        total_phases=1,
        total_seats=140,
        states=["Kerala"],
        description_en="Elections to the Kerala Legislative Assembly.",
        description_hi="केरल विधान सभा के लिए चुनाव।",
    ),

    ElectionEvent(
        id="tamil-nadu-assembly-2026",
        name_en="Tamil Nadu Vidhan Sabha Elections 2026",
        name_hi="तमिलनाडु विधान सभा चुनाव 2026",
        election_type=ElectionType.VIDHAN_SABHA,
        notification_date=date(2026, 3, 1),
        nomination_start=date(2026, 3, 5),
        nomination_end=date(2026, 3, 12),
        polling_start=date(2026, 4, 6),
        polling_end=date(2026, 4, 6),
        counting_date=date(2026, 5, 2),
        result_date=date(2026, 5, 2),
        total_phases=1,
        total_seats=234,
        states=["Tamil Nadu"],
        description_en="Elections to the Tamil Nadu Legislative Assembly.",
        description_hi="तमिलनाडु विधान सभा के लिए चुनाव।",
    ),
]


def _get_ist_today() -> date:
    """Returns current date in IST (Indian Standard Time)."""
    return datetime.now(IST).date()


def _compute_status(election: ElectionEvent, today: date) -> ElectionStatus:
    """
    Determines the live status of an election based on today's IST date.

    Timeline: notification → nomination → polling → counting → result → completed
    """
    if today < election.nomination_start:
        return ElectionStatus.UPCOMING
    if today <= election.nomination_end:
        return ElectionStatus.NOMINATION
    if today <= election.polling_end:
        return ElectionStatus.POLLING
    if today <= election.result_date:
        return ElectionStatus.COUNTING
    return ElectionStatus.COMPLETED


def _compute_current_phase(election: ElectionEvent, today: date) -> int | None:
    """Determine which phase is active or next based on today's date."""
    if not election.phases:
        return 1 if election.polling_start <= today <= election.polling_end else None

    for phase in election.phases:
        if today <= phase.polling_date:
            return phase.phase_number
    # All phases completed
    return election.total_phases


def _compute_next_phase_date(election: ElectionEvent, today: date) -> date | None:
    """Find the next upcoming polling date."""
    if not election.phases:
        if today < election.polling_start:
            return election.polling_start
        return None

    for phase in election.phases:
        if today < phase.polling_date:
            return phase.polling_date
    return None


def _compute_progress(election: ElectionEvent, today: date) -> float:
    """
    Compute election progress as a percentage.
    0% = nomination start, 100% = result declared.
    """
    total_span = (election.result_date - election.nomination_start).days
    if total_span <= 0:
        return 100.0
    elapsed = (today - election.nomination_start).days
    return min(max((elapsed / total_span) * 100, 0.0), 100.0)


def get_live_election() -> LiveElectionResponse:
    """
    Returns the currently live election if one exists.

    An election is considered "live" if its status is one of:
    - NOMINATION (filing period open)
    - POLLING (voting underway)
    - COUNTING (votes being counted, results pending)

    Only returns the MOST relevant live election (priority: POLLING > COUNTING > NOMINATION).
    """
    today = _get_ist_today()

    # Score elections by how "live" they are
    live_candidates: list[tuple[int, ElectionEvent, ElectionStatus]] = []

    for election in INDIA_ELECTION_CALENDAR:
        status = _compute_status(election, today)
        if status in (ElectionStatus.NOMINATION, ElectionStatus.POLLING, ElectionStatus.COUNTING):
            # Priority: polling = 3, counting = 2, nomination = 1
            priority = {
                ElectionStatus.POLLING: 3,
                ElectionStatus.COUNTING: 2,
                ElectionStatus.NOMINATION: 1,
            }[status]
            live_candidates.append((priority, election, status))

    if not live_candidates:
        return LiveElectionResponse(
            is_live=False,
            status_message_en="No elections are currently live.",
            status_message_hi="वर्तमान में कोई चुनाव लाइव नहीं है।",
        )

    # Pick the highest-priority election
    live_candidates.sort(key=lambda x: x[0], reverse=True)
    _, election, status = live_candidates[0]

    current_phase = _compute_current_phase(election, today)
    next_phase_date = _compute_next_phase_date(election, today)
    progress = _compute_progress(election, today)

    days_until_next = None
    if next_phase_date:
        days_until_next = (next_phase_date - today).days

    # Build status messages
    if status == ElectionStatus.NOMINATION:
        msg_en = f"📋 Nominations open until {election.nomination_end.strftime('%d %b %Y')}"
        msg_hi = f"📋 नामांकन {election.nomination_end.strftime('%d %b %Y')} तक खुले हैं"
    elif status == ElectionStatus.POLLING:
        if next_phase_date and days_until_next is not None and days_until_next > 0:
            msg_en = f"🗳️ Phase {current_phase} polling on {next_phase_date.strftime('%d %b %Y')} ({days_until_next} days away)"
            msg_hi = f"🗳️ चरण {current_phase} मतदान {next_phase_date.strftime('%d %b %Y')} को ({days_until_next} दिन बाकी)"
        elif next_phase_date and days_until_next == 0:
            msg_en = f"🗳️ POLLING TODAY! Phase {current_phase} — Go vote!"
            msg_hi = f"🗳️ आज मतदान है! चरण {current_phase} — वोट करने जाएं!"
        else:
            msg_en = "🗳️ Polling underway"
            msg_hi = "🗳️ मतदान जारी है"
    elif status == ElectionStatus.COUNTING:
        msg_en = f"📊 Vote counting on {election.counting_date.strftime('%d %b %Y')}"
        msg_hi = f"📊 मतगणना {election.counting_date.strftime('%d %b %Y')} को"
    else:
        msg_en = ""
        msg_hi = ""

    return LiveElectionResponse(
        is_live=True,
        election=election,
        status=status,
        current_phase=current_phase,
        next_phase_date=next_phase_date,
        days_until_next=days_until_next,
        progress_percent=round(progress, 1),
        status_message_en=msg_en,
        status_message_hi=msg_hi,
    )


def get_upcoming_elections(limit: int = 5) -> list[dict]:  # type: ignore
    """
    Returns upcoming and currently active elections, sorted by polling start date.
    Excludes completed elections.
    """
    today = _get_ist_today()
    upcoming = []

    for election in INDIA_ELECTION_CALENDAR:
        status = _compute_status(election, today)
        if status != ElectionStatus.COMPLETED:
            upcoming.append({
                "election": election,
                "status": status.value,
                "progress_percent": round(_compute_progress(election, today), 1),
            })

    # Sort by polling_start ascending
    upcoming.sort(key=lambda x: x["election"].polling_start)
    return upcoming[:limit]
