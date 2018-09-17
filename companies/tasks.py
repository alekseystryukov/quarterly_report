from celery import shared_task
from bs4 import BeautifulSoup
from django.db.utils import IntegrityError
from collections import defaultdict
from time import sleep
import requests
import logging
import re


TABLE_NAMES = (
    "CONSOLIDATED_BALANCE_SHEETS",
    ("CONSOLIDATED_STATEMENTS_OF_OPERATIONS", "CONSOLIDATED STATEMENTS OF INCOME"),
    "CONSOLIDATED_STATEMENTS_OF_CASH_FLOWS",
)


logger = logging.getLogger("AsyncTasksLogger")


def get_numeric_value(v):
    return int(float(v.replace(",", "").replace("(", "")))


def format_title(value):
    v = value.replace(" ", "_").replace("-", "_")
    v = re.sub(r"[^\w_]", "", v)
    return v.lower()


def find_table(tree, name, alt_name=None):
    if isinstance(name, tuple):
        name, alt_name = name

    # let's find link, ex: <a name="CONSOLIDATED_BALANCE_SHEETS">
    table_pointer = tree.find("a", {"name": name})
    if table_pointer:
        # next <div> after the link's block contains the table we are looking for
        while table_pointer.name != "p":
            table_pointer = table_pointer.parent

        while table_pointer.name != "div":
            table_pointer = table_pointer.next_sibling

        return table_pointer.table
    else:  # look for <font>CONSOLIDATED BALANCE SHEETS</font>

        title = tree.find(string=name.replace("_", " "))
        if not title and alt_name:
            title = tree.find(string=alt_name.replace("_", " "))

        if title:
            element = title.parent.parent
            while element is not None and element.table is None:
                element = element.next_sibling
            return element.table


def get_data_from_page_content(content, file_link=None):
    data = {"shares": 0}
    soup = BeautifulSoup(content, 'html.parser')

    shares_report = soup.find(
        string=re.compile(r"The number of shares of the registrant’s common stock outstanding"))
    # get 752666518 from "The number of shares of the registrant’s common stock .. was 752,666,518."
    if shares_report:
        match = re.search(r"([\d,]+)\.", shares_report)
        if match:
            data["shares"] = int(match.group(1).replace(",", ""))

    for table_name in TABLE_NAMES:
        table = find_table(soup, table_name)
        if not table:
            logger.error("{} is not found on {}".format(table_name, file_link))
            continue

        prev_title = None
        for el in table:
            if el.name == "tr":
                td_elements = el.find_all("td")
                raw_title = td_elements[0].get_text(strip=True)

                if raw_title:
                    value = None
                    for col in td_elements[1:]:
                        cell_value = col.get_text(strip=True).strip('—')
                        if any(char.isdigit() for char in cell_value):
                            value = cell_value
                            break

                    if value:
                        title = format_title(raw_title)
                        if prev_title and len(title.split("_")) < 2:
                            title = "_".join((prev_title, title))
                        value = get_numeric_value(value)
                        data[title] = value

                    if raw_title.endswith(":"):
                        prev_title = format_title(raw_title)

    if "revenue" not in data and "revenues" in data:
        data["revenue"] = data.pop("revenues")

    if "cost_of_revenue" not in data and "cost_of_revenues" in data:
        data["cost_of_revenue"] = data.pop("cost_of_revenues")

    if "net_income_loss" not in data:
        if "net_loss" in data:
            data["net_income_loss"] = data.pop("net_loss")
        elif "net_income" in data:
            data["net_income_loss"] = data.pop("net_income")

    if "total_stockholders_equity" not in data and "total_stockholders_equity_deficit" in data:
        data["total_stockholders_equity"] = data.pop("total_stockholders_equity_deficit")

    if "convertible_notes" not in data:
        logger.warning('"convertible_notes" line is missed')
        data["convertible_notes"] = 0

    return data


@shared_task
def load_sec_reports_data(cik):
    from companies.models import Company, Report
    company, _ = Company.objects.get_or_create(cik=cik)

    count = 100  # max reports per page option
    sec_host = "https://www.sec.gov"
    min_date = '2000-01-01'

    page_links = []
    page_n = 0
    proceed = True
    while proceed:
        reports_list_url = "{}/cgi-bin/browse-edgar?action=getcompany&CIK={}&owner=include&start={}&count={}".format(
            sec_host, cik,
            page_n * count,  # 0, 100, 200, ..
            count
        )
        page_n += 1
        page = requests.get(reports_list_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        if not company.name:
            name_span = soup.find("span", {"class": "companyName"})
            if name_span:
                name_parts = list(name_span.stripped_strings)
                if name_parts:
                    company.name = name_parts[0]
                    company.save()

        rows = soup.find_all(string=re.compile(r'10-Q|10-K'))
        if len(rows):
            for row in rows:
                first_cell = row.parent
                row_date = first_cell.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.string
                if row_date > min_date:
                    page_links.append(
                        first_cell.next_sibling.next_sibling.a["href"]
                    )
                else:
                    proceed = False
        else:
            proceed = False

    # -------------
    file_links = []

    for page_link in page_links:
        page = requests.get(sec_host + page_link)
        soup = BeautifulSoup(page.content, 'html.parser')

        # two first tables
        detail_table, report_table = soup.find_all(id="formDiv")[:2]

        # get report period
        period = detail_table.find(string="Period of Report").parent.next_sibling.next_sibling.string

        # get report link
        file_row = report_table.find(string=re.compile(r'10-Q|10-K'))
        link = file_row.parent.next_sibling.next_sibling.a["href"]

        file_links.append((period, link))

    if not company.symbol and len(file_links):
        file_name = file_links[0][1].split("/")[-1]
        symbol = file_name.split("-")[0]
        company.symbol = symbol.upper()
        company.save()

    # -----

    for period, file_link in file_links:
        page = requests.get(sec_host + file_link)
        data = get_data_from_page_content(page.content, file_link)

        # prepare report
        try:
            report_data = dict(
                shares=data["shares"],
                revenue=data["revenue"],
                cost_of_revenue=data["cost_of_revenue"],
                net_income=data["net_income_loss"],
                convertible_notes=data["convertible_notes"],
                equity=data["total_stockholders_equity"],
            )
        except KeyError as e:
            logger.error("KeyError {} IN {}".format(e, file_link))
        else:
            # save report
            try:
                Report.objects.create(company=company, date=period,  **report_data)
            except IntegrityError as e:
                logger.error(e)

