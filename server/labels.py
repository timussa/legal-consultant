"""Human-readable Russian labels for dates, durations and people."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

MONTHS = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]


def local(iso: str, offset_hours: int) -> datetime:
    moment = datetime.fromisoformat(iso)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone(timedelta(hours=offset_hours)))


def date_label(iso: str | None, offset_hours: int, with_time: bool = False) -> str:
    if not iso:
        return ""
    moment = local(iso, offset_hours)
    today = datetime.now(moment.tzinfo).date()
    clock = moment.strftime("%H:%M")
    if moment.date() == today:
        return f"сегодня, {clock}" if with_time else "сегодня"
    if moment.date() == today - timedelta(days=1):
        return f"вчера, {clock}" if with_time else "вчера"
    label = f"{moment.day} {MONTHS[moment.month - 1]}"
    return label if moment.year == today.year else f"{label} {moment.year}"


def iso_to_ru(day: str | None) -> str:
    """2025-03-01 -> 01.03.2025"""
    if not day:
        return ""
    year, month, dom = day[:10].split("-")
    return f"{dom}.{month}.{year}"


def seconds_label(milliseconds: float | None) -> str:
    if not milliseconds:
        return "—"
    return f"{milliseconds / 1000:.1f} с".replace(".", ",")


def initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def short_name(name: str) -> str:
    """Анна Корнеева -> А. Корнеева"""
    parts = [p for p in name.split() if p]
    if len(parts) < 2:
        return name
    return f"{parts[0][0]}. {' '.join(parts[1:])}"


def percent(part: int, total: int) -> str:
    if not total:
        return "—"
    return f"{round(100 * part / total)} %"
