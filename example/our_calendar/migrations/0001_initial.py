# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OurCalendarEvent'
        db.create_table(u'our_calendar_ourcalendarevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('start_datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=140, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'our_calendar', ['OurCalendarEvent'])

    def backwards(self, orm):
        # Deleting model 'OurCalendarEvent'
        db.delete_table(u'our_calendar_ourcalendarevent')

    models = {
        u'our_calendar.ourcalendarevent': {
            'Meta': {'object_name': 'OurCalendarEvent'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        }
    }

    complete_apps = ['our_calendar']