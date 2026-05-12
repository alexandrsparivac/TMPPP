from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

from .facade import StudentLifeFacade
from .models import Priority, TransactionType
from .ports import CommandRequest, CommandResponse
from .strategies import TaskSortStrategyFactory, TipStrategyFactory
from .ui import h, reply, title as ui_title


FORM_TRIGGER = "__form__"
TEXT_COMMAND = "text"
CANCEL_COMMAND = "cancel"


@dataclass(frozen=True)
class CompletedForm:
    command: str
    args: str


@dataclass(frozen=True)
class FormStep:
    field: str
    prompt: str | Callable[[CommandRequest, dict[str, str]], str]
    validator: Callable[[str], str]
    keyboard: list[list[str]] | None = None


@dataclass(frozen=True)
class FormSpec:
    command: str
    steps: list[FormStep]
    build_args: Callable[[dict[str, str]], str]
    start_on_empty: bool = True


@dataclass
class FormState:
    spec: FormSpec
    answers: dict[str, str] = field(default_factory=dict)
    index: int = 0


class ConversationManager:
    """Keeps short multi-step forms per user."""

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade
        self._states: dict[str, FormState] = {}
        self._forms = self._build_forms()

    def has_active(self, user_id: str) -> bool:
        return user_id in self._states

    def should_start(self, command: str, args: str) -> bool:
        spec = self._forms.get(command)
        if spec is None:
            return False
        cleaned = args.strip()
        return cleaned == FORM_TRIGGER or (not cleaned and spec.start_on_empty)

    def start(self, request: CommandRequest) -> CommandResponse:
        spec = self._forms[request.command]
        state = FormState(spec=spec)
        self._states[request.user_id] = state
        return self._prompt_response(request, state)

    def cancel(self, user_id: str) -> CommandResponse:
        from student_life_helper.adapters import MAIN_KEYBOARD
        self._states.pop(user_id, None)
        return reply(f"{ui_title('❌', 'Formular anulat')}\\n\\nAlege un tab pentru alta actiune.", keyboard=MAIN_KEYBOARD)

    def accept_answer(self, request: CommandRequest) -> CommandResponse | CompletedForm:
        state = self._states[request.user_id]
        step = state.spec.steps[state.index]
        try:
            answer = step.validator(request.args)
        except ValueError as exc:
            prompt = self._prompt_text(step, request, state.answers)
            return reply(
                f"⚠️ <b>Eroare:</b> {h(exc)}\n\n{prompt}",
                keyboard=step.keyboard or cancel_keyboard(),
            )

        state.answers[step.field] = answer
        state.index += 1
        if state.index < len(state.spec.steps):
            return self._prompt_response(request, state)

        self._states.pop(request.user_id, None)
        return CompletedForm(
            command=state.spec.command,
            args=state.spec.build_args(state.answers),
        )

    def _prompt_response(self, request: CommandRequest, state: FormState) -> CommandResponse:
        step = state.spec.steps[state.index]
        return reply(
            self._prompt_text(step, request, state.answers),
            keyboard=step.keyboard or cancel_keyboard(),
        )

    def _prompt_text(
        self,
        step: FormStep,
        request: CommandRequest,
        answers: dict[str, str],
    ) -> str:
        prompt = step.prompt(request, answers) if callable(step.prompt) else step.prompt
        return (
            f"{ui_title('✍️', 'Introducere date')}\n\n"
            f"{h(prompt)}\n\n"
            "Scrie ❌ Cancel pentru anulare."
        )

    def _build_forms(self) -> dict[str, FormSpec]:
        return {
            "explain": FormSpec(
                command="explain",
                steps=[
                    FormStep("topic", "🤖 Ce concept dorești să îți explic? (ex: polimorfismul în Java):", required("Conceptul"))
                ],
                build_args=lambda answers: answers["topic"],
            ),
            "pomodorostart": FormSpec(
                command="pomodorostart",
                steps=[
                    FormStep("minutes", "Câte minute vrei să dureze sesiunea de studiu? (ex: 25):", minutes_value, keyboard=[["25", "30", "45", "60"], ["❌ Cancel"]])
                ],
                build_args=lambda answers: answers["minutes"],
            ),
            "addhabit": FormSpec(
                command="addhabit",
                steps=[
                    FormStep("name", "Numele obiceiului (ex: Citește 10 pagini):", required("Numele obiceiului"))
                ],
                build_args=lambda answers: answers["name"],
            ),
            "loghabit": FormSpec(
                command="loghabit",
                steps=[
                    FormStep("prefix", "Scrie primele litere din ID-ul sau numele obiceiului pentru a-l bifa azi:", lambda x: x)
                ],
                build_args=lambda answers: answers["prefix"],
            ),
            "profile": FormSpec(
                command="profile",
                steps=[
                    FormStep("name", "Introduceti numele studentului:", required("Numele")),
                    FormStep("university", "Introduceti universitatea:", required("Universitatea")),
                    FormStep("faculty", "Introduceti facultatea:", required("Facultatea")),
                    FormStep("group", "Introduceti grupa:", required("Grupa")),
                    FormStep("year", "Introduceti anul de studii:", year_value),
                ],
                build_args=join_args("name", "university", "faculty", "group", "year"),
            ),
            "addtask": FormSpec(
                command="addtask",
                steps=[
                    FormStep("title", "Introduceti denumirea taskului:", required("Denumirea")),
                    FormStep("due_date", "Introduceti data limita (YYYY-MM-DD):", iso_date),
                    FormStep(
                        "priority",
                        "Introduceti prioritatea:",
                        priority_value,
                        keyboard=[["low", "medium", "high"], ["❌ Cancel"]],
                    ),
                ],
                build_args=join_args("title", "due_date", "priority"),
            ),
            "done": FormSpec(
                command="done",
                steps=[
                    FormStep(
                        "task_number",
                        self._done_prompt,
                        required("Numarul taskului"),
                    )
                ],
                build_args=lambda answers: answers["task_number"],
            ),
            "strategy": FormSpec(
                command="strategy",
                steps=[
                    FormStep(
                        "strategy",
                        "Introduceti strategia de sortare:",
                        strategy_value,
                        keyboard=[TaskSortStrategyFactory.names(), ["❌ Cancel"]],
                    )
                ],
                build_args=lambda answers: answers["strategy"],
            ),
            "search": FormSpec(
                command="search",
                steps=[
                    FormStep("query", "Introduceti textul de cautat:", required("Textul de cautare"))
                ],
                build_args=lambda answers: answers["query"],
            ),
            "addnote": FormSpec(
                command="addnote",
                steps=[
                    FormStep("title", "Introduceti titlul notitei:", required("Titlul")),
                    FormStep("body", "Introduceti textul notitei:", required("Textul")),
                    FormStep("tag", "Introduceti tagul/categoria:", required("Tagul")),
                ],
                build_args=join_args("title", "body", "tag"),
            ),
            "gradecalc": FormSpec(
                command="gradecalc",
                steps=[
                    FormStep("current", "Introduceti nota curenta:", grade_value),
                    FormStep("desired", "Introduceti media dorita:", grade_value),
                    FormStep("weight", "Introduceti ponderea examenului in procente:", percent_value),
                ],
                build_args=join_args("current", "desired", "weight"),
            ),
            "addschedule": FormSpec(
                command="addschedule",
                steps=[
                    FormStep(
                        "weekday",
                        "Introduceti ziua:",
                        required("Ziua"),
                        keyboard=[["Luni", "Marti", "Miercuri"], ["Joi", "Vineri", "Sambata"], ["Duminica", "❌ Cancel"]],
                    ),
                    FormStep("time", "Introduceti ora (HH:MM):", time_value),
                    FormStep("subject", "Introduceti materia:", required("Materia")),
                    FormStep("location", "Introduceti sala/locatia:", required("Locatia")),
                ],
                build_args=join_args("weekday", "time", "subject", "location"),
            ),
            "budget": FormSpec(
                command="budget",
                steps=[
                    FormStep(
                        "kind",
                        "Introduceti tipul tranzactiei:",
                        transaction_type_value,
                        keyboard=[["income", "expense"], ["❌ Cancel"]],
                    ),
                    FormStep("amount", "Introduceti suma:", amount_value),
                    FormStep("category", "Introduceti categoria:", required("Categoria")),
                    FormStep("description", "Introduceti descrierea:", required("Descrierea")),
                ],
                build_args=join_args("kind", "amount", "category", "description"),
            ),
            "budgetlimit": FormSpec(
                command="budgetlimit",
                steps=[
                    FormStep("category", "Introduceti categoria pentru limita lunara:", required("Categoria")),
                    FormStep("amount", "Introduceti limita lunara:", amount_value),
                ],
                build_args=join_args("category", "amount"),
            ),
            "recurringexpense": FormSpec(
                command="recurringexpense",
                steps=[
                    FormStep("amount", "Introduceti suma recurenta:", amount_value),
                    FormStep("category", "Introduceti categoria recurentei:", required("Categoria")),
                    FormStep("description", "Introduceti descrierea recurentei:", required("Descrierea")),
                    FormStep("day", "Introduceti ziua lunii pentru recurenta:", day_of_month_value),
                ],
                build_args=join_args("amount", "category", "description", "day"),
            ),
            "tip": FormSpec(
                command="tip",
                steps=[
                    FormStep(
                        "tip_type",
                        "Introduceti tipul sfatului:",
                        tip_value,
                        keyboard=[TipStrategyFactory.names(), ["❌ Cancel"]],
                    )
                ],
                build_args=lambda answers: answers["tip_type"],
            ),
        }

    def _done_prompt(self, request: CommandRequest, answers: dict[str, str]) -> str:
        tasks, _strategy = self._facade.list_tasks(request.user_id)
        active = [task for task in tasks if not task.completed]
        if not active:
            return "Nu ai taskuri active. Introduceti totusi o denumire daca vrei sa incerci:"
        rows = "\n".join(
            f"{index}. {task.title} | {task.due_date.isoformat()} | {task.priority.value}"
            for index, task in enumerate(active[:8], start=1)
        )
        return "Introduceti numarul taskului de finalizat:\n" + rows


