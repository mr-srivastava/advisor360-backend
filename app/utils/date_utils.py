import calendar


def parse_financial_year(date_obj):
    year = date_obj.year
    if date_obj.month >= 4:  # April or later → current year to next year
        return f"FY{str(year)[-2:]}-{str(year + 1)[-2:]}"
    else:  # Jan–Mar → previous year to current year
        return f"FY{str(year - 1)[-2:]}-{str(year)[-2:]}"


def format_month_year(month, year):
    # If month is already an integer
    if isinstance(month, int):
        month_name = calendar.month_name[month]

    # If month is a string number like "03" or "3"
    elif month.isdigit():
        month_int = int(month)
        month_name = calendar.month_name[month_int]

    # If month is already a full month name like "March"
    else:
        # Normalize capitalization just in case
        month_name = month.capitalize()

    return f"{month_name} {year}"
