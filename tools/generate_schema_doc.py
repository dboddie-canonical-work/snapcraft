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
    #print_type(name, 'array', level)
    min_items = d.get('minItems', 1)
    unique = {False: '', True: ' (unique)'}[d.get('uniqueItems', True)]
    if 'items' in d:
        items = d.get('items')
        if type(items) == dict:
            process_schema(name, items, level)
        else:
            #print(name, 'at least %i%s of' % (min_items, unique))
            process_sequence(items, level)

def process_boolean(name, d, level):
    #print_type(name, 'boolean', level)
    return

def process_integer(name, d, level):
    #print_type(name, 'integer', level)
    return

def process_null(name, d, level):
    #print_type(name, 'null', level)
    return

def process_object(name, d, level):
    if 'properties' in d:
        print()
        for name, value in d['properties'].items():
            process_schema(name, value, level + 1)
        print()
    elif 'patternProperties' in d:
        print()
        for name, value in d['patternProperties'].items():
            process_schema(name, value, level + 1)
        print()

def process_ref(name, d, level):
    #print_type(name, 'ref', level)
    print('(ref)')
    return

def process_sequence(items, level):
    #indent(level)
    #print(' * ``%s`` %s' % (name, label))
    print()
    for item in items:
        process_schema('', item, level + 1)
    print()

def process_string(name, d, level):
    #print_type(name, 'string', level)
    return

handlers = {
    'array': process_array,
    'boolean': process_boolean,
    'integer': process_integer,
    'null': process_null,
    'object': process_object,
    'string': process_string,
}

def process_schema(name, d, level):
    indent(level)
    print(' * ', end='')
    if name:
        print('``%s`` ' % name, end='')

    if 'type' in d:
        if type(d['type']) == list:
            types = d['type']
        else:
            types = [d['type']]

        print('(', end='')
        l = len(types)
        for t in types:
            print(t, end='')
            l -= 1
            if l > 0:
                indent(level + 1)
                print(' *or* ', end='')
        print(')')
        for t in types:
            handlers[t](name, d, level)
    elif '$ref' in d:
        process_ref(name, d, level)
    elif 'allOf' in d:
        print('(type must match all of these)')
        process_sequence(d['allOf'], level)
    elif 'anyOf' in d:
        print('(type can match any of these)')
        process_sequence(d['anyOf'], level)
    elif 'pattern' in d:
        print('pattern: ``%s``' % d['pattern'])
    elif 'not' in d:
        print('*not*')
        print()
        process_schema('', d['not'], level + 1)

def main(schema_file_name):
    d = json.load(open(schema_file_name))
    process_schema(d['title'], d, 0)
    return d

if __name__ == "__main__":
    if len(sys.argv) == 2:
        d = main(sys.argv[1])
