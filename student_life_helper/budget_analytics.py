from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date
from typing import Any

from .models import BudgetCategoryLimit, BudgetTransaction, RecurringExpense, TransactionType


class BudgetAnalyticsService:
    """Calculates monthly budget reports without touching persistence."""

    def build_report(
        self,
        transactions: list[BudgetTransaction],
        limits: list[BudgetCategoryLimit],
        recurring_expenses: list[RecurringExpense],
        today: date | None = None,
    ) -> dict[str, Any]:
        current_day = today or date.today()
        month_transactions = [
            item
            for item in transactions
            if item.created_at.year == current_day.year
            and item.created_at.month == current_day.month
        ]
        income = sum(item.amount for item in month_transactions if item.kind == TransactionType.INCOME)
        expenses = sum(item.amount for item in month_transactions if item.kind == TransactionType.EXPENSE)
        by_category = self._expense_totals_by_category(month_transactions)
        recurring_active = [item for item in recurring_expenses if item.active]
        recurring_remaining = sum(
            item.amount for item in recurring_active if self._is_due_later_this_month(item, current_day)
        )
        recurring_monthly_total = sum(item.amount for item in recurring_active)
        projected_expenses = expenses + recurring_remaining
        projected_balance = income - projected_expenses
        remaining_days = self._remaining_days(current_day)

        limit_statuses = [
            {
                "category": limit.category,
                "limit": limit.monthly_limit,
                "spent": by_category.get(limit.category.lower(), 0.0),
                "remaining": limit.monthly_limit - by_category.get(limit.category.lower(), 0.0),
                "percent": self._percent(by_category.get(limit.category.lower(), 0.0), limit.monthly_limit),
            }
            for limit in sorted(limits, key=lambda item: item.category)
        ]

        return {
            "month": current_day.strftime("%Y-%m"),
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "by_category": dict(sorted(by_category.items())),
            "limits": limit_statuses,
            "recurring": sorted(recurring_active, key=lambda item: (item.day_of_month, item.category)),
            "recurring_remaining": recurring_remaining,
            "recurring_monthly_total": recurring_monthly_total,
            "projected_expenses": projected_expenses,
            "projected_balance": projected_balance,
            "remaining_days": remaining_days,
            "safe_daily_budget": projected_balance / remaining_days if remaining_days else projected_balance,
            "alerts": self._alerts(income, expenses, projected_balance, limit_statuses),
        }

    def _expense_totals_by_category(self, transactions: list[BudgetTransaction]) -> dict[str, float]:
        totals: dict[str, float] = defaultdict(float)
        for item in transactions:
            if item.kind == TransactionType.EXPENSE:
                totals[item.category.lower()] += item.amount
        return totals

    def _is_due_later_this_month(self, expense: RecurringExpense, today: date) -> bool:
        last_day = calendar.monthrange(today.year, today.month)[1]
        due_day = min(expense.day_of_month, last_day)
        return due_day >= today.day

    def _remaining_days(self, today: date) -> int:
        last_day = calendar.monthrange(today.year, today.month)[1]
        return max(last_day - today.day + 1, 1)

    def _percent(self, spent: float, limit: float) -> float:
        if limit <= 0:
            return 0.0
        return spent / limit * 100

    def _alerts(
        self,
        income: float,
        expenses: float,
        projected_balance: float,
        limits: list[dict[str, float | str]],
    ) -> list[str]:
        alerts: list[str] = []
        if income == 0 and expenses > 0:
            alerts.append("Ai cheltuieli in luna curenta, dar niciun venit introdus.")
        if income > 0 and expenses >= income * 0.8:
            alerts.append("Ai folosit peste 80% din veniturile lunii.")
        if projected_balance < 0:
            alerts.append("Predictia pana la final de luna este negativa.")
        for item in limits:
            percent = float(item["percent"])
            category = str(item["category"])
            if percent >= 100:
                alerts.append(f"Categoria {category} a depasit limita lunara.")
            elif percent >= 80:
                alerts.append(f"Categoria {category} a trecut de 80% din limita lunara.")
        return alerts
