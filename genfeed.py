#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Generates csv list files for listfeed.py"""

# Author : Ginko
# Date : 14/11/2014
# Version : 0.1.a
# License : zlib/libpng

# The zlib/libpng License

# Copyright (c) 2014 Ginko Aloe - ginkobox.fr

# This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.
# Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:
#     1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
#     2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
#     3. This notice may not be removed or altered from any source distribution.

# --* Roadmap *--
# Make this script cgi capable
# Ship with a HTML form to invoke it with wished parameters easily

import sys, datetime

NOW = datetime.datetime.now()

DAY = datetime.timedelta(days=1)

CONFIG = {
	'start-time': NOW - 5 * DAY,
	'interval': DAY,
	'time-format': '%Y-%m-%dT%H:%M:%S',
}

def format_date(time):
	return str(time.strftime(CONFIG['time-format']))

def parse_list(filename):
	items = []
	with open(filename, 'r') as f:
		for line in f:
			item = {}
			elms = line.split(';')
			item['href'] = elms[0]
			item['title'] = elms[1]
			item['content'] = ';'.join(elms[2:]).rstrip('\n')
			items.append(item)
	return items

def make_time(items):
	t = CONFIG['start-time']
	for item in items:
		item['published'] = format_date(t)
		item['updated'] = format_date(t)
		t += CONFIG['interval']
	return items

def write_feed(filename, items):
	content = '\n'.join([';'.join((item['href'],
		item['title'],
		item['published'],
		item['updated'],
		item['content'])) for item in items])
	with open(filename, 'w') as f:
		f.write(content)

def main(list_filename, feed_filename):
	items = parse_list(list_filename)
	items = make_time(items)
	write_feed(feed_filename, items)

if __name__ == "__main__":
	import sys
	args = sys.argv[1:]
	if len(args) == 2:
		main(*args)