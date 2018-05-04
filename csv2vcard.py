#!/usr/bin/env python3

import argparse
import codecs
import csv
import os.path
import uuid

import vobject

EXTENSION = "vcf"


def read_csv(filename):
    with codecs.open(filename, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f, delimiter=';'))


def create_vcard(data):
    """Create and return a serialized vcard."""
    c = vobject.vCard()
    c.add('n')
    c.n.value = vobject.vcard.Name(family=data['Family Name'],
                                   given=data['Given Name'],
                                   prefix=data['Name Prefix'],
                                   suffix=data['Name Suffix'],
                                   additional=data['Additional Name'],
                                   )
    c.add('fn')
    c.fn.value = ' '.join([
        data['Name Prefix'],
        data['Given Name'],
        data['Family Name'],
    ])

    # Organization
    c.add('org')
    c.org.value = [data['Organization 1 - Name']]
    if data['Organization 1 - Department']:
        c.org.value.append(data['Organization 1 - Department'])

    c.add('title')
    c.title.value = data['Organization 1 - Title']

    c.add('notes')
    c.notes.value = data['Notes']

    # Tel
    for i in range(1, 6):
        if not data['Phone %d - Type' % i]:
            break
        tel = c.add('tel')
        tel.value = data['Phone %d - Value' % i]
        tel.type_param = data['Phone %d - Type' % i]

    # Emails
    for i in range(1, 2):
        if not data['E-mail %d - Type' % i]:
            break
        tel = c.add('email')
        tel.value = data['E-mail %d - Value' % i]
        tel.type_param = data['E-mail %d - Type' % i]

    # Addresses
    for i in range(1, 2):
        prefix = 'Address %d - ' % i
        if not data[prefix + 'Type']:
            break
        address = c.add('adr')
        address.type_param = data[prefix + 'Type']
        address.value = vobject.vcard.Address(
            street=data[prefix + 'Street'],
            city=data[prefix + 'City'],
            region=data[prefix + 'Region'],
            code=data[prefix + 'Postal Code'],
            country=data[prefix + 'Country'],
        )

    # Websites
    for i in range(1, 2):
        prefix = 'Website %d - ' % i
        if not data[prefix + 'Type']:
            break
        web = c.add('url')
        web.type_param = data[prefix + 'Type']
        web.value = data[prefix + 'Value']

    # IM
    for i in range(1, 2):
        prefix = 'IM %d - ' % i
        if not data[prefix + 'Type']:
            break
        o = c.add('impp')
        o.type_param = data[prefix + 'Type']
        o.value = data[prefix + 'Value']

    c.add('categories')
    c.categories.value = [data['Group Membership']]

    return c.serialize()


def dump_all(cards, outdir):
    for c in cards:
        filename = os.path.join(outdir,
                                "%s.%s" % (uuid.uuid4(), EXTENSION))
        with open(filename, "w") as f:
            f.write(c)


def convert(csv_file, outdir):
    data = read_csv(csv_file)
    vcards = []
    for row in data:
        vcards.append(create_vcard(row))

    dump_all(vcards, outdir)


def main(args):
    convert(csv_file=args.infile, outdir=args.outdir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a CSV into a vcard format")
    parser.add_argument("infile", help="CSV filename")
    parser.add_argument("--outdir", help="outdir")
    args = parser.parse_args()
    main(args)
