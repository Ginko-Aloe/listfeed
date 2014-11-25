ListFeed
========

Make a feed from any list

ListFeed is a python cgi script capable of dynamically generating a feed (Atom) from a simple list file (csv).

It's built with simplicity in mind (KISS principle - Keep It Simple Stupid).

What ListFeed can do
====================
* Generate Atom feed from a (simple) csv list you have built
* Handle multiple feeds
* Publish new items with an interval of your choice
* Use a caching system to save server resource

What ListFeed can't do
======================
* Run on a server with no Python cgi capabilites (if someone wants to port ListFeed to PHP, I'd be glad to display a link to his project right here)
* Build automagically the csv file list for you (there are some proprietary web services that pretend to be able to do that, you should try them because ListFeed will stay KISS: magic is complex and complex is not KISS)

Getting started
===============

1. Grab or constitute the list you want to generate the feed from. Each entry must have following items separated by semi-colons:
  * The link to the object
  * A title
  * A description (it can contain semi-colons)

2. Use genfeed.py to calculate publication dates for each entry.
  ```bash
python genfeed.py mylist.csv yourfeed.csv
  ```
  where mylist.csv is the list you created (with 3 columns) and yourfeed.csv is the new csv file generated with publication dates (five columns).

  NB: the name of the file ("yourfeed" in the previous example) will be the name under which this feed will be accessible.

3. Create an ini file like the following one, named yourfeed.ini:

  ```ini
[feed]
max_item = 10
lang = en-US
alt-url = http://yourserver.com/listfeed.py?feed=yourfeed
self-url = http://yourserver.com/listfeed.py?feed=yourfeed
title =  My own personal feed.
  ```
4. Adapt the values to your own taste.

5. On your websever:
  * Put listfeed.py on your server. (chmod it to 704 to let the webserver execute it; some webserver might require you to rename it listfeed.cgi)
  * Create the directories data and cache in the same directory.
  * Put yourfeed.csv and yourfeed.ini in the data directory you've just created.

6. Add your new feed http://yourserver.com/listfeed.py?feed=yourfeed to your favorite feed reader.

7. Enjoy!

License
=======

ListFeed is distributed under the zlib/libpng License:

Copyright (c) 2014 Ginko Aloe - ginkobox.fr

This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
