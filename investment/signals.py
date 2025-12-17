# investment/signals.py    
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal, getcontext
from .models import Investment
from finance.models import Expense, Income
from .utils import calculate_compound_value

getcontext().prec = 28


def choose_income_category(inv_type):
    t = (inv_type or "").lower()
    if t in ["fd", "fixed deposit", "rd", "recurring deposit", "bond"]:
        return "Interest Income"
    if t in ["stock", "mutual fund", "etf", "crypto", "share"]:
        return "Dividends"
    if t in ["real estate", "pension"]:
        return "Rental Income"
    if t in ["gold"]:
        return "Other Income"
    return "Other Income"


def _to_decimal(value):
    if value is None:
        return Decimal('0')
    return value if isinstance(value, Decimal) else Decimal(str(value))


@receiver(pre_save, sender=Investment)
def track_old_name(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Investment.objects.get(pk=instance.pk)
            instance._old_name = old.name
        except Investment.DoesNotExist:
            instance._old_name = None
    else:
        instance._old_name = None


@receiver(post_save, sender=Investment)
def sync_investment_records(sender, instance, created, **kwargs):
    old_name = getattr(instance, "_old_name", None)
    name_changed = old_name and old_name != instance.name

    expense_name = f"Investment in {instance.name}"

    expense, _ = Expense.objects.get_or_create(
        user=instance.user,
        investment=instance,
        defaults={
            "name": expense_name,
            "amount": instance.amount,
            "date": instance.start_date or timezone.now().date(),
            "category": "Financial",
        },
    )

    updated_fields = []
    expected_date = instance.start_date or timezone.now().date()

    if _to_decimal(expense.amount) != _to_decimal(instance.amount):
        expense.amount = instance.amount
        updated_fields.append("amount")

    if expense.date != expected_date:
        expense.date = expected_date
        updated_fields.append("date")

    if name_changed:
        expense.name = expense_name
        updated_fields.append("name")

    if updated_fields:
        expense.save(update_fields=updated_fields)

    income_name = f"Investment Maturity - {instance.name}"
    income = Income.objects.filter(user=instance.user, investment=instance).first()

    if instance.status == "Completed" and instance.end_date:

        est_value = calculate_compound_value(
            principal=instance.amount,
            annual_rate=instance.expected_return,
            start=instance.start_date,
            end=instance.end_date,
            investment_type=instance.investment_type,
            frequency=instance.frequency,
        )

        category = choose_income_category(instance.investment_type)

        if income:
            income.amount = est_value
            income.date = instance.end_date
            income.source = income_name
            income.save(update_fields=["amount", "date", "source"])
        else:
            Income.objects.create(
                user=instance.user,
                investment=instance,
                source=income_name,
                amount=est_value,
                date=instance.end_date,
                category=category,
            )

    elif income and instance.status != "Completed":
        income.delete()


@receiver(post_delete, sender=Investment)
def delete_linked_records(sender, instance, **kwargs):
    Expense.objects.filter(investment=instance).delete()
    Income.objects.filter(investment=instance).delete()
