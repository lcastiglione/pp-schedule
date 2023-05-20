import unittest
import pytz
from schedule.schedule import (add_time, get_business_days_between, timeit, get_time, today, date_to_int, int_to_date, get_min_between_times,
                               is_bussines_day, get_seconds_by_time, convert_string_to_date, get_last_business_day, get_prev_business_day, get_next_business_day, up_date)
from datetime import datetime, date, time, timedelta


class TestDatetimeFuncs(unittest.TestCase):

    def test_timeit(self):
        @timeit(file=None)
        def test_func():
            return "test"

        self.assertEqual(test_func(), "test")

    def test_get_time(self):
        self.assertEqual(get_time(500), "500nS")
        self.assertEqual(get_time(1500), "1.5uS")
        self.assertEqual(get_time(1500000), "1.5mS")
        self.assertEqual(get_time(1500000000), "1.5S")
        self.assertEqual(get_time(3600000000000), "60.0min")

    def test_today(self):
        tz = pytz.timezone('America/Argentina/Buenos_Aires')
        self.assertEqual(today(), datetime.now(tz=tz))
        self.assertEqual(today(tz=None), datetime.now())

    def test_is_bussines_day(self):
        self.assertTrue(is_bussines_day(datetime(2023, 5, 19)))
        self.assertFalse(is_bussines_day(datetime(2023, 5, 20)))
        self.assertFalse(is_bussines_day(datetime(2023, 5, 19),
                                         holidays={2023: [date(2023, 5, 19)]}))

    def test_date_to_int(self):
        self.assertIsInstance(date_to_int('2023-05-19'), int)
        self.assertIsInstance(date_to_int(datetime.now()), int)
        self.assertEqual(date_to_int(datetime(2023, 5, 19)), 1684465200000)
        self.assertEqual(date_to_int("2023-05-19"), 1684465200000)

    def test_int_to_date(self):
        self.assertEqual(int_to_date(1684465200000), datetime(2023, 5, 19))

    def test_get_seconds_by_time(self):
        self.assertEqual(get_seconds_by_time(
            datetime(2023, 5, 19, 12, 30, 45)), 45045)

    def test_convert_string_to_date(self):
        self.assertEqual(convert_string_to_date(
            "2023-05-19 12:30:45"), datetime(2023, 5, 19, 12, 30, 45))
        self.assertEqual(convert_string_to_date(
            "2023-05-19"), datetime(2023, 5, 19))
        self.assertEqual(convert_string_to_date(
            ["2023-05-19", "2023-05-20"]), [datetime(2023, 5, 19), datetime(2023, 5, 20)])

    def test_get_last_business_day(self):
        # Si es fin de semana, es necesario obtener la fecha del viernes y no la del día de hoy
        today = datetime.now()
        day = today.weekday()
        days_susbtract = (day + 3) - 7
        friday = today - timedelta(days=days_susbtract)
        self.assertEqual(get_last_business_day(), datetime.combine(
            date.today() if day < 5 else friday, datetime.min.time()))

    def test_get_prev_business_day(self):
        self.assertEqual(get_prev_business_day(
            datetime(2023, 5, 20)), datetime(2023, 5, 19))
        self.assertEqual(get_prev_business_day(
            datetime(2023, 5, 20), keep=True), datetime(2023, 5, 19))
        self.assertEqual(get_prev_business_day(
            datetime(2023, 5, 19)), datetime(2023, 5, 18))
        self.assertEqual(get_prev_business_day(
            datetime(2023, 5, 19), keep=True), datetime(2023, 5, 19))

    def test_get_next_business_day(self):
        self.assertEqual(get_next_business_day(
            datetime(2023, 5, 20)), datetime(2023, 5, 22))
        self.assertEqual(get_next_business_day(
            datetime(2023, 5, 20), keep=True), datetime(2023, 5, 22))
        self.assertEqual(get_next_business_day(
            datetime(2023, 5, 19)), datetime(2023, 5, 22))
        self.assertEqual(get_next_business_day(
            datetime(2023, 5, 19), keep=True), datetime(2023, 5, 19))

    def test_get_business_days_between(self):
        start = datetime(2023, 1, 1)
        end = datetime(2023, 1, 7)
        result = get_business_days_between(start, end)
        expected = [datetime(2023, 1, 2), datetime(2023, 1, 3), datetime(
            2023, 1, 4), datetime(2023, 1, 5), datetime(2023, 1, 6)]
        self.assertEqual(result, expected)

    def test_up_date(self):
        ref = datetime(2023, 1, 1)
        result = up_date(ref, days=1, months=1, years=1)
        expected = datetime(2024, 2, 2)
        self.assertEqual(result, expected)

    def test_add_time(self):
        ref = time(12, 0, 0)
        result = add_time(ref, hours=1, minutes=1, seconds=1)
        expected = time(13, 1, 1)
        self.assertEqual(result, expected)

    def test_get_min_between_times(self):
        start = time(hour=12, minute=0, second=0)
        end = time(hour=13, minute=0, second=0)
        self.assertEqual(get_min_between_times(start, end), 12.0)
