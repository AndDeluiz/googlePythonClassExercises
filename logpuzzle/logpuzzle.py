#!/usr/bin/python -tt
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

import os
import re
import sys
import urllib

"""Logpuzzle exercise
Given an apache logfile, find the puzzle urls and download the images.

Here's what a puzzle url looks like:
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"
"""

def sortUrl(url):
  """Return second wordchar (yyyy) as key for sorting if pattern "-xxxx-yyyy.zzz" is present.
  Otherwise returns url."""
  match = re.search(r'-(\w+)-(\w+)\.\w+', url)
  if match:
    return match.group(2)
  else:
    return url

def read_urls(filename):
  """Returns a list of the puzzle urls from the given log file,
  extracting the hostname from the filename itself.
  Screens out duplicate urls and returns the urls sorted into
  increasing order."""

  try:
    fpInputLogFile = open(filename, 'rU')
    strText = fpInputLogFile.read()
  except IOError:
    print >> sys.stderr, "ERROR: file %s doesn't exist or doesn't have read permission!" % filename
    fpInputLogFile.close()
    sys.exit(1)

  # Extracts domain from file name
  strWebsite = 'http://' + filename.split('_')[1]

  dictUrl = {}
  # Search for URL image string inside file. findall() loads entire file at once.
  for tuple in re.findall("GET (\S+)", strText):
    if 'puzzle' in tuple:
      dictUrl[strWebsite + tuple] = 1

  fpInputLogFile.close()
  return sorted(dictUrl.keys(), key=sortUrl)
  
def download_images(img_urls, dest_dir):
  """Given the urls already in the correct order, downloads
  each image into the given directory.
  Gives the images local filenames img0, img1, and so on.
  Creates an index.html in the directory
  with an img tag to show each local image file.
  Creates the directory if necessary.
  """

  # Check if dest_dir exists and creates if not
  if not os.access(dest_dir, os.F_OK):
    os.makedirs(dest_dir)

  # Retrieve images and copy to dest_dir
  intIndex = 0
  listImgFile = []
  for strImgUrl in img_urls:
    sys.stdout.write("Retieving " + strImgUrl + " to " + dest_dir + "/img" + str(intIndex) + " ...")
    try:
      urllib.urlretrieve(strImgUrl, dest_dir + "/img" + str(intIndex))
      listImgFile.append('img' + str(intIndex))
      sys.stdout.write("OK\n")
    except IOError:
      sys.stdout.write("FAIL\n")
    intIndex = intIndex + 1

  # Create index.html file in the directory specified by dest_dir
  strFileName = dest_dir + "/index.html"
  strImageRef = ''
  try:
    fpIndexHtml = open(strFileName, 'w')
    fpIndexHtml.write("<verbatim>\n<html>\n<body>)\n")
    for strFile in listImgFile:
      strImageRef = strImageRef + '<img src="' + strFile + '">'
    fpIndexHtml.write(strImageRef + '\n')
    fpIndexHtml.write("</html>\n</body>)\n")
    fpIndexHtml.close()
  except IOError:
    sys.stderr.write("ERROR: Error writing to " + strFileName + " file!")

def main():
  args = sys.argv[1:]

  if not args:
    print 'usage: [--todir dir] logfile '
    sys.exit(1)

  todir = ''
  if args[0] == '--todir':
    todir = args[1]
    del args[0:2]

  img_urls = read_urls(args[0])

  if todir:
    download_images(img_urls, todir)
  else:
    print '\n'.join(img_urls)

if __name__ == '__main__':
  main()
