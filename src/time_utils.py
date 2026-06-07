from __future__ import annotations

from datetime import timedelta

def parse_duration(duration: str) -> timedelta:
    """Gjør HH:MM:SS om til timedelta"""
    
    hours, minutes, seconds = duration.split(":")
    
    return timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds)
    )
    
def format_timedelta(duration: timedelta) -> str:
    
    total_seconds = int(duration.total_seconds())
    
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def calculate_duration_difference(new_duration: str, old_duration: str) -> str:
    """Beregner differansen mellom to HH:MM:SS-verdier."""

    difference = parse_duration(new_duration) - parse_duration(old_duration)

    return format_timedelta(difference)