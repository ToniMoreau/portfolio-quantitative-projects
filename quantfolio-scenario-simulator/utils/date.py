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
        
def month_count(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + (end.month - start.month) + 1

def month_to_date(month : int):
    year = month // 12
    month =round(((month /12) - year) * 12,0)
    month = 12 if month == 0 else month
    return date(year, int(month),1)
    
def get_date_tuple_from_month(month : int):
    year = month // 12
    month =round(((month /12) - year) * 12,0)
    month = 12 if month == 0 else month

    return year, int(month)


print(get_date_tuple_from_month(24323))