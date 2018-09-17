from django.db import models
from django.db.models.signals import post_save
from .tasks import load_sec_reports_data


class Company(models.Model):
    cik = models.CharField(max_length=16, primary_key=True)
    symbol = models.CharField(max_length=16, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    def __str__(self):
        return "[{} {} {}]".format(self.cik, self.symbol, self.name)

    class Meta:
        verbose_name_plural = "companies"


def on_save_company(sender, instance, created, **kwargs):
    if created:
        load_sec_reports_data.delay(instance.cik)


post_save.connect(on_save_company, sender=Company)


class Report(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="reports")
    date = models.DateField()

    shares = models.IntegerField()

    revenue = models.IntegerField()
    cost_of_revenue = models.IntegerField()
    net_income = models.IntegerField()

    convertible_notes = models.IntegerField()
    equity = models.IntegerField()

    class Meta:
        unique_together = (("date", "company"),)
        ordering = ('date', 'company')

    def __str__(self):
        return "R{}: {} ({}, {}, {}) ({} {})".format(
            self.date, self.shares,
            self.revenue, self.cost_of_revenue, self.net_income,
            self.convertible_notes, self.equity
        )
