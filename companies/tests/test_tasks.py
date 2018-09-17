from django.test import TestCase
from companies.tasks import get_data_from_page_content


class GetReportDataTestCase(TestCase):

    expected_keys = (
        "net_income_loss",
        "shares",
        "revenue",
        "cost_of_revenue",
        "convertible_notes",
        "total_stockholders_equity",
    )

    def test_get_data_from_report_1(self):
        with open("fixtures/twtr-10q_20180331.htm") as f:
            data = get_data_from_page_content(f.read())
        for key in self.expected_keys:
            self.assertIn(key, data)

    def test_get_data_from_report_2(self):
        with open("fixtures/twtr-10q_20140630.htm") as f:
            data = get_data_from_page_content(f.read())
        for key in self.expected_keys:
            self.assertIn(key, data)

    def test_get_data_from_report_3(self):
        with open("fixtures/twtr-10q_20140331.htm") as f:
            data = get_data_from_page_content(f.read())
        for key in self.expected_keys:
            self.assertIn(key, data)

    def test_get_data_from_report_4(self):
        with open("fixtures/twtr-10k_20131231.htm") as f:
            data = get_data_from_page_content(f.read())
        for key in self.expected_keys:
            self.assertIn(key, data)

    def test_get_data_from_report_5(self):
        with open("fixtures/goog10-qq22018.htm") as f:
            data = get_data_from_page_content(f.read())
        for key in self.expected_keys:
            self.assertIn(key, data)

    def test_get_data_from_report_6(self):
        with open("fixtures/goog10-kq42017.htm") as f:
            data = get_data_from_page_content(f.read())
        for key in self.expected_keys:
            self.assertIn(key, data)

    def test_get_data_from_report_7(self):
        with open("fixtures/d133613d10ka.htm") as f:
            data = get_data_from_page_content(f.read())
        self.assertEqual(data, {'shares': 0, 'convertible_notes': 0})
