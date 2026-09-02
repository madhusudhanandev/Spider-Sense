from typing import Optional

from pydantic import BaseModel


class TransitionPattern(BaseModel):
    event_type: str
    from_value: str
    to_value: str
    occurrence_count: int


class EvolutionPatternsResult(BaseModel):
    total_campaigns_analyzed: int
    campaigns_with_mutations: int
    common_transitions: list[TransitionPattern] = []
    first_mutation_type_distribution: dict[str, int] = {}
    median_time_to_first_mutation_hours: Optional[float] = None
    sample_size_note: str


class MutationTypeCount(BaseModel):
    event_type: str
    occurrence_count: int


class SuggestedNextMutation(BaseModel):
    """
    A transparent historical lookup, NOT a prediction. current_state is
    this campaign's most recent mutation type (or null if it hasn't
    mutated yet); distribution shows what type of change followed that
    same state in OTHER campaigns; comparable_case_count is the real
    sample size backing that distribution, which is very often small or
    zero -- see `note` for the honest caveat every time.
    """
    current_state: Optional[str] = None
    comparable_case_count: int
    distribution: list[MutationTypeCount] = []
    note: str