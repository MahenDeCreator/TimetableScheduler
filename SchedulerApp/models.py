"""Top-level model module exposing application entities."""

from .model_definitions import (
    Classroom,
    DAYS_OF_WEEK,
    Faculty,
    Group,
    Subject,
    Teacher,
    TIME_SLOTS,
    TimeSlot,
)

__all__ = [
    'TIME_SLOTS',
    'DAYS_OF_WEEK',
    'Classroom',
    'Teacher',
    'TimeSlot',
    'Subject',
    'Faculty',
    'Group',
]
