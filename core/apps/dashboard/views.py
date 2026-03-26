import calendar
from datetime import timedelta

from django.db import models
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.apps.billing.models import BillingItem
from core.apps.dashboard.serializers import DashboardStatsSerializer
from core.apps.inventory.models import Productstock


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics filtered by current tenant"""

    # Get current tenant - first try from middleware, then from user
    tenant = getattr(request, "tenant", None)

    # If no tenant from middleware, try to get from authenticated user
    if not tenant and request.user and request.user.is_authenticated:
        tenant = getattr(request.user, "tenant", None)

    # If still no tenant, return empty stats
    if not tenant:
        empty_data = {
            "total_sales": 0,
            "total_profit": 0,
            "total_stocks": 0,
            "products": [],
            "profit_daily": 0,
            "profit_weekly": 0,
            "profit_monthly": 0,
            "profit_yearly": 0,
            "weekly_profit_by_day": [],
            "monthly_profit_by_date": [],
            "yearly_profit_by_month": [],
            "sales_daily": 0,
            "sales_weekly": 0,
            "sales_monthly": 0,
            "sales_yearly": 0,
            "weekly_sales_by_day": [],
            "monthly_sales_by_date": [],
            "yearly_sales_by_month": [],
            "week_top_product": None,
            "month_top_product": None,
            "year_top_product": None,
        }
        serializer = DashboardStatsSerializer(empty_data)
        return Response(serializer.data)

    # Filter all queries by tenant
    products_qs = Productstock.objects.filter(tenant=tenant, is_deleted=False)

    # Total Sales: sum of all billing items' unit_total
    total_sales = (
        BillingItem.objects.filter(bill_id__tenant=tenant).aggregate(
            total_sales_sum=models.Sum("unit_total")
        )["total_sales_sum"]
        or 0
    )

    # Total Profit: sum of (unit_price - cost_price) * quantity for all billing items
    total_profit = (
        BillingItem.objects.filter(bill_id__tenant=tenant)
        .select_related("product_id")
        .annotate(
            profit_per_item=models.F("unit_price") - models.F("product_id__cost_price"),
            total_profit=models.ExpressionWrapper(
                (models.F("unit_price") - models.F("product_id__cost_price"))
                * models.F("quantity"),
                output_field=models.DecimalField(),
            ),
        )
        .aggregate(total_profit_sum=models.Sum("total_profit"))["total_profit_sum"]
        or 0
    )

    # Profit by period
    now = timezone.now().date()
    # Daily
    daily_profit = (
        BillingItem.objects.filter(bill_id__tenant=tenant, bill_id__date=now)
        .select_related("product_id")
        .annotate(
            total_profit=models.ExpressionWrapper(
                (models.F("unit_price") - models.F("product_id__cost_price"))
                * models.F("quantity"),
                output_field=models.DecimalField(),
            )
        )
        .aggregate(profit=models.Sum("total_profit"))["profit"]
        or 0
    )

    # Weekly (current week: Monday to Sunday)
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)
    weekly_profit = (
        BillingItem.objects.filter(
            bill_id__tenant=tenant, bill_id__date__range=[week_start, week_end]
        )
        .select_related("product_id")
        .annotate(
            total_profit=models.ExpressionWrapper(
                (models.F("unit_price") - models.F("product_id__cost_price"))
                * models.F("quantity"),
                output_field=models.DecimalField(),
            )
        )
        .aggregate(profit=models.Sum("total_profit"))["profit"]
        or 0
    )

    # Weekly breakdown by day with weekday name and formatted profit
    weekly_profit_by_day = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_profit = (
            BillingItem.objects.filter(bill_id__tenant=tenant, bill_id__date=day)
            .select_related("product_id")
            .annotate(
                total_profit=models.ExpressionWrapper(
                    (models.F("unit_price") - models.F("product_id__cost_price"))
                    * models.F("quantity"),
                    output_field=models.DecimalField(),
                )
            )
            .aggregate(profit=models.Sum("total_profit"))["profit"]
            or 0
        )
        profit_str = f"{day_profit:.2f}"
        weekly_profit_by_day.append(
            {
                "date": day.isoformat(),
                "weekday": day.strftime("%A"),
                "profit": profit_str,
            }
        )

    # Monthly (current month)
    monthly_profit = (
        BillingItem.objects.filter(
            bill_id__tenant=tenant,
            bill_id__date__year=now.year,
            bill_id__date__month=now.month,
        )
        .select_related("product_id")
        .annotate(
            total_profit=models.ExpressionWrapper(
                (models.F("unit_price") - models.F("product_id__cost_price"))
                * models.F("quantity"),
                output_field=models.DecimalField(),
            )
        )
        .aggregate(profit=models.Sum("total_profit"))["profit"]
        or 0
    )

    # Yearly (current year)
    yearly_profit = (
        BillingItem.objects.filter(bill_id__tenant=tenant, bill_id__date__year=now.year)
        .select_related("product_id")
        .annotate(
            total_profit=models.ExpressionWrapper(
                (models.F("unit_price") - models.F("product_id__cost_price"))
                * models.F("quantity"),
                output_field=models.DecimalField(),
            )
        )
        .aggregate(profit=models.Sum("total_profit"))["profit"]
        or 0
    )

    # Yearly breakdown by month
    yearly_profit_by_month = []
    for month_num in range(1, 13):
        month_profit = (
            BillingItem.objects.filter(
                bill_id__tenant=tenant,
                bill_id__date__year=now.year,
                bill_id__date__month=month_num,
            )
            .select_related("product_id")
            .annotate(
                total_profit=models.ExpressionWrapper(
                    (models.F("unit_price") - models.F("product_id__cost_price"))
                    * models.F("quantity"),
                    output_field=models.DecimalField(),
                )
            )
            .aggregate(profit=models.Sum("total_profit"))["profit"]
            or 0
        )
        profit_str = f"{month_profit:.2f}"
        yearly_profit_by_month.append(
            {"month": calendar.month_name[month_num], "profit": profit_str}
        )

    # Total Sales breakdowns
    # Daily
    daily_sales = (
        BillingItem.objects.filter(bill_id__tenant=tenant, bill_id__date=now).aggregate(
            sales=models.Sum("unit_total")
        )["sales"]
        or 0
    )

    # Weekly (current week: Monday to Sunday)
    weekly_sales = (
        BillingItem.objects.filter(
            bill_id__tenant=tenant, bill_id__date__range=[week_start, week_end]
        ).aggregate(sales=models.Sum("unit_total"))["sales"]
        or 0
    )

    # Weekly breakdown by day
    weekly_sales_by_day = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_sales = (
            BillingItem.objects.filter(
                bill_id__tenant=tenant, bill_id__date=day
            ).aggregate(sales=models.Sum("unit_total"))["sales"]
            or 0
        )
        sales_str = f"{day_sales:.2f}"
        weekly_sales_by_day.append(
            {"date": day.isoformat(), "weekday": day.strftime("%A"), "sales": sales_str}
        )

    # Monthly (current month)
    monthly_sales = (
        BillingItem.objects.filter(
            bill_id__tenant=tenant,
            bill_id__date__year=now.year,
            bill_id__date__month=now.month,
        ).aggregate(sales=models.Sum("unit_total"))["sales"]
        or 0
    )

    # Yearly (current year)
    yearly_sales = (
        BillingItem.objects.filter(
            bill_id__tenant=tenant, bill_id__date__year=now.year
        ).aggregate(sales=models.Sum("unit_total"))["sales"]
        or 0
    )

    # Yearly breakdown by month
    yearly_sales_by_month = []
    for month_num in range(1, 13):
        month_sales = (
            BillingItem.objects.filter(
                bill_id__tenant=tenant,
                bill_id__date__year=now.year,
                bill_id__date__month=month_num,
            ).aggregate(sales=models.Sum("unit_total"))["sales"]
            or 0
        )
        sales_str = f"{month_sales:.2f}"
        yearly_sales_by_month.append(
            {"month": calendar.month_name[month_num], "sales": sales_str}
        )

    # Total Product Stocks: sum of all Productstock's stock (excluding deleted)
    total_stocks = (
        products_qs.aggregate(total_stock=models.Sum("stock"))["total_stock"] or 0
    )

    # Product names and stocks (excluding deleted)
    products = products_qs.values("id", "name", "stock")
    product_ids = [p["id"] for p in products]

    # Calculate total sold quantity per product
    sold_qty_map = {
        item["product_id"]: item["total_sold"]
        for item in BillingItem.objects.filter(
            bill_id__tenant=tenant, product_id__in=product_ids
        )
        .values("product_id")
        .annotate(total_sold=models.Sum("quantity"))
    }

    product_list = [
        {
            "product_name": p["name"],
            "stock": p["stock"],
            "sold": sold_qty_map.get(p["id"], 0),
        }
        for p in products
    ]

    # Top-selling product for the week
    week_top = (
        BillingItem.objects.filter(
            bill_id__tenant=tenant, bill_id__date__range=[week_start, week_end]
        )
        .values("product_id")
        .annotate(total_sold=models.Sum("quantity"))
        .order_by("-total_sold")
        .first()
    )
    week_top_product = None
    if week_top:
        product = products_qs.filter(id=week_top["product_id"]).first()
        if product:
            week_top_product = {
                "product_name": product.name,
                "sold_quantity": week_top["total_sold"],
                "stock": product.stock,
            }

    # Top-selling product for the month
    month_top = (
        BillingItem.objects.filter(
            bill_id__tenant=tenant,
            bill_id__date__year=now.year,
            bill_id__date__month=now.month,
        )
        .values("product_id")
        .annotate(total_sold=models.Sum("quantity"))
        .order_by("-total_sold")
        .first()
    )
    month_top_product = None
    if month_top:
        product = products_qs.filter(id=month_top["product_id"]).first()
        if product:
            month_top_product = {
                "product_name": product.name,
                "sold_quantity": month_top["total_sold"],
                "stock": product.stock,
            }

    # Top-selling product for the year
    year_top = (
        BillingItem.objects.filter(bill_id__tenant=tenant, bill_id__date__year=now.year)
        .values("product_id")
        .annotate(total_sold=models.Sum("quantity"))
        .order_by("-total_sold")
        .first()
    )
    year_top_product = None
    if year_top:
        product = products_qs.filter(id=year_top["product_id"]).first()
        if product:
            year_top_product = {
                "product_name": product.name,
                "sold_quantity": year_top["total_sold"],
                "stock": product.stock,
            }

    data = {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_stocks": total_stocks,
        "products": product_list,
        "profit_daily": daily_profit,
        "profit_weekly": weekly_profit,
        "profit_monthly": monthly_profit,
        "weekly_profit_by_day": weekly_profit_by_day,
        "yearly_profit_by_month": yearly_profit_by_month,
        "profit_yearly": yearly_profit,
        "sales_daily": daily_sales,
        "sales_weekly": weekly_sales,
        "sales_monthly": monthly_sales,
        "sales_yearly": yearly_sales,
        "weekly_sales_by_day": weekly_sales_by_day,
        "yearly_sales_by_month": yearly_sales_by_month,
        "week_top_product": week_top_product,
        "month_top_product": month_top_product,
        "year_top_product": year_top_product,
    }
    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data)
