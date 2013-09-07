#!/usr/bin/env python

# Copyright (C) 2013 nu774
# For conditions of distribution and use, see copyright notice in COPYING

import sys
import re
from subprocess import Popen, PIPE
from itertools import groupby
from collections import namedtuple

GITLOG_FMT = 'commit %H%nauthor %cn <%ae>%ndate %ad%nsubject %s%nref %d%n%n'
GITLOG_CMD = ['git','log','--date=short','--format={0}'.format(GITLOG_FMT)]

Commit = namedtuple('Commit', 'commit author date subject ref')

def parse_gitlog(stream):
    re_decode_tag = re.compile(r'(?<=\()([^,)]+)')
    commit = dict()
    for line in stream:
        fields = line.decode('utf-8').rstrip('\r\n').split(' ', 1)
        if len(fields) == 2:
            key, value = fields
            if key == 'ref':
                m = re_decode_tag.search(value)
                value = ' [{0}]'.format(m.group()) if m else ''
            commit[key] = value
        elif commit:
            yield Commit(**commit) 
            commit = dict()

output=sys.stdout.write

with Popen(GITLOG_CMD, shell=False, stdout=PIPE).stdout as pipe:
    commits = parse_gitlog(pipe)
    commits_by_date_author = groupby(commits, key=lambda x: (x.date, x.author))
    for (date, author), commits in commits_by_date_author:
        output('{0}  {1}\n\n'.format(date, author))
        for c in commits:
            output('  * {0}{1}\n\n'.format(c.subject, c.ref))
