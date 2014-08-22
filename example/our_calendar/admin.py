# coding=utf-8
from django.contrib import admin
from .models import OurCalendarEvent


class OurCalendarEventAdmin(admin.ModelAdmin):
    date_hierarchy = "start_datetime"
    list_display = ("title", "start_datetime", "location")

admin.site.register(OurCalendarEvent, OurCalendarEventAdmin)