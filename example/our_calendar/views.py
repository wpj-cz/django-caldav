# coding=utf-8
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseBadRequest
from django_caldav.views import CalDavView, CalDavFeedView
from example.our_calendar.models import OurCalendarEvent


class OurCalendarFeedView(CalDavFeedView):
    product_id = '-//example.com//Example//EN'
    timezone = 'UTC'
    now = datetime.now()
    min_date = now + timedelta(days=-7)
    max_date = now + timedelta(days=14)

    def items(self):
        return OurCalendarEvent.objects. \
            filter(start_datetime__gte=OurCalendarFeedView.min_date). \
            filter(start_datetime__lte=OurCalendarFeedView.max_date). \
            order_by('-start_datetime')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_start_datetime(self, item):
        return item.start_datetime

    def item_end_datetime(self, item):
        return item.end_datetime

    def item_location(self, item):
        return item.location

    def item_link(self, item):
        return "/{pk}.ics".format(pk=item.pk)

    @staticmethod
    def item_save(base_item, iCalendar_component):
        try:
            item = None
            if base_item.uid:
                try:
                    item = OurCalendarEvent.objects.get(pk=base_item.uid)
                except Exception as e:
                    print(str(e))
            if not item:
                item = OurCalendarEvent()
            item.title = base_item.title
            item.start_datetime = base_item.start_datetime
            item.end_datetime = base_item.end_datetime
            item.location = base_item.location
            item.description = base_item.description
            item.save()

            return HttpResponse(status=201)
        except Exception as e:
            return HttpResponseBadRequest(content=str(e))


class OurCalendarView(CalDavView):
    """
    A simple event calender
    """
    feed_view = OurCalendarFeedView