# coding=utf-8
from django.db import models
from django.utils.timezone import now
from django_caldav.utils import iCalendar


class BaseDavModel(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(default=now)
    modified = models.DateTimeField(default=now)

    class Meta(object):
        abstract = True


class CollectionModel(BaseDavModel):
    parent = models.ForeignKey('self', blank=True, null=True)
    size = 0

    class Meta(object):
        unique_together = (('parent', 'name'),)


class ObjectModel(BaseDavModel):
    parent = models.ForeignKey(CollectionModel, blank=True, null=True)
    size = models.IntegerField(default=0)
    content = models.TextField(default=u"")

    class Meta(object):
        unique_together = (('parent', 'name'),)


class CalDavEvent(models.Model):
    uid = None  # This value is not store in DB and contains value returned from item_guid
    title = models.CharField(max_length=70)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)

    location = models.CharField(max_length=140, null=True, blank=True)

    description = models.TextField(null=True, blank=True)

    def finalize(self):
        """
        Converts from iCalendar types to python types
        """
        if self.uid:
            self.uid = iCalendar.unicode(self.uid)

        self.title = iCalendar.unicode(self.title)

        self.start_datetime = iCalendar.datetime(self.start_datetime).replace(tzinfo=None)

        if self.end_datetime:
            self.end_datetime = iCalendar.datetime(self.end_datetime).replace(tzinfo=None)

        if self.location:
            self.location = iCalendar.unicode(self.location)

        if self.description:
            self.description = iCalendar.unicode(self.description)

    class Meta(object):
        abstract = True