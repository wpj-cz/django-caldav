# coding=utf-8
from django.utils.timezone import now
from djangodav.db.resources import NameLookupDBDavMixIn, BaseDBDavResource
from .models import CollectionModel, ObjectModel


class CalDavResource(NameLookupDBDavMixIn, BaseDBDavResource):
    collection_model = CollectionModel
    object_model = ObjectModel