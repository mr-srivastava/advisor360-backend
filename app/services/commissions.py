from app.db.supabase import get_supabase
from app.services.partners import get_entities
from app.utils.date_utils import parse_financial_year
from app.models.commissions import Commission
from datetime import datetime
from typing import List
from app.utils.date_utils import format_month_year


def get_transactions():
    supabase = get_supabase()
    data = supabase.table("entity_transactions").select("*").order('month', desc=True).execute()
    return data.data


def get_total_commissions() -> float:
    supabase = get_supabase()
    response = supabase.rpc("get_total_commissions").execute()
    return response.data


def get_total_commissions_by_month(month: str, year: int) -> float:
    supabase = get_supabase()
    month_num = datetime.strptime(month, "%B").month
    response = supabase.rpc(
        "get_total_commissions_by_month", {"y": year, "m": month_num}
    ).execute()
    return response.data or 0.0


def get_total_commissions_by_fy(financial_year: str) -> float:
    supabase = get_supabase()
    response = supabase.rpc(
        "get_total_commissions_by_fy", {"fy": financial_year}
    ).execute()
    return response.data or 0.0


def get_commissions() -> List[Commission]:
    transactions = get_transactions()
    entities = get_entities()
    entity_lookup = {entity["id"]: entity for entity in entities}

    commissions: List[Commission] = []

    for txn in transactions:
        txn_month = datetime.fromisoformat(txn["month"])
        year = txn_month.year
        month_name = txn_month.strftime("%B")
        financial_year = parse_financial_year(txn_month)

        commissions.append(
            Commission(
                id=str(txn["id"]),
                partnerId=str(txn["entity_id"]),
                amount=float(txn["amount"]),
                month=month_name,
                year=str(year),
                financialYear=financial_year,
                date=txn_month.date(),
                createdAt=datetime.fromisoformat(txn["created_at"]),
            )
        )

    commissions.sort(key=lambda x: x.date, reverse=True)

    return commissions

def get_commissions_with_partner() -> List[dict]:
    commissions = get_commissions()
    entities = get_entities()
    entity_lookup = {entity["id"]: entity for entity in entities}

    result = []
    for commission in commissions:
        commission_dict = commission.model_dump()
        commission_dict["partner"] = entity_lookup.get(commission.partnerId)
        result.append(commission_dict)

    return result

def get_monthly_commissions():
    # Fetch commissions from Supabase
    commissions = get_commissions()
    monthly_data = {}

    # Aggregate like your TS logic
    for commission in commissions:
        month = commission.month
        year = commission.year
        key = format_month_year(month, year)

        if key not in monthly_data:
            monthly_data[key] = {"month": key, "total": 0, "count": 0}

        monthly_data[key]["total"] += commission.amount
        monthly_data[key]["count"] += 1

    # Convert to list + sort
    monthly_data_list = list(monthly_data.values())
    monthly_data_list.sort(
        key=lambda x: datetime.strptime(x["month"], "%B %Y")
    )

    # Return last 6 months
    return monthly_data_list[-6:]