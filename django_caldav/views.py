# coding=utf-8
from datetime import datetime
import hashlib
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode
from django.http import HttpRequest
from icalendar import Calendar
from lxml import etree
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from djangodav.responses import HttpResponseMultiStatus
from djangodav.views import DavView
from django_ical.views import ICalFeed
from django_caldav.acl import FullAcl
from django_caldav.lock import DummyLock
from django_caldav.models import CalDavEvent
from django_caldav.resources import CalDavResource
from django_caldav.utils import WebDAV, CalDAV, url_join, CalDAV_MAP, WebDAV_MAP, CalendarServer_MAP, CalendarServer


class CalDavFeedView(ICalFeed):
    @staticmethod
    def one_event_per_calendar(calendar):
        calendar = smart_unicode(calendar)
        events = calendar.split(u"BEGIN:VEVENT")
        header = events[0]
        footer = events[len(events) - 1].split(u"END:VEVENT")[1]
        events.remove(header)
        calendars = []

        for event in events:
            event = event.split(u"END:VEVENT")[0]
            url = event.split(u"URL")[1].split(u"\n")[0]
            calendars.append((
                url,
                u"{header}BEGIN:VEVENT{event}END:VEVENT{footer}".format(
                    header=header,
                    event=event,
                    footer=footer
                )
            ))

        return calendars

    def item_guid(self, item):
        return item.pk

    @staticmethod
    def item_save(base_item, iCalendar_component):
        return HttpResponseForbidden()


