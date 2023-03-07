#!/usr/bin/env python3

import json
import sys

def indent(level):
    print('  ' * level, end='')

def print_type(name, typename, level):
    indent(level)
    if name:
        print(' * ``%s`` (%s)' % (name, typename))
    else:
        print(' * %s' % typename)

def process_array(name, d, level):
    print_type(name, 'array', level)
    min_items = d.get('minItems', 1)
    unique = {False: '', True: ' (unique)'}[d.get('uniqueItems', True)]
    if 'items' in d:
        items = d.get('items')
        if type(items) == dict:
            process_schema(name, items, level)
        else:
            process_sequence(name, 'at least %i%s of' % (min_items, unique), items, level)

def process_boolean(name, d, level):
    print_type(name, 'boolean', level)

def process_integer(name, d, level):
    print_type(name, 'integer', level)

def process_null(name, d, level):
    print_type(name, 'null', level)

def process_object(name, d, level):
    print_type(name, 'object', level)
    if 'properties' in d:
        print()
        for name, value in d['properties'].items():
            process_schema(name, value, level + 1)
    elif 'patternProperties' in d:
        print()
        for name, value in d['patternProperties'].items():
            process_schema(name, value, level + 1)

def process_ref(name, d, level):
    print_type(name, 'ref', level)
    return

def process_sequence(name, label, items, level):
    indent(level)
    print(' * ``%s`` %s' % (name, label))
    print()
    for item in items:
        process_schema('', item, level + 1)
    print()

def process_string(name, d, level):
    print_type(name, 'string', level)

handlers = {
    'array': process_array,
    'boolean': process_boolean,
    'integer': process_integer,
    'null': process_null,
    'object': process_object,
    'string': process_string,
}

def process_schema(name, d, level):
    if 'type' in d:
        if type(d['type']) == list:
            for t in d['type']:
                handlers[t](name, d, level)
                indent(level + 1)
                print('   *or*')
        else:
            handlers[d['type']](name, d, level)
    elif '$ref' in d:
        process_ref(name, d, level)
    elif 'allOf' in d:
        process_sequence(name, '(type must match all of these)', d['allOf'], level)
    elif 'anyOf' in d:
        process_sequence(name, '(type can match any of these)', d['anyOf'], level)
    elif 'pattern' in d:
        indent(level)
        print(' * pattern: ``%s``' % d['pattern'])
    elif 'not' in d:
        indent(level)
        print(' * *not*')
        print()
        process_schema('', d['not'], level + 1)

def main(schema_file_name):
    d = json.load(open(schema_file_name))
    process_schema(d['title'], d, 0)
    return d

if __name__ == "__main__":
    if len(sys.argv) == 2:
        d = main(sys.argv[1])