def cancel_keyboard() -> list[list[str]]:
    return [["❌ Cancel"]]


def join_args(*fields: str) -> Callable[[dict[str, str]], str]:
    return lambda answers: " | ".join(answers[field] for field in fields)


def required(label: str) -> Callable[[str], str]:
    def validate(value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"{label} este obligatoriu.")
        return cleaned

    return validate


def iso_date(value: str) -> str:
    cleaned = value.strip()
    try:
        date.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError("Data trebuie sa fie in format YYYY-MM-DD.") from exc
    return cleaned


def year_value(value: str) -> str:
    cleaned = value.strip()
    try:
        year = int(cleaned)
    except ValueError as exc:
        raise ValueError("Anul trebuie sa fie un numar.") from exc
    if year < 1 or year > 8:
        raise ValueError("Anul trebuie sa fie intre 1 si 8.")
    return str(year)


def priority_value(value: str) -> str:
    return Priority.from_text(value).value


def transaction_type_value(value: str) -> str:
    return TransactionType.from_text(value).value


def amount_value(value: str) -> str:
    cleaned = value.strip().replace(",", ".")
    try:
        amount = float(cleaned)
    except ValueError as exc:
        raise ValueError("Suma trebuie sa fie un numar.") from exc
    if amount <= 0:
        raise ValueError("Suma trebuie sa fie mai mare decat 0.")
    return f"{amount:.2f}"