class CalDavView(DavView):
    resource_class = CalDavResource
    lock_class = DummyLock
    acl_class = FullAcl
    feed_view = CalDavFeedView

    # TODO mkcalendar, head, get, delete, copy, move
    http_method_names = [
        'options',
        'put',
        'propfind',
        'proppatch',
        'lock',
        'unlock',
        'report'
    ]
    template_name = "django_caldav/index.html"
    xml_pretty_print = True
    request_body = None
    request_body_as_etree = None

    KNOWN_PROPERTIES = [
        "D:resourcetype",
        "D:owner",
        "D:current-user-principal",
        "D:supported-report-set",
        "C:supported-calendar-component-set",
        "D:getetag",
        "CS:getctag",
        "D:getcontenttype",
        "D:displayname",
        "D:principal-collection-set",
        "D:principal-URL",
        "D:resource-id",
        "C:calendar-home-set",
        "C:calendar-user-address-set",
        "CS:email-address-set",
        "CS:dropbox-home-URL",
        "CS:notification-URL",
        "C:schedule-inbox-URL",
        "C:schedule-outbox-URL"
    ]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, path, *args, **kwargs):
        self.request_body = {
            "plain": request.body,
            "xml": self.get_request_body_as_etree_with_ns_map(request)
        }
        print(self.request_body["plain"])
        return super(CalDavView, self).dispatch(request, path)

    def get_request_body_as_etree_with_ns_map(self, request):
        try:
            ns_map = {}
            ns_map.update(WebDAV_MAP)
            ns_map.update(CalDAV_MAP)
            ns_map.update(CalendarServer_MAP)
            return {
                "etree": etree.ElementTree(etree.fromstring(request.body, etree.XMLParser(ns_clean=True))),
                "namespaces": ns_map
            }
        except:
            return {
                "etree": None,
                "namespaces": None
            }

    def get_elements(self, xpath):
        return self.request_body["xml"]["etree"].xpath(
            xpath,
            namespaces=self.request_body["xml"]["namespaces"]
        )

    @staticmethod
    def getECTag(string):
        h = hashlib.md5()
        h.update(string.encode("utf-8"))
        return h.hexdigest()

    def _allowed_methods(self):
        allowed_methods = []
        for http_method_name in self.http_method_names:
            allowed_methods.append(http_method_name.upper())
        return allowed_methods

    def propfind(self, request, path, xbody=None, *args, **kwargs):

        if not self.has_access(self.resource, 'read'):
            return HttpResponseForbidden()

        # TODO fix case: users/{username} -> exist=False
        #if not self.resource.exists:
        #    return HttpResponseNotFound()

        if not self.get_access(self.resource):
            return HttpResponseForbidden()

        response_properties = []

        for known_property in self.KNOWN_PROPERTIES:
            try:
                #elements = xbody('/D:propfind/D:prop/{property}'.format(property=known_property))
                elements = self.get_elements('/D:propfind/D:prop/{property}'.format(property=known_property))
                if elements:
                    response_properties.append((known_property, elements))
            except Exception as e:
                print str(e)

        current_user_name = request.user.username
        if not current_user_name:
            current_user_name = str(request.user)

        responses = []
        properties = []
        for response_property in response_properties:
            if response_property[0] == "D:resourcetype":
                properties.append(
                    WebDAV(
                        "resourcetype",
                        WebDAV("collection"),
                        CalDAV("calendar")
                    )
                )
            elif response_property[0] == "D:owner":
                properties.append(
                    WebDAV(
                        "owner",
                        WebDAV(
                            "href",
                            url_join(
                                self.base_url,
                                "/users/{user_name}".format(
                                    user_name=current_user_name
                                )
                            )
                        )
                    )
                )
            elif response_property[0] == "D:current-user-principal":
                properties.append(
                    WebDAV(
                        "current-user-principal",
                        WebDAV(
                            "href",
                            url_join(
                                self.base_url,
                                "/users/{current_user}".format(
                                    current_user=current_user_name
                                )
                            )
                        )
                    )
                )
            elif response_property[0] == "D:supported-report-set":
                properties.append(
                    WebDAV(
                        "supported-report-set",
                        WebDAV(
                            "supported-report",
                            WebDAV(
                                "report",
                                CalDAV("calendar-multiget")
                            )
                        )
                    )
                )
                """ TODO
                WebDAV(
                    "supported-report",
                    WebDAV(
                        "report",
                        CalDAV("calendar-query")
                    )
                ),
                WebDAV(
                    "supported-report",
                    WebDAV(
                        "report",
                        CalDAV("free-busy-query")
                    )
                ),
                WebDAV(
                    "supported-report",
                    WebDAV(
                        "report",
                        CalDAV("expand-property")
                    )
                ),
                WebDAV(
                    "supported-report",
                    WebDAV(
                        "report",
                        CalDAV("principal-property-search")
                    )
                ),
                WebDAV(
                    "supported-report",
                    WebDAV(
                        "report",
                        CalDAV("principal-search-property-set")
                    )
                )
                """
            elif response_property[0] == "C:supported-calendar-component-set":
                properties.append(
                    CalDAV(
                        "supported-calendar-component-set",
                        CalDAV("comp", name="VEVENT")
                    )
                )
                """ TODO
                CalDAV("comp", name="VTODO"),
                CalDAV("comp", name="VJOURNAL")
                """
            elif response_property[0] == "D:getetag":
                properties.append(
                    WebDAV("getetag", "\"{datetime}\"".format(datetime=str(datetime.now())))
                )
            elif response_property[0] == "CS:getctag":
                properties.append(
                    CalendarServer("getctag", "\"{datetime}\"".format(datetime=str(datetime.now())))
                )
            elif response_property[0] == "D:getcontenttype":
                responses.append(
                    WebDAV(
                        "response",
                        WebDAV.href(url_join(
                            self.base_url,
                            "/calendars/{current_user}/default.ics".format(
                                current_user=current_user_name
                            )
                        )),
                        WebDAV(
                            "propstat",
                            WebDAV(
                                "prop",
                                WebDAV("getcontenttype", "text/calendar; charset=utf-8"),
                                WebDAV("resourcetype"),
                                WebDAV("getetag", "\"{datetime}\"".format(datetime=str(datetime.now())))
                            ),
                            WebDAV("status", "HTTP/1.1.200.OK")
                        )
                    )
                )
            elif response_property[0] == "D:displayname":
                properties.append(
                    WebDAV(
                        "displayname",
                        url_join(
                            self.base_url,
                            "/calendars/{current_user}".format(
                                current_user=current_user_name
                            )
                        )
                    )
                )
            elif response_property[0] == "D:principal-collection-set":
                properties.append(
                    WebDAV(
                        "principal-collection-set",
                        WebDAV("href", url_join(self.base_url, "/acl/users")),
                        WebDAV("href", url_join(self.base_url, "/acl/groups"))
                    )
                )
            elif response_property[0] == "D:principal-URL":
                properties.append(
                    WebDAV(
                        "principal-URL",
                        WebDAV(
                            "href",
                            url_join(
                                self.base_url,
                                "/users/{current_user}".format(
                                    current_user=current_user_name
                                )
                            )
                        )
                    )
                )
            elif response_property[0] == "D:resource-id":
                properties.append(
                    WebDAV(
                        "resource-id",
                        WebDAV(
                            "href",
                            url_join(
                                self.base_url,
                                "/calendars/{current_user}/default.ics".format(
                                    current_user=current_user_name
                                )
                            )
                        )
                    )
                )
            elif response_property[0] == "C:calendar-home-set":
                properties.append(
                    CalDAV(
                        "calendar-home-set",
                        WebDAV(
                            "href",
                            url_join(
                                self.base_url,
                                "/calendars/{current_user}".format(current_user=current_user_name)
                            )
                        )
                    )
                )
            elif response_property[0] == "C:calendar-user-address-set":
                properties.append(
                    CalDAV("calendar-user-address-set")
                )
                # TODO <C:calendar-user-address-set><D:href>mailto:{user_mail}</D:href></C:calendar-user-address-set>
            elif response_property[0] == "CS:email-address-set":
                properties.append(
                    CalendarServer("email-address-set")
                )
                # TODO <CS:email-address-set><D:href>mailto:{user_mail}</D:href></CS:email-address-set>
            elif response_property[0] == "CS:dropbox-home-URL":
                properties.append(
                    CalendarServer("dropbox-home-URL")
                )
                # TODO <CS:dropbox-home-URL>/calendar/r/dav/users/bgs_demo07@try.lotuslive.com/</CS:dropbox-home-URL>
            elif response_property[0] == "CS:notification-URL":
                properties.append(
                    CalendarServer("notification-URL")
                )
                # TODO <CS:notification-URL>/calendar/r/dav/users/bgs_demo07@try.lotuslive.com/</CS:notification-URL>
            elif response_property[0] == "C:schedule-inbox-URL":
                properties.append(
                    CalDAV("schedule-inbox-URL")
                )
                # TODO <C:schedule-inbox-URL><D:href>/calendar/r/dav/calendar/bgs_demo07@try.lotuslive.com/inbox/</D:href></C:schedule-inbox-URL>
            elif response_property[0] == "C:schedule-outbox-URL":
                properties.append(
                    CalDAV("schedule-outbox-URL")
                )
                # TODO <C:schedule-outbox-URL><D:href>/calendar/r/dav/calendar/bgs_demo07@try.lotuslive.com/outbox/</D:href></C:schedule-outbox-URL>


        responses.append(
            WebDAV.response(
                WebDAV.href(url_join(self.base_url, "/calendars/{current_user}".format(current_user=current_user_name))),
                WebDAV.propstat(
                    WebDAV.prop(*properties),
                    WebDAV.status('HTTP/1.1 200 OK'),
                )
            )
        )
        body = WebDAV.multistatus(*responses)
        response = self.build_xml_response(body, HttpResponseMultiStatus)
        print(response.content)
        return response

    def report(self, request, path, xbody=None, *args, **kwargs):
        calendar_uris = self.get_elements('/C:calendar-multiget/D:href')
        calendar_query = self.get_elements('/C:calendar-query')

        if not calendar_uris:
            calendar_uris = [request.path]
            """ TODO support for query
            <?xml version="1.0" encoding="UTF-8"?>
            <C:calendar-query xmlns:C="urn:ietf:params:xml:ns:caldav">
              <B:prop xmlns:B="DAV:">
                <B:getetag/>
                <B:getcontenttype/>
              </B:prop>
              <C:filter>
                <C:comp-filter name="VCALENDAR">
                  <C:comp-filter name="VEVENT">
                    <C:time-range start="20140721T000000Z"/>
                  </C:comp-filter>
                </C:comp-filter>
              </C:filter>
            </C:calendar-query>
            """

        responses = []

        for calendar_uri in calendar_uris:
            if not calendar_query:
                calendar_uri = calendar_uri.text
            feed = self.feed_view()
            feed_request = HttpRequest()
            feed_request.method = "GET"
            feed_request.path = calendar_uri
            feed_request.is_secure = request.is_secure
            feed_request.path = request.path
            feed_response = feed.__call__(request).content
            feed_response = feed_response.replace("\r", "")
            if not calendar_query:
                events = CalDavFeedView.one_event_per_calendar(feed_response)
            else:
                events = [(calendar_uri, smart_unicode(feed_response))]

            responses.append(
                WebDAV(
                    "multistatus",
                    *[
                        WebDAV(
                            "response",
                            WebDAV("href", event[0]),
                            WebDAV(
                                "propstat",
                                WebDAV(
                                    "prop",
                                    CalDAV("calendar-data", event[1])
                                ),
                                WebDAV("getetag", "\"{etag}\"".format(etag=CalDavView.getECTag(event[1])))
                            ),
                            WebDAV("status", "HTTP/1.1.200.OK")
                        ) for event in events
                    ]
                )
            )

        body = WebDAV.multistatus(*responses)

        response = self.build_xml_response(body, HttpResponseMultiStatus)
        print(response.content)
        return response

    def put(self, request, path, xbody=None, *args, **kwargs):
        calendar = Calendar.from_ical(self.request_body["plain"])
        for component in calendar.walk():
            if component.name == "VEVENT":
                base_item = CalDavEvent()
                base_item.uid = component.get("UID")
                base_item.title = component.get("SUMMARY")
                base_item.start_datetime = component.get("DTSTART")
                base_item.end_datetime = component.get("DTEND")
                base_item.location = component.get("LOCATION")
                base_item.description = component.get("DESCRIPTION")
                base_item.finalize()
                return self.feed_view.item_save(base_item, component)
        return HttpResponseBadRequest()