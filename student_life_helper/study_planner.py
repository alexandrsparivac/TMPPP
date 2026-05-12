from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from .models import Priority, ScheduleEvent, Task


WEEKDAYS = ["Luni", "Marti", "Miercuri", "Joi", "Vineri", "Sambata", "Duminica"]
PRIORITY_MINUTES = {
    Priority.HIGH: 120,
    Priority.MEDIUM: 75,
    Priority.LOW: 45,
}
PRIORITY_RANK = {
    Priority.HIGH: 0,
    Priority.MEDIUM: 1,
    Priority.LOW: 2,
}


@dataclass(frozen=True)
class TimeBlock:
    day: date
    start: time
    end: time
    label: str = ""

    def overlaps(self, other: "TimeBlock") -> bool:
        if self.day != other.day:
            return False
        return self.start < other.end and other.start < self.end


@dataclass(frozen=True)
class PlannedStudySession:
    task: Task
    day: date
    start: time
    end: time
    minutes: int
    after_deadline: bool


@dataclass(frozen=True)
class StudyPlanResult:
    sessions: list[PlannedStudySession]
    conflicts: list[str]
    warnings: list[str]

    def to_lines(self) -> list[str]:
        if not self.sessions:
            return [
                "Saptamana aceasta nu ai taskuri active. Pastreaza 30 minute pentru recapitulare usoara.",
                "Organizeaza notitele si pregateste materialele pentru urmatoarele deadline-uri.",
            ]

        lines: list[str] = []
        for session in self.sessions:
            status = "recuperare dupa deadline" if session.after_deadline else "inainte de deadline"
            lines.append(
                f"{session.day.isoformat()} {session.start.strftime('%H:%M')}-{session.end.strftime('%H:%M')}: "
                f"{session.task.title} ({session.minutes} min, {session.task.priority.value}, {status})"
            )

        if self.conflicts:
            lines.append("Conflicte evitate: " + "; ".join(self.conflicts[:5]))
        if self.warnings:
            lines.extend(self.warnings)
        return lines


class SmartStudyPlanner:
    """Builds a weekly study plan around fixed schedule events."""

    def build_weekly_plan(
        self,
        tasks: list[Task],
        schedule: list[ScheduleEvent],
        today: date | None = None,
    ) -> StudyPlanResult:
        start_day = today or date.today()
        active_tasks = [task for task in tasks if not task.completed]
        active_tasks.sort(key=lambda task: (task.due_date, PRIORITY_RANK[task.priority], task.created_at))
        busy_blocks = self._busy_blocks(schedule, start_day)
        free_slots = self._free_slots(start_day, busy_blocks)
        conflicts = self._conflict_notes(busy_blocks)

        sessions: list[PlannedStudySession] = []
        warnings: list[str] = []
        slot_index = 0

        for task in active_tasks:
            remaining = self._recommended_minutes(task, start_day)
            planned_for_task = 0
            while remaining > 0 and slot_index < len(free_slots):
                slot = free_slots[slot_index]
                slot_index += 1
                minutes = min(remaining, self._minutes_between(slot.start, slot.end))
                if minutes < 25:
                    continue
                session = PlannedStudySession(
                    task=task,
                    day=slot.day,
                    start=slot.start,
                    end=self._add_minutes(slot.start, minutes),
                    minutes=minutes,
                    after_deadline=slot.day > task.due_date,
                )
                sessions.append(session)
                remaining -= minutes
                planned_for_task += minutes
                if slot.day > task.due_date:
                    warnings.append(
                        f"Atentie: {task.title} nu incape complet inainte de deadline si este reprogramat pe {slot.day.isoformat()}."
                    )
                    break

            if remaining > 0 and planned_for_task == 0:
                warnings.append(
                    f"Nu am gasit interval liber pentru {task.title} in urmatoarele 7 zile."
                )
            elif remaining > 0:
                warnings.append(
                    f"{task.title}: mai raman aproximativ {remaining} minute de programat."
                )

        return StudyPlanResult(sessions=sessions, conflicts=conflicts, warnings=self._dedupe(warnings))

    def _recommended_minutes(self, task: Task, today: date) -> int:
        base = PRIORITY_MINUTES[task.priority]
        days_left = (task.due_date - today).days
        if days_left <= 1:
            return base + 30
        if days_left <= 3:
            return base + 15
        return base

    def _busy_blocks(self, schedule: list[ScheduleEvent], start_day: date) -> list[TimeBlock]:
        blocks: list[TimeBlock] = []
        for offset in range(7):
            day = start_day + timedelta(days=offset)
            weekday = WEEKDAYS[day.weekday()]
            for event in schedule:
                if event.weekday != weekday:
                    continue
                start = self._parse_time(event.time)
                end = self._add_minutes(start, 90)
                blocks.append(TimeBlock(day=day, start=start, end=end, label=event.subject))
        return sorted(blocks, key=lambda item: (item.day, item.start))

    def _free_slots(self, start_day: date, busy_blocks: list[TimeBlock]) -> list[TimeBlock]:
        day_windows = [
            (time(8, 0), time(12, 0)),
            (time(13, 0), time(18, 0)),
            (time(19, 0), time(21, 0)),
        ]
        slots: list[TimeBlock] = []
        for offset in range(7):
            day = start_day + timedelta(days=offset)
            busy_today = [block for block in busy_blocks if block.day == day]
            for window_start, window_end in day_windows:
                cursor = window_start
                for busy in busy_today:
                    if busy.end <= cursor or busy.start >= window_end:
                        continue
                    slots.extend(self._split_study_slots(day, cursor, min(busy.start, window_end)))
                    cursor = max(cursor, busy.end)
                slots.extend(self._split_study_slots(day, cursor, window_end))
        return slots

    def _split_study_slots(self, day: date, start: time, end: time) -> list[TimeBlock]:
        slots: list[TimeBlock] = []
        cursor = start
        while self._minutes_between(cursor, end) >= 25:
            minutes = min(45, self._minutes_between(cursor, end))
            slot_end = self._add_minutes(cursor, minutes)
            slots.append(TimeBlock(day=day, start=cursor, end=slot_end))
            cursor = self._add_minutes(slot_end, 15)
        return slots

    def _conflict_notes(self, busy_blocks: list[TimeBlock]) -> list[str]:
        return [
            f"{block.day.isoformat()} {block.start.strftime('%H:%M')}-{block.end.strftime('%H:%M')} {block.label}"
            for block in busy_blocks
            if block.label
        ]

    def _parse_time(self, value: str) -> time:
        return datetime.strptime(value, "%H:%M").time()

    def _add_minutes(self, value: time, minutes: int) -> time:
        base = datetime.combine(date.today(), value)
        return (base + timedelta(minutes=minutes)).time()

    def _minutes_between(self, start: time, end: time) -> int:
        start_dt = datetime.combine(date.today(), start)
        end_dt = datetime.combine(date.today(), end)
        return int((end_dt - start_dt).total_seconds() // 60)

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result
