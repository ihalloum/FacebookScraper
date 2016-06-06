# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# ------ This script coded by Sumaia (@sumaia-a-k) and Ibraheem (@ihalloum)-----
# ------ For educational purposes only .                                   -----
# ------------------------------------------------------------------------------

import urllib2
import json
import _mysql
import MySQLdb as mdb

import sys

from page_functions import *
from group_functions import *

def main():
	if ( len(sys.argv) == 6):

		scrape_pages=sys.argv[1]
		scrape_groups=sys.argv[2]
		scrape_comments=sys.argv[3]
		scrape_replys=sys.argv[4]
		scrape_likes=sys.argv[5]
		
		if ( scrape_pages.startswith("ScrapePage=") and scrape_groups.startswith("ScrapeGroup=") and scrape_comments.startswith("ScrapeComment=") and scrape_replys.startswith("ScrapeReply=")and scrape_likes.startswith("ScrapeLike=")  ) :
			
			if ( (scrape_pages.endswith("=Y") or scrape_pages.endswith("=N") ) and (scrape_groups.endswith("=Y") or scrape_groups.endswith("=N") ) and (scrape_comments.endswith("=Y") or scrape_comments.endswith("=N") ) and (scrape_replys.endswith("=Y") or scrape_replys.endswith("=N") ) and (scrape_likes.endswith("=Y") or scrape_likes.endswith("=N") ) ) :
				
				if (scrape_pages.endswith("=Y")) :
					scrape_page = 1
				else :
					scrape_page = 0
				
				if (scrape_groups.endswith("=Y")) :
					scrape_group = 1
				else :
					scrape_group = 0
		
				if (scrape_comments.endswith("=Y")) :
					scrape_comment = 1
				else :
					scrape_comment = 0

				if (scrape_replys.endswith("=Y")) :
					scrape_reply = 1
				else :
					scrape_reply = 0
				
				if (scrape_likes.endswith("=Y")) :
					scrape_like = 1
				else :
					scrape_like = 0
				
				if (scrape_page):
					scan_fb_pages(scrape_comment,scrape_reply,scrape_like)
				if (scrape_group):					
					scan_fb_groups(scrape_comment,scrape_reply,scrape_like)
				
			else :
				print "Bad Script Excute , make sure you write Value right"
				print "EX: python -W ignore "+sys.argv[0]+ " ScrapePage=Y ScrapeGroup=Y ScrapeComment=Y ScrapeReply=Y ScrapeLike=Y"
		else :
			print "Bad Script Excute , make sure you write Vars right"
			print "EX: python -W ignore "+sys.argv[0]+ " ScrapePage=Y ScrapeGroup=Y ScrapeComment=Y ScrapeReply=Y ScrapeLike=Y"
	else :
		print "Bad Script Excute , make sure you pass four Vars"
		print "EX: python -W ignore "+sys.argv[0]+ " ScrapePage=Y ScrapeGroup=Y ScrapeComment=Y ScrapeReply=Y ScrapeLike=Y"
main()
