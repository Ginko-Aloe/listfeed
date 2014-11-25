#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Generate atom feed from csv file.
Publish only items whose updated datetime are in past."""

# Author : Ginko
# Date : 25/11/2014
# Version : 0.1.f
# License : zlib/libpng

# The zlib/libpng License

# Copyright (c) 2014 Ginko Aloe - ginkobox.fr

# This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.
# Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:
#     1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
#     2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
#     3. This notice may not be removed or altered from any source distribution.

# --* Roadmap *--
# Convert it into a cgi script => 0.1.b
# Make it able to handle several feeds => 0.1.c
# Build a cache function ? (have to be find out, maybe caching should be handled by the webserver) => 0.1.d
# Organize files (data, cache) => 0.1.e
# Cleanup code (especially HEADER), comment code => 0.1.f
# Push on github
# Make documentation
# Advertise

import functools, datetime, cgi, cgitb, os, re
from ConfigParser import SafeConfigParser

HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<feed xml:lang="{lang}" xmlns="http://www.w3.org/2005/Atom">
  <id>tag:linuxfr.org,2005:/news</id>
  <link rel="alternate" type="text/html" href="{alt-url}"/>
  <link rel="self" type="application/atom+xml" href="{self-url}"/>
  <title>{title}</title>
  <icon>/favicon.png</icon>"""

FOOTER = """</feed>"""

CONFIG = {
	'debug': 'OFF', # ON/OFF
	'time-format': '%Y-%m-%dT%H:%M:%S',
	'data-folder': 'data',
	'cache-folder': 'cache',
}

http_header_time_format = "%a, %d %b %Y %H:%M:%S %Z"

NOW = datetime.datetime.now()

def tag(tagname):
	"""Decorator that enclose string content returned by decorated function between HTML tags"""
	def wrapped(func):
		@functools.wraps(func)
		def decorated_func(*args, **kwargs):
			result = []
			result.append(''.join(('<', tagname, '>')))
			result += func(*args, **kwargs)
			result.append(''.join(('</', tagname, '>')))
			return ''.join(result)
		return decorated_func
	return wrapped

def format_date(time):
	return str(time.strftime(CONFIG['time-format']))

def now():
	return format_date(datetime.datetime.now())

def parse_time(raw):
	""""""
	return datetime.datetime.strptime(raw, CONFIG['time-format'])

@tag('published')
def build_published(time):
	return [time]

@tag('updated')
def build_updated(time):
	return [time]

def build_link(item):
	return ''.join(('<link rel="alternate" type="text/html" href="', item['href'], '"/>'))

@tag('title')
def build_title(item):
	return [item['title']]

@tag('content')
def build_content(item):
	return [item['content']]

def build_header(feed_conf):
	return HEADER.format(**feed_conf)

@tag('entry')
def build_entry(item):
	result = []
	result.append(build_published(format_date(item['published'])))
	result.append(build_updated(format_date(item['updated'])))
	result.append(build_link(item))
	result.append(build_title(item))
	result.append(build_content(item))
	return result

def older_than_now(item):
	"""Filter function"""
	return item['updated'] < NOW

def write_feed(filename, content):
	with open(filename, 'w') as f:
		f.write(content)

def serve_feed(content, expires):
	"""Print content to stdout prepended by HTTP headers"""
	print "Content-Type: text/html;charset=utf-8"
	if expires:
		print "Expires: %s" % (expires.strftime(http_header_time_format))
	print
	print(content)

def serve_error(status, message):
	"""Serve with HTTP status header"""
	# Some server seem to dislike that the cgi specifies any HTTP status
	# Uncomment next line to set error HTTP status
	# print 'Status: {}'.format(status)
	print "Content-Type: text/html;charset=utf-8"
	print
	print status, message

