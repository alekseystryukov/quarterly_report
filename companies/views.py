from django.shortcuts import render, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from companies.models import Company
import json


def index(request):
    context = {
        "companies": None,
        "search": request.GET.get('search', '')
    }
    if context["search"]:
        context["companies"] = Company.objects.filter(
            Q(cik__icontains=context["search"]) |
            Q(symbol__icontains=context["search"]) |
            Q(name__icontains=context["search"])
        )

    return render(request, 'index.html', context)


def detail(request, cik):
    company = get_object_or_404(Company, cik=cik)

    data = json.dumps(
        list(
            company.reports.all().values(
                "date", "shares", "revenue", "cost_of_revenue",
                "net_income", "convertible_notes", "equity"
            )
        ),
        cls=DjangoJSONEncoder
    )

    return render(request, 'detail.html', {'company': company, 'chart_data': data})
