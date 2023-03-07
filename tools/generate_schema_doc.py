#!/usr/bin/env python3

import json
import sys

def indent(level):
    print('  ' * level, end='')

def typestring(types):
    l = [typenames[t] for t in types]
    return ' *or* '.join(l)

def process_array(name, d, level):
    min_items = d.get('minItems', 1)
    unique = {False: ' ', True: 'unique '}[d.get('uniqueItems', True)]
    indent(level)
    print('   *with at least %i %sitem(s) of*' % (min_items, unique))
    if 'items' in d:
        items = d.get('items')
        if type(items) == dict:
            process_schema(None, items, level)
        elif len(items) == 1:
            process_schema(None, items[0], level)
        else:
            process_sequence(items, level)

def process_boolean(name, d, level):
    return

def process_integer(name, d, level):
    return

def process_null(name, d, level):
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
    print('ref: ``%s``' % d['$ref'])

def process_sequence(items, level):
    #indent(level)
    #print(' * ``%s`` %s' % (name, label))
    print()
    for item in items:
        process_schema('', item, level + 1)
    print()

def process_string(name, d, level):
    if 'enum' in d:
        indent(level)
        values = ', '.join([('``"%s"``' % s) for s in d['enum']])
        print('   *value must be one of* %s' % values)

handlers = {
    'array': process_array,
    'boolean': process_boolean,
    'integer': process_integer,
    'null': process_null,
    'object': process_object,
    'string': process_string,
}

typenames = {
    'array': 'array',
    'boolean': 'boolean',
    'integer': 'integer',
    'null': 'null',
    'object': '',
    'string': 'string'
}

def process_schema(name, d, level):
    if level >= 0:
        indent(level)
        if name:
            print(' * ', end='')
            print('``%s`` ' % name, end='')
        elif name == '':
            print(' * ', end='')
        else:
            print('   ', end='')

    if 'type' in d:
        if type(d['type']) == list:
            types = d['type']
        else:
            types = [d['type']]

        s = typestring(types)
        if s:
            print(s, end='')
        elif not name:
            print('*object with properties*')
        print()

        for t in types:
            handlers[t](name, d, level)
    elif '$ref' in d:
        process_ref(name, d, level)
    elif 'allOf' in d:
        print('*type must match all of these*')
        process_sequence(d['allOf'], level)
    elif 'anyOf' in d:
        print('*type can match any of these*')
        process_sequence(d['anyOf'], level)
    elif 'oneOf' in d:
        print('*type matching one of these*')
        process_sequence(d['oneOf'], level)
    elif 'pattern' in d:
        print('pattern: ``%s``' % d['pattern'])
    elif 'not' in d:
        print('*not*')
        print()
        process_schema('', d['not'], level + 1)
    else:
        print()

def main(schema_file_name):
    d = json.load(open(schema_file_name))
    process_schema(d['title'], d, -1)
    return d

if __name__ == "__main__":
    if len(sys.argv) == 2:
        d = main(sys.argv[1])