class Feed():
	def __init__(self, feed_name):
		self.name = feed_name
		# ListFeed expects these files to be named this way :
		# data/feed.ini
		# data/feed.csv
		self.cfg_name = '{folder}/{name}.ini'.format(name=self.name, folder=CONFIG['data-folder'])
		self.list_name = '{folder}/{name}.csv'.format(name=self.name, folder=CONFIG['data-folder'])
		self.get_cache() # Look for valid cache before trying to generate a brand new one
		if not hasattr(self, 'content'):
			self.find_feed_files()
			self.read_feed_config()
			self.parse_list()
			self.build_feed()

	def get_cache(self):
		"""Looks for cache file for this feed, check expiration date and cleanup files"""
		pat = re.compile(r'{name}_(\d+)\.xml'.format(name=self.name))
		files = os.listdir(os.path.join(os.getcwd(), CONFIG['cache-folder']))
		this_feed_cache_files = filter(lambda x: pat.match(x), files)
		if this_feed_cache_files:
			# Get last file
			this_feed_cache_files.sort()
			last = this_feed_cache_files[-1]
			expiration_date = datetime.datetime.fromtimestamp(float(pat.match(last).group(1)))
			# Check for validity
			if expiration_date > NOW:
				with open("{folder}/{last}".format(folder=CONFIG['cache-folder'], last=last), 'r') as f:
					self.content = ''.join(f.readlines())
					self.expires = expiration_date
				this_feed_cache_files.pop(-1)
			# Clean up
			for f in this_feed_cache_files:
				os.remove("{folder}/{f}".format(folder=CONFIG['cache-folder'], f=f))



	def find_feed_files(self):
		"""Check that feed files are present before going further"""
		for filename in (self.cfg_name, self.list_name):
			with open(filename, 'r') as f:
				pass

	def read_feed_config(self):
		"""Read feed configuration file"""
		parser = SafeConfigParser()
		parser.read(self.cfg_name)
		self.conf = {}
		for item in parser.items('feed'):
			if item[0] == 'max_item':
				self.conf[item[0]] = int(item[1])
			else:
				self.conf[item[0]] = item[1]

	def parse_list(self):
		"""Extract data from csv file"""
		self.items = []
		with open(self.list_name, 'r') as f:
			for line in f:
				item = {}
				elms = line.split(';')
				item['href'] = elms[0]
				item['title'] = elms[1]
				item['published'] = parse_time(elms[2])
				item['updated'] = parse_time(elms[3])
				item['content'] = ';'.join(elms[4:]).rstrip('\n')
				self.items.append(item)

	def get_items(self):
		"""Returns only items whose updated dates are in the past and do the work
		to grab the expiration date from the updated date of the next item"""
		filtered = filter(older_than_now, self.items)
		last = filtered[-1]
		try:
			self.expires = self.items[self.items.index(last)+1]['updated']
		except:
			pass
		return filtered

	def build_feed(self):
		"""Build ATOM feed content"""
		out = []
		out.append(build_header(self.conf))
		out.append(build_updated(now()))
		for item in self.get_items()[-self.conf['max_item']:]:
			out.append(build_entry(item))
		out.append(FOOTER)
		self.content = ''.join(out)

	def write_cache(self):
		"""Write cache file on server"""
		cache_filename = "{folder}/{name}_{timestamp}.xml".format(
			name=self.name, timestamp=self.expires.strftime('%s'), folder=CONFIG['cache-folder']
			)
		write_feed(cache_filename, self.content)

	def serve(self):
		self.write_cache()
		serve_feed(self.content, self.expires)

def main():
	"""Get requested feed from GET parameter and serve if found"""
	form = cgi.FieldStorage() 

	# Get data from fields
	if form.getvalue('feed'):
		feed_name = form.getvalue('feed')
		try:
			feed = Feed(feed_name)
			feed.serve()
		except IOError: # Feed files were not found
			serve_error('404 Not Found', 'Feed files missing')
	else:
		serve_error('404 Not Found', 'No feed parameter')


if CONFIG['debug'] == 'ON':
	# cgitb displays the python trace to the open world. Enable only when required!
	cgitb.enable()
	try:
		main()
	except:
		cgitb.handler()
else:
	main()