from methods import *
from unittest import TestCase

class MethodsTest(TestCase):
    def test_get_categories(self):
        cat_list=get_categories()
        self.assertIn((None,None), cat_list)

    def test_get_date_time(self):
        date_time=get_date_time("2005-03-01 19:00:00")
        self.assertEqual(date_time, "2005-03-01 07:00 PM")

    def test_image_error(self):
        url=image_error("anything silly")
        self.assertEqual(url, "/static/img/card-crop.jpg")
    
    def test_sort_events_by_date(self):
        dates=[{"start_time": "2002-03-01 19:00:00", "start_time": "2003-03-01 19:00:00", "start_time": "2001-03-01 19:00:00", "start_time": "2008-03-01 19:00:00"}]
        sorted=sort_events_by_date(dates)
        self.assertEqual(sorted[0]['start_time'], "2008-03-01 19:00:00" )