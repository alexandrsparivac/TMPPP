import re

with open("student_life_helper/models.py", "r") as f:
    content = f.read()

habit_model = """
@dataclass(frozen=True)
class Habit:
    id: str
    name: str
    log_dates: list[str]
    created_at: datetime

    @property
    def short_id(self) -> str:
        return self.id.split("-")[0]
        
    def log_today(self) -> "Habit":
        today_iso = date.today().isoformat()
        if today_iso not in self.log_dates:
            new_logs = self.log_dates + [today_iso]
            return Habit(id=self.id, name=self.name, log_dates=new_logs, created_at=self.created_at)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "log_dates": self.log_dates,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Habit":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            log_dates=list(data.get("log_dates", [])),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )

@dataclass(frozen=True)
class Note:
"""

content = content.replace("@dataclass(frozen=True)\nclass Note:", habit_model)

with open("student_life_helper/models.py", "w") as f:
    f.write(content)
