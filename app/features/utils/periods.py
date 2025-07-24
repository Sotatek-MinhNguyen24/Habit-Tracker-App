# Xac dinh danh sach ngay/thang can hien thi theo thoi gian hien tai:
from datetime import date, timedelta

YEARS_COUNT = 5

def get_current_period(frequency:str) -> list[date]:
    today = date.today()

    if frequency == "daily":
        start = today - timedelta(days=today.weekday())
        return [start + timedelta(days=i) for i in range(7)]

    if frequency == "monthly":
        return [date(today.year, m, 1) for m in range(1,13)]

    if frequency == "yearly":
        return [date(today.year+i, 1, 1) for i in range(YEARS_COUNT)]

    return []
