from __future__ import annotations

import unittest
from datetime import date, timedelta
from uuid import uuid4

import mongomock

from student_life_helper.adapters import ConsoleAdapter
from student_life_helper.app import build_router
from student_life_helper.storage import MongoStorage


class StudentLifeHelperFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mongo_client = mongomock.MongoClient()
        self.storage = MongoStorage(
            database=f"student_life_test_{uuid4().hex}",
            client=self.mongo_client,
        )
        self.router = build_router(self.storage)
        self.adapter = ConsoleAdapter()

    def tearDown(self) -> None:
        self.mongo_client.close()

    def ask(self, text: str) -> str:
        response = self.router.handle(self.adapter.to_request(text, user_id="u1", user_name="Ana"))
        return response.text

    def test_profile_task_strategy_and_done_flow(self) -> None:
        profile = self.ask("/profile Ana | UTM | FCIM | FAF-231 | 2")
        self.assertIn("Profil salvat", profile)
        self.assertIn("Student Life Helper", self.ask("🏠 Start"))
        self.assertIn("Ce concept", self.ask("🤖 Intreaba (AI)"))
        self.assertIn("Formular anulat", self.ask("❌ Cancel"))
        self.assertIn("Ana", self.ask("👤 Profile"))
        self.assertIn("Comenzi", self.ask("❓ Help"))

        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        self.assertIn("Introduceti denumirea taskului", self.ask("➕ Add Task"))
        self.assertIn("Introduceti data limita", self.ask("Proiect TMPS"))
        self.assertIn("Introduceti prioritatea", self.ask(tomorrow))
        added = self.ask("high")
        self.assertIn("Task adaugat", added)
        self.assertIn("Reminder", added)

        tasks = self.ask("/tasks")
        self.assertIn("Proiect TMPS", tasks)
        self.assertIn("strategie: deadline", tasks)
        self.assertNotRegex(tasks, r"\b[a-f0-9]{8}\b \|")
        self.assertIn("Proiect TMPS", self.ask("📋 Tasks"))
        self.assertIn("Proiect TMPS", self.ask("📅 Deadlines"))
        self.assertIn("Introduceti numarul taskului", self.ask("✅ Done"))
        self.assertIn("Introduceti strategia", self.ask("⚙️ Strategy"))

        changed = self.ask("/strategy priority")
        self.assertIn("priority", changed)

        done = self.ask("/done 1")
        self.assertIn("Task finalizat", done)
        self.assertIn("Nu mai ai taskuri active", done)

    def test_schedule_budget_tip_and_aliases(self) -> None:
        self.assertIn("Introduceti numele studentului", self.ask("✏️ Set Profile"))
        self.assertIn("Introduceti universitatea", self.ask("Ana"))
        self.assertIn("Introduceti facultatea", self.ask("UTM"))
        self.assertIn("Introduceti grupa", self.ask("FCIM"))
        self.assertIn("Introduceti anul", self.ask("FAF-231"))
        self.assertIn("Profil salvat", self.ask("2"))

        self.assertIn("Introduceti ziua", self.ask("➕ Add Lesson"))
        self.assertIn("Introduceti ora", self.ask("Luni"))
        self.assertIn("Introduceti materia", self.ask("09:30"))
        self.assertIn("Introduceti sala", self.ask("Matematica"))
        self.assertIn("Eveniment adaugat", self.ask("A-204"))

        schedule = self.ask("/addschedule Luni | 09:30 | Matematica | A-204")
        self.assertIn("Eveniment adaugat", schedule)
        self.assertIn("Matematica", self.ask("/orar"))
        self.assertIn("Matematica", self.ask("🗓 Schedule"))
        self.assertIn("Matematica", self.ask("/search matematica"))
        self.assertIn("Introduceti textul de cautat", self.ask("🔍 Search"))
        self.assertIn("Matematica", self.ask("matematica"))

        self.assertIn("Introduceti tipul tranzactiei", self.ask("💰 Budget"))
        self.assertIn("Introduceti suma", self.ask("income"))
        self.assertIn("Introduceti categoria", self.ask("3000"))
        self.assertIn("Introduceti descrierea", self.ask("bursa"))
        self.assertIn("Tranzactie salvata", self.ask("bursa lunara"))

        expense = self.ask("/buget expense | 2500 | mancare | cantina si cumparaturi")
        self.assertIn("80%", expense)

        summary = self.ask("/budget summary")
        self.assertIn("Venituri", summary)
        self.assertIn("3000.00", summary)
        self.assertIn("Cheltuieli", summary)
        self.assertIn("2500.00", summary)
        budget_tab = self.ask("🧾 Budget Summary")
        self.assertIn("Sold", budget_tab)
        self.assertIn("500.00", budget_tab)

        self.assertIn("Introduceti tipul sfatului", self.ask("💡 Tips"))
        self.assertIn("Bani:", self.ask("money"))
        self.assertIn("Invatare:", self.ask("📚 Study Tip"))
        tip = self.ask("/sfat money")
        self.assertIn("Bani:", tip)
        self.assertIn("Bani:", self.ask("💸 Money Tip"))
        self.assertIn("Wellness:", self.ask("🧘 Wellness Tip"))

    def test_notes_study_plan_and_grade_calculator(self) -> None:
        self.assertIn("Introduceti titlul notitei", self.ask("➕ Add Note"))
        self.assertIn("Introduceti textul notitei", self.ask("Algebra"))
        self.assertIn("Introduceti tagul", self.ask("Recapitulat matrice si determinant"))
        note = self.ask("matematica")
        self.assertIn("Notita salvata", note)
        self.assertIn("Algebra", self.ask("📝 Notes"))
        self.assertIn("Algebra", self.ask("/search matrice"))

        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        self.assertIn("Task adaugat", self.ask(f"/addtask Laborator Python | {tomorrow} | high"))
        plan = self.ask("🧭 Study Plan")
        self.assertIn("Plan de studiu", plan)
        self.assertIn("Laborator Python", plan)

        self.assertIn("Introduceti nota curenta", self.ask("🎯 Grade Calc"))
        self.assertIn("Introduceti media dorita", self.ask("7.50"))
        self.assertIn("Introduceti ponderea", self.ask("8.50"))
        grade = self.ask("40")
        self.assertIn("Calculator nota", grade)
        self.assertIn("Nota necesara", grade)

    def test_budget_analytics_and_smart_study_planner(self) -> None:
        self.assertIn("Limita salvata", self.ask("/budgetlimit mancare | 900"))
        self.assertIn("Recurenta salvata", self.ask("/recurringexpense 250 | transport | abonament lunar | 20"))
        self.assertIn("Tranzactie salvata", self.ask("/budget income | 3000 | bursa | bursa lunara"))
        self.assertIn("Tranzactie salvata", self.ask("/budget expense | 700 | mancare | mese la cantina"))

        limits = self.ask("/budgetlimits")
        self.assertIn("mancare", limits)
        self.assertIn("700.00", limits)
        self.assertIn("900.00", limits)

        forecast = self.ask("/budget forecast")
        self.assertIn("Predictie buget", forecast)
        self.assertIn("Sold estimat", forecast)

        report = self.ask("📊 Raport Buget")
        self.assertIn("Raport buget", report)
        self.assertIn("mancare", report)
        self.assertIn("transport", report)

        weekdays = ["Luni", "Marti", "Miercuri", "Joi", "Vineri", "Sambata", "Duminica"]
        today_weekday = weekdays[date.today().weekday()]
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        self.assertIn("Eveniment adaugat", self.ask(f"/addschedule {today_weekday} | 09:00 | Programare | A-101"))
        self.assertIn("Task adaugat", self.ask(f"/addtask Proiect AI | {tomorrow} | high"))

        plan = self.ask("/studyplan")
        self.assertIn("Plan de studiu", plan)
        self.assertIn("Proiect AI", plan)
        self.assertIn("Conflicte evitate", plan)
        self.assertIn("Programare", plan)


if __name__ == "__main__":
    unittest.main()
