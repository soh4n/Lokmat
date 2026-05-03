"""
Unit tests for the election calendar service.

Verifies:
- Dynamic status computation based on IST date
- Phase tracking and progress calculation
- Live election detection and priority logic
- Upcoming elections filtering
"""

from datetime import date
from unittest.mock import patch

from api.services.election_calendar import (
    INDIA_ELECTION_CALENDAR,
    ElectionStatus,
    _compute_current_phase,
    _compute_progress,
    _compute_status,
    get_live_election,
    get_upcoming_elections,
)


class TestComputeStatus:
    """Tests for election status computation."""

    def test_upcoming_before_nomination(self) -> None:
        """Election before nomination start is UPCOMING."""
        election = INDIA_ELECTION_CALENDAR[0]  # Lok Sabha 2024
        result = _compute_status(election, date(2024, 3, 1))
        assert result == ElectionStatus.UPCOMING

    def test_nomination_during_filing(self) -> None:
        """Election during nomination period is NOMINATION."""
        election = INDIA_ELECTION_CALENDAR[0]
        result = _compute_status(election, date(2024, 3, 25))
        assert result == ElectionStatus.NOMINATION

    def test_polling_during_voting(self) -> None:
        """Election during polling period is POLLING."""
        election = INDIA_ELECTION_CALENDAR[0]
        result = _compute_status(election, date(2024, 5, 10))
        assert result == ElectionStatus.POLLING

    def test_counting_after_polling(self) -> None:
        """Election after polling but before results is COUNTING."""
        election = INDIA_ELECTION_CALENDAR[0]
        result = _compute_status(election, date(2024, 6, 3))
        assert result == ElectionStatus.COUNTING

    def test_completed_after_results(self) -> None:
        """Election after result date is COMPLETED."""
        election = INDIA_ELECTION_CALENDAR[0]
        result = _compute_status(election, date(2024, 6, 10))
        assert result == ElectionStatus.COMPLETED


class TestComputePhase:
    """Tests for phase tracking."""

    def test_phase_before_polling(self) -> None:
        """Before any polling, returns phase 1."""
        election = INDIA_ELECTION_CALENDAR[0]  # Lok Sabha 2024 with 7 phases
        result = _compute_current_phase(election, date(2024, 4, 15))
        assert result == 1

    def test_phase_between_phases(self) -> None:
        """Between phases, returns next phase number."""
        election = INDIA_ELECTION_CALENDAR[0]
        result = _compute_current_phase(election, date(2024, 4, 20))
        assert result == 2  # After phase 1 (Apr 19), before phase 2 (Apr 26)

    def test_phase_after_all(self) -> None:
        """After all phases, returns total phases."""
        election = INDIA_ELECTION_CALENDAR[0]
        result = _compute_current_phase(election, date(2024, 6, 5))
        assert result == 7

    def test_single_phase_election(self) -> None:
        """Single-phase election returns 1 during polling."""
        # Maharashtra 2024 — single phase
        election = INDIA_ELECTION_CALENDAR[1]
        result = _compute_current_phase(election, date(2024, 11, 20))
        assert result == 1


class TestComputeProgress:
    """Tests for progress percentage."""

    def test_zero_at_start(self) -> None:
        """Progress is 0% at nomination start."""
        election = INDIA_ELECTION_CALENDAR[0]
        result = _compute_progress(election, election.nomination_start)
        assert result == 0.0

    def test_hundred_at_end(self) -> None:
        """Progress is 100% at or after result date."""
        election = INDIA_ELECTION_CALENDAR[0]
        result = _compute_progress(election, election.result_date)
        assert result == 100.0

    def test_midpoint_progress(self) -> None:
        """Progress is between 0 and 100 during the election."""
        election = INDIA_ELECTION_CALENDAR[0]
        result = _compute_progress(election, date(2024, 4, 25))
        assert 0.0 < result < 100.0


class TestGetLiveElection:
    """Tests for live election detection."""

    @patch("api.services.election_calendar._get_ist_today")
    def test_no_live_when_all_completed(self, mock_today) -> None:  # type: ignore
        """Returns is_live=False when all elections are completed."""
        mock_today.return_value = date(2030, 1, 1)
        result = get_live_election()
        assert result.is_live is False

    @patch("api.services.election_calendar._get_ist_today")
    def test_live_during_polling(self, mock_today) -> None:  # type: ignore
        """Returns is_live=True during a polling period."""
        # During Lok Sabha 2024 polling
        mock_today.return_value = date(2024, 5, 10)
        result = get_live_election()
        assert result.is_live is True
        assert result.status == ElectionStatus.POLLING

    @patch("api.services.election_calendar._get_ist_today")
    def test_live_returns_correct_election(self, mock_today) -> None:  # type: ignore
        """Returns the correct election during its active period."""
        mock_today.return_value = date(2024, 5, 10)
        result = get_live_election()
        assert result.election is not None
        assert result.election.id == "lok-sabha-2024"

    @patch("api.services.election_calendar._get_ist_today")
    def test_polling_priority_over_nomination(self, mock_today) -> None:  # type: ignore
        """Polling status takes priority over nomination."""
        # If two elections overlap — polling > nomination
        mock_today.return_value = date(2026, 4, 10)  # WB polling starts, Assam also
        result = get_live_election()
        assert result.is_live is True
        assert result.status == ElectionStatus.POLLING

    @patch("api.services.election_calendar._get_ist_today")
    def test_response_has_progress(self, mock_today) -> None:  # type: ignore
        """Live response includes progress percentage."""
        mock_today.return_value = date(2024, 5, 10)
        result = get_live_election()
        assert result.progress_percent > 0.0
        assert result.progress_percent < 100.0


class TestGetUpcomingElections:
    """Tests for upcoming elections list."""

    @patch("api.services.election_calendar._get_ist_today")
    def test_excludes_completed(self, mock_today) -> None:  # type: ignore
        """Completed elections are excluded."""
        mock_today.return_value = date(2025, 6, 1)
        upcoming = get_upcoming_elections()
        for item in upcoming:
            assert item["status"] != "completed"

    @patch("api.services.election_calendar._get_ist_today")
    def test_sorted_by_polling_start(self, mock_today) -> None:  # type: ignore
        """Results are sorted by polling start date."""
        mock_today.return_value = date(2025, 6, 1)
        upcoming = get_upcoming_elections()
        if len(upcoming) >= 2:
            dates = [item["election"].polling_start for item in upcoming]
            assert dates == sorted(dates)

    @patch("api.services.election_calendar._get_ist_today")
    def test_respects_limit(self, mock_today) -> None:  # type: ignore
        """Limit parameter caps results."""
        mock_today.return_value = date(2025, 1, 1)
        upcoming = get_upcoming_elections(limit=2)
        assert len(upcoming) <= 2
