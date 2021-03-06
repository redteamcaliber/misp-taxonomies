#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python script parsing the MISP taxonomies expressed in Machine Tags (Triple
# Tags) to list all valid tags from a specific taxonomy.
#
# Copyright (c) 2015 Alexandre Dulaunoy - a@foo.be
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import os.path
import argparse

taxonomies = ['admiralty-scale','tlp', 'circl', 'veris', 'ecsirt', 'dni-ism', 'nato', 'euci']

argParser = argparse.ArgumentParser(description='Dump Machine Tags (Triple Tags) from MISP taxonomies')
argParser.add_argument('-e', action='store_true', help='Include expanded tags')
argParser.add_argument('-a', action='store_true', help='Generate asciidoctor document from MISP taxonomies')
argParser.add_argument('-v', action='store_true', help='Include descriptions')
args = argParser.parse_args()

doc = ''
if args.a:
    doc = doc + ":toc: right\n"
    doc = doc + ":icons: font\n"
    doc = doc + ":images-cdn: https://raw.githubusercontent.com/MISP/MISP/master/INSTALL/logos/\n"
    doc = doc + "= MISP taxonomies and classification as machine tags\n\n"
    doc = doc + "Generated from https://github.com/MISP/misp-taxonomies.\n\n"
    doc = doc + "\nimage::{images-cdn}misp-logo.png[MISP logo]\n"
    doc = doc + "Taxonomies that can be used in MISP (2.4) and other information sharing tool and expressed in Machine Tags (Triple Tags). A machine tag is composed of a namespace (MUST), a predicate (MUST) and an (OPTIONAL) value. Machine tags are often called triple tag due to their format.\n"
    doc = doc + "\n\n"

def asciidoc(content=False, adoc=doc, t='title'):
    if not args.a:
        return False
    adoc = adoc + "\n"
    if t == 'title':
        content = '==== ' + content
    elif t == 'predicate':
        content = '=== ' + content
    elif t == 'namespace':
        content = '== ' + content + '\n'
        content = content + 'NOTE: ' + namespace + ' namespace available in JSON format at https://github.com/MISP/misp-taxonomies/blob/master/' + namespace + '/machinetag.json[*this location*]. The JSON format can be freely reused in your application or automatically enabled in https://www.github.com/MISP/MISP[MISP] taxonomy.'
    elif t == 'description':
        content = '\n'+content+'\n'
    adoc = adoc + content
    return adoc

def machineTag(namespace=False, predicate=False, value=None):

    if namespace is False or predicate is False:
        return None
    if value is None:
        return ('{0}:{1}'.format(namespace, predicate))
    else:
        return ('{0}:{1}=\"{2}\"'.format(namespace, predicate, value))

for taxonomy in taxonomies:
    filename = os.path.join("../", taxonomy, "machinetag.json")
    with open(filename) as fp:
        t = json.load(fp)
    namespace = t['namespace']
    if args.a:
       doc = asciidoc(content=t['namespace'], adoc=doc, t='namespace')
       doc = asciidoc(content=t['description'], adoc=doc, t='description')
    if args.v:
        print ('{0}'.format(t['description']))
    for predicate in t['predicates']:
        if args.a:
            doc = asciidoc(content=predicate['value'], adoc=doc, t='predicate')
        if t.get('values') is None:
            if args.a:
                doc = asciidoc(content=machineTag(namespace=namespace, predicate=predicate['value']), adoc=doc)
                doc = asciidoc(content=machineTag(namespace=namespace, predicate=predicate['expanded']), adoc=doc, t='description')
                if predicate.get('description'):
                    doc = asciidoc(content=machineTag(namespace=namespace, predicate=predicate['description']), adoc=doc, t='description')
            else:
                print (machineTag(namespace=namespace, predicate=predicate['value']))
            if args.e:
                 print ("--> " + machineTag(namespace=namespace, predicate=predicate['expanded']))
                 if predicate.get('description'):
                     print ("--> " + predicate['description'])
        else:
            for e in t['values']:
                if e['predicate'] == predicate['value']:
                    if 'expanded' in predicate:
                        expanded = predicate['expanded']
                    for v in e['entry']:
                        if args.a:
                            doc = asciidoc(content=machineTag(namespace=namespace, predicate=e['predicate'], value=v['value']), adoc=doc)
                            doc = asciidoc(content=machineTag(namespace=namespace, predicate=v['expanded']), adoc=doc, t='description')
                        else:
                            print (machineTag(namespace=namespace, predicate=e['predicate'], value=v['value']))
                        if args.e:
                            print ("--> " + machineTag(namespace=namespace, predicate=expanded, value=v['expanded']))

if args.a:
    print (doc)
