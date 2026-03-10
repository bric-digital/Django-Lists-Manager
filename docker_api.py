# pylint: disable=line-too-long, no-member

import json

from django.contrib import messages
from django.core import serializers

from .models import ListItem, List, Vocabulary

def import_objects(file_type, import_file):
    if file_type == 'lists_manager.listitem':
#         return import_list_items(import_file)
#
#     if file_type == 'keystone.listitem':
        return import_keystone_list_items(import_file)

    if file_type == 'lists_manager.vocabulary':
        return import_vocabulary_items(import_file)

    if file_type == 'lists_manager.list':
        return import_lists(import_file)

    return None

def import_vocabulary_items(import_file):
    user_messages = []

    with import_file.open() as file_stream:
        vocabs_json = json.load(file_stream)

        items_imported = 0

        for vocab_json in vocabs_json: # pylint: disable=too-many-nested-blocks
            if vocab_json.get('model', None) == 'lists_manager.vocabulary':
                item_obj = Vocabulary()

                for field_key in vocab_json.get('fields', {}).keys():
                    field_value = vocab_json.get('fields', {}).get(field_key, None)

                    setattr(item_obj, field_key, field_value)

                item_obj.save()

                items_imported += 1

        if items_imported > 1:
            user_messages.append(('%s vocabularies imported.' % items_imported, messages.SUCCESS))
        elif items_imported == 1:
            user_messages.append(('1 vocabulary imported.', messages.SUCCESS))
        else:
            user_messages.append(('No vocabularies imported.', messages.INFO))

    return user_messages

def import_lists(import_file):
    user_messages = []

    with import_file.open() as file_stream:
        lists_json = json.load(file_stream)

        lists_imported = 0

        for list_json in lists_json: # pylint: disable=too-many-nested-blocks
            if list_json.get('model', None) == 'lists_manager.list':
                list_obj = List()

                for field_key in item_json.get('fields', {}).keys():
                    field_value = item_json.get('fields', {}).get(field_key, None)

                    setattr(item_obj, field_key, field_value)

                for item_json in list_json['items']:
                    if item_json.get('model', None) == 'lists_manager.listitem':
                        item_obj = ListItem()

                        for field_key in item_json.get('fields', {}).keys():
                            field_value = item_json.get('fields', {}).get(field_key, None)

                            setattr(item_obj, field_key, field_value)

                        item_obj.member_of = list_obj

                        item_obj.save()

                        items_imported += 1

                vocabulary = List.objects.filter(name=list_json['vocabulary__name']).first()

                if vocabulary is None:
                    vocabulary = Vocabulary.objects.create(name=list_json['vocabulary__name'])

                list_obj.vocabulary = vocabulary

                list_obj.save()

                items_imported += 1

        if lists_imported > 1:
            user_messages.append(('%s lists imported.' % lists_imported, messages.SUCCESS))
        elif lists_imported == 1:
            user_messages.append(('1 list imported.', messages.SUCCESS))
        else:
            user_messages.append(('No lists imported.', messages.INFO))

    return user_messages

def import_list_items(import_file): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    user_messages = []

    with import_file.open() as file_stream:
        items_json = json.load(file_stream)

        items_imported = 0

        for item_json in items_json: # pylint: disable=too-many-nested-blocks
            if item_json.get('model', None) == 'lists_manager.listitem':
                item_obj = ListItem()

                for field_key in item_json.get('fields', {}).keys():
                    field_value = item_json.get('fields', {}).get(field_key, None)

                    setattr(item_obj, field_key, field_value)

                list_obj = List.objects.filter(name=item_json['list__name']).first()

                if list_obj is None:
                    list_obj = List.objects.create(name=item_json['list__name'])

                item_obj.member_of = list_obj

                item_obj.save()

                items_imported += 1

        if items_imported > 1:
            user_messages.append(('%s list items imported.' % items_imported, messages.SUCCESS))
        elif items_imported == 1:
            user_messages.append(('1 list item imported.', messages.SUCCESS))
        else:
            user_messages.append(('No list items imported.', messages.INFO))

    return user_messages

def import_keystone_list_items(import_file): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    user_messages = []

    with import_file.open() as file_stream:
        items_json = json.load(file_stream)

        items_imported = 0

        for item_json in items_json: # pylint: disable=too-many-nested-blocks
            if item_json.get('model', None) == 'keystone.listitem':
                item_obj = ListItem()

                item_obj.name = item_json.get('fields', {}).get('name', 'Unknown')
                item_obj.value = item_json.get('fields', {}).get('domain', 'Unknown')
                item_obj.item_type = item_json.get('fields', {}).get('pattern_type', 'Unknown')
                item_obj.tags = [item_json.get('fields', {}).get('category', 'Unknown'),]

                list_name = item_json.get('fields', {}).get('list_name', 'Unknown')

                list_obj = List.objects.filter(name=list_name).first()

                if list_obj is None:
                    list_obj = List.objects.create(name=list_name)

                item_obj.member_of = list_obj

                item_obj.save()

                items_imported += 1

        if items_imported > 1:
            user_messages.append(('%s Keystone list items imported.' % items_imported, messages.SUCCESS))
        elif items_imported == 1:
            user_messages.append(('1 Keystone list item imported.', messages.SUCCESS))
        else:
            user_messages.append(('No Keystone list items imported.', messages.INFO))

    return user_messages

def export_list_items(queryset):
    to_export = []

    for list_item in queryset:
        list_item_json = json.loads(serializers.serialize('json', ListItem.objects.filter(pk=list_item.pk)))[0]

        del list_item_json['pk']
        del list_item_json['fields']['list']

        list_item_json['list__name'] = list_item.member_of.name

        to_export.append(list_item_json)

    return to_export

def export_lists(queryset):
    to_export = []

    for list_obj in queryset:
        list_obj_json = json.loads(serializers.serialize('json', List.objects.filter(pk=list_obj.pk)))[0]

        del list_obj_json['pk']
        del list_obj_json['fields']['vocabulary']

        list_obj_json['vocabulary__name'] = list_obj.vocabulary.name

        list_obj_json['items'] = []

        for item in list_obj.items.all().order_by('pk'):
            item_json = json.loads(serializers.serialize('json', ListItem.objects.filter(pk=item.pk)))[0]

            del item_json['pk']
            del item_json['fields']['list']

            list_obj_json['items'].append(item_json)

        to_export.append(list_obj_json)

    return to_export

def export_vocabularies(queryset):
    to_export = []

    for vocabulary in queryset:
        vocabulary_json = json.loads(serializers.serialize('json', Vocabulary.objects.filter(pk=vocabulary.pk)))[0]

        del vocabulary_json['pk']

        to_export.append(vocabulary_json)

    return to_export

def export_objects(queryset, queryset_name):
    to_export = []

    if queryset_name == 'ListItem':
        to_export.extend(export_list_items(queryset))

    if queryset_name == 'List':
        to_export.extend(export_lists(queryset))

    if queryset_name == 'Vocabulary':
        to_export.extend(export_vocabularies(queryset))

    return to_export
