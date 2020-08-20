import requests
from secrets import event_key, event_url
from datetime import datetime
from models import User


def get_categories():
    """returns a list of categories for event search"""
    r = requests.post(
        f"{event_url}categories/list", data={"app_key": event_key})
    categories = r.json()['category']
    choices = [(category['id'], category['id']) for category in categories]
    choices.append((None, None))
    return choices


def get_search_params(obj):
    """returns an object of search parameters used in a search"""

    params = {}
    for val in obj:
        if obj[val]:
            params[val] = obj[val]
    params.pop('app_key')
    params.pop('page_number')
    params.pop('page_size')
    return params


def get_date_time(json_date):
    """reformats date received from eventful api"""
    date_time = datetime.strptime(json_date, '%Y-%m-%d %H:%M:%S')
    date = datetime.date(date_time)
    time = datetime.time(date_time).strftime('%I:%M %p')
    return f"{date} {time}"


def image_error(obj):
    """inserts a default image if no image is found in api response"""
    try:
        return obj['images']['image'][0]['medium']['url']
    except:
        return "/static/img/card-crop.jpg"


def get_saved(id):
    """returns ids of user-saved events"""
    u = User.query.get(id)
    return [event.id for event in u.events]


def sort_events_by_date(list):
    """sorts a list of events by date-time"""
    sortedList = sorted(
        list,
        key=lambda x: datetime.strptime(x['start_time'], '%Y-%m-%d %H:%M:%S')
    )
    return sortedList


def get_saved_events(id):
    """returns a list of user-saved events"""
    u = User.query.get(id)
    e_ids = [event.id for event in u.events]
    events = []
    for e_id in e_ids:
        e = requests.post(f"{event_url}events/get",
                          data={"app_key": event_key, "id": e_id})
        events.append(e.json())
    sorted_events = sort_events_by_date(events)
    return sorted_events