def grade_value(value: str) -> str:
    cleaned = value.strip().replace(",", ".")
    try:
        grade = float(cleaned)
    except ValueError as exc:
        raise ValueError("Nota trebuie sa fie un numar.") from exc
    if grade < 1 or grade > 10:
        raise ValueError("Nota trebuie sa fie intre 1 si 10.")
    return f"{grade:.2f}"


def percent_value(value: str) -> str:
    cleaned = value.strip().replace(",", ".").replace("%", "")
    try:
        percent = float(cleaned)
    except ValueError as exc:
        raise ValueError("Ponderea trebuie sa fie un numar.") from exc
    if percent <= 0 or percent >= 100:
        raise ValueError("Ponderea trebuie sa fie intre 1 si 99.")
    return f"{percent:.2f}"


def day_of_month_value(value: str) -> str:
    cleaned = value.strip()
    try:
        day = int(cleaned)
    except ValueError as exc:
        raise ValueError("Ziua lunii trebuie sa fie un numar.") from exc
    if day < 1 or day > 31:
        raise ValueError("Ziua lunii trebuie sa fie intre 1 si 31.")
    return str(day)


def time_value(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) != 5 or cleaned[2] != ":":
        raise ValueError("Ora trebuie scrisa in format HH:MM.")
    hour, minute = cleaned.split(":")
    if not hour.isdigit() or not minute.isdigit():
        raise ValueError("Ora trebuie scrisa in format HH:MM.")
    if int(hour) > 23 or int(minute) > 59:
        raise ValueError("Ora introdusa nu este valida.")
    return cleaned


def strategy_value(value: str) -> str:
    cleaned = value.strip().lower()
    if cleaned not in TaskSortStrategyFactory.names():
        raise ValueError("Strategia trebuie sa fie: " + ", ".join(TaskSortStrategyFactory.names()))
    return cleaned


def tip_value(value: str) -> str:
    cleaned = value.strip().lower()
    if cleaned not in TipStrategyFactory.names():
        raise ValueError("Tipul de sfat trebuie sa fie: " + ", ".join(TipStrategyFactory.names()))
    return cleaned


def minutes_value(value: str) -> str:
    cleaned = value.strip()
    try:
        minutes = int(cleaned)
    except ValueError as exc:
        raise ValueError("Durata trebuie sa fie un numar intreg.") from exc
    if minutes <= 0 or minutes > 180:
        raise ValueError("Durata trebuie sa fie intre 1 si 180 minute.")
    return str(minutes)
