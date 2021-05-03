"""
Dump the list of courses and its structure

Location: /edx/app/edxapp/edx-platform/lms/djangoapps/courseware/management/commands/dump_structures.py
Run with
sudo -u edxapp /edx/bin/python.edxapp /edx/app/edxapp/edx-platform/manage.py lms --settings production dump_structure [--category=<category>]

"""
import json
from textwrap import dedent
import csv
import sys

from django.core.management.base import BaseCommand, CommandError
from xblock.fields import Scope
from xblock_discussion import DiscussionXBlock
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.inheritance import compute_inherited_metadata, own_metadata
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

FILTER_LIST = ['xml_attributes']
INHERITED_FILTER_LIST = ['children', 'xml_attributes']


class Command(BaseCommand):
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument('--modulestore',
                            default='default',
                            help='name of the modulestore')
        parser.add_argument('--inherited',
                            action='store_true',
                            help='include inherited metadata')
        parser.add_argument('--inherited_defaults',
                            action='store_true',
                            help='include default values of inherited metadata')
        parser.add_argument('--category',
                            default=None,
                            help='filter only this category block (e.g. video, html, etc.)')

    def handle(self, *args, **options):

        fieldnames = [
            'module_location',
            'block_type',
            'parent_id',
            'course',
            'chapter',
            'sequential',
            'vertical',
            'component'
        ]

        csvWriter = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter=',', doublequote=False, escapechar='\\')
        csvWriter.writeheader()

        # Get the courses
        course_keys = CourseOverview.get_all_course_keys()

        # Get the modulestore
        store = modulestore()

        for course_key in course_keys:

            course = store.get_course(course_key)
            if course is None:
                raise CommandError("Invalid course_id {}".format(str(course_key)))

            # Precompute inherited metadata at the course level, if needed:

            if options['inherited']:
                compute_inherited_metadata(course)

            # Convert course data to dictionary and dump it as JSON to stdout

            info = dump_module(course, inherited=options['inherited'], defaults=options['inherited_defaults'], category_filter=options['category'])

        csvWriter.writerows(structure)

        #return json.dumps(info, indent=2, sort_keys=True, default=unicode)

structure = []

def dump_module(module, destination=None, inherited=False, defaults=False, category_filter = None, upper_structure={}):
    """
    Add the module and all its children to the destination dictionary in
    as a flat structure.
    """

    destination = destination if destination else {}

    items = own_metadata(module)

    # HACK: add discussion ids to list of items to export (AN-6696)
    if isinstance(module, DiscussionXBlock) and 'discussion_id' not in items:
        items['discussion_id'] = module.discussion_id

    filtered_metadata = {k: v for k, v in items.iteritems() if k not in FILTER_LIST}

    destination[unicode(module.location)] = {
        'category': module.location.block_type,
        'children': [unicode(child) for child in getattr(module, 'children', [])],
        'metadata': filtered_metadata,
    }

    if inherited:
        # When calculating inherited metadata, don't include existing
        # locally-defined metadata
        inherited_metadata_filter_list = list(filtered_metadata.keys())
        inherited_metadata_filter_list.extend(INHERITED_FILTER_LIST)

        def is_inherited(field):
            if field.name in inherited_metadata_filter_list:
                return False
            elif field.scope != Scope.settings:
                return False
            elif defaults:
                return True
            else:
                return field.values != field.default

        inherited_metadata = {field.name: field.read_json(module) for field in module.fields.values() if is_inherited(field)}
        destination[unicode(module.location)]['inherited_metadata'] = inherited_metadata

    display_name = filtered_metadata['display_name'] if 'display_name' in filtered_metadata else ''

    children = module.get_children()
    if not children:
        if not category_filter or category_filter == module.location.block_type:
            structure.append({
                'module_location': unicode(module.location),
                'block_type': module.location.block_type,
                'parent_id': upper_structure['parent_id'],
                'course': upper_structure['course'],
                'chapter': upper_structure['chapter'],
                'sequential': upper_structure['sequential'],
                'vertical': upper_structure['vertical'],
                'component': display_name,
            })
    elif module.location.block_type == 'course':
        structure.append({
            'module_location': unicode(module.location),
            'block_type': module.location.block_type,
            'parent_id': '',
            'course': display_name
        })
    elif module.location.block_type == 'chapter':
        structure.append({
            'module_location': unicode(module.location),
            'block_type': module.location.block_type,
            'parent_id': upper_structure['parent_id'],
            'course': upper_structure['course'],
            'chapter': display_name
        })
    elif module.location.block_type == 'sequential':
        structure.append({
            'module_location': unicode(module.location),
            'block_type': module.location.block_type,
            'parent_id': upper_structure['parent_id'],
            'course': upper_structure['course'],
            'chapter': upper_structure['chapter'],
            'sequential': display_name
        })
    elif module.location.block_type == 'vertical':
        structure.append({
            'module_location': unicode(module.location),
            'block_type': module.location.block_type,
            'parent_id': upper_structure['parent_id'],
            'course': upper_structure['course'],
            'chapter': upper_structure['chapter'],
            'sequential': upper_structure['sequential'],
            'vertical': display_name
        })

    upstream_structure = upper_structure
    upstream_structure[module.location.block_type] = display_name
    upstream_structure['parent_id'] = unicode(module.location)

    for child in children:
        dump_module(child, destination, inherited, defaults, category_filter, upstream_structure)

    return destination
