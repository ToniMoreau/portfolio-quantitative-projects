from datetime import date


def add_months(d : date, p : int):
    total_months = d.year * 12 + (d.month - 1) + p
    year = total_months // 12
    month = total_months % 12 + 1
    return date(year, month, 1)

def month_range(start: date, end: date):
    """Génère une liste de dates mensuelles entre start et end inclus."""
    current = start
    while current <= end:
        yield current
        current = add_months(current, 1)