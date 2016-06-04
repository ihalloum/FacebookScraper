# -*- coding: utf-8 -*-

import urllib2
import json


from config import *
from mysql_functions import *


fb_feed_counter = 0
fb_comment_counter = 0
fb_reply_counter = 0
fb_total_feed_counter = 0
fb_total_comment_counter = 0
fb_total_reply_counter = 0
feeds_parametrs = "/feed/?fields="+feeds_fields+"&access_token="+accesstoken
comments_parametrs = "?fields="+comments_fields+"&access_token="+accesstoken

# This function update next record in status tables which contains group id and last feed page scanned for this group
def update_group_status(group_id,status):
	try:
		statement="INSERT INTO status (pageid,next) VALUES ('"+group_id+"', '"+status+"') ON DUPLICATE KEY UPDATE  next ='"+status+"'"
		excuteQuery(statement)	
	except Exception as ex:
		print str(ex);
                pass

# This function store  replys for  selected comments (comment_id) in the replys table	
def get_fb_Feed_reply ( feed_id , group_id ,comment_id):
	
	current_page = graph_url + comment_id + "/comments/" + comments_parametrs + "&limit=" + str(fb_reply_max)
	web_response = urllib2.urlopen(current_page)
	readable_page = web_response.read()
	json_fbpage = json.loads(readable_page)
	reply_num = 0
	for data in json_fbpage["data"]:
		try :
			message = data["message"].encode('utf8')
			created_time = data["created_time"]
			reply_id = data["id"]
			reply_from = data["from"]
			from_name = reply_from["name"]
			from_id = reply_from["id"]
			likes = data["likes"]
			summary_likes = likes["summary"]
			total_likes= summary_likes["total_count"]
			add_query=("INSERT INTO replys "
               			"(pageid, postid,commentid,replyid,message,fromid,fromname,createdtime,total_likes) "
               			"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
			add_data = (group_id,feed_id,comment_id,reply_id,message,from_id,from_name,created_time,total_likes)
			insert_row(add_query,add_data)
			global fb_reply_counter
			fb_reply_counter+=1
			reply_num +=1

		except Exception as ex:
			print str(ex)
			pass

# This function store  comments for  selected feed (feed_id) in the comments table	
def get_fb_Feed_comment ( feed_id , group_id ):
	
	current_page = graph_url + feed_id + "/comments/" + comments_parametrs + "&limit=" + str(fb_comment_max)
	web_response = urllib2.urlopen(current_page)
	readable_page = web_response.read()
	json_fbpage = json.loads(readable_page)
	comment_num = 0
	for data in json_fbpage["data"]:
		try :
			message = data["message"].encode('utf8')
			created_time = data["created_time"]
			comment_id = data["id"]
			comment_from = data["from"]
			from_name = comment_from["name"]
			from_id = comment_from["id"]
			likes = data["likes"]
			summary_likes = likes["summary"]
			total_likes= summary_likes["total_count"]
			add_query=("INSERT INTO comments "
               			"(pageid, postid,commentid,message,fromid,fromname,createdtime,total_likes) "
               			"VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
			add_data = (group_id,feed_id,comment_id,message,from_id,from_name,created_time,total_likes)
			insert_row(add_query,add_data)
			global fb_comment_counter
			fb_comment_counter+=1
			comment_num +=1
			if(scrape_reply):
				get_fb_Feed_reply(feed_id,group_id,comment_id)


		except Exception as ex:
			print str(ex)
			pass

# This function store feeds which exist in data_url and update last group scanned by update next record in status table
def get_fb_group_feeds( data_url ,group_id):

	current_page = data_url
	web_response = urllib2.urlopen(current_page)
	readable_page = web_response.read()
	json_fbpage = json.loads(readable_page)
	
	for data in json_fbpage["data"]:
		try :
			message = data["message"]
			created_time = data["created_time"]
			feed_id = data["id"]
			feed_from = data["from"]
			from_name = feed_from["name"]
			from_id = feed_from["id"]
			likes = data["likes"]
			summary_likes = likes["summary"]
			total_likes= summary_likes["total_count"]
			add_query=("INSERT INTO Posts "
               			"(pageid, postid,message,fromid,fromname,createdtime,total_likes) "
               			"VALUES (%s,%s,%s,%s,%s,%s,%s)")
			add_data = (group_id,feed_id,message,from_id,from_name,created_time,total_likes)
			insert_row(add_query,add_data)
			global fb_feed_counter
			fb_feed_counter+=1
			if(scrape_comment):
				get_fb_Feed_comment(feed_id,group_id)
			
			if fb_feed_counter%10==0:
				print "\t"+str(fb_feed_counter) +" feeds and "+ str(fb_comment_counter)+ " comments and "+str(fb_reply_counter)+" Reply is scanned for group "+group_id
		
		except Exception as ex:
			#print str(ex)
			pass
	
	try :
		fb_paging = json_fbpage["paging"]
		next_group_page = fb_paging["next"]
		update_group_status(group_id,next_group_page)
		return next_group_page
	except Exception as ex:
		return None

# This function store feeds for selected group by execute get_fb_group_feeds() more than one until reach to fb_feed_max
def scan_fb_group(group_id):
	
	try:
		sql="select next from status where pageid='{}'"
		statement=sql.format(group_id)
		rows=excuteQuery(statement)
		if len(rows)  == 0:
			current_page = graph_url + group_id + feeds_parametrs
		else :
			current_page = rows[0]['next']
		
		while (fb_feed_counter<fb_feed_max):
			if current_page != "None":
				current_page=get_fb_group_feeds(current_page,group_id)
			else :
				print "\tThe Script Scan all the Feeds in this page"+ group_id	
	except Exception as ex:
		print str(ex)
		pass


def scan_fb_groups(scrape_comments,scrape_replys):
	global scrape_comment
	global scrape_reply
	scrape_comment=scrape_comments
	scrape_reply=scrape_replys
	for group_id in list_groups :
		global fb_comment_counter
		global fb_feed_counter
		global fb_reply_counter
		fb_comment_counter=0
		fb_feed_counter=0
		fb_reply_counter=0
		print "###############################################################################"
		print "Scan Started For Group "+group_id
		scan_fb_group(group_id)
		print "Scan Finished For Group "+group_id
		print "Total feeds = " + str(fb_feed_counter)
		print "Total comments = " + str(fb_comment_counter)
		print "Total replys = " + str(fb_reply_counter)
		global fb_total_comment_counter
		global fb_total_feed_counter
		global fb_total_reply_counter
		fb_total_comment_counter+=fb_comment_counter
		fb_total_feed_counter+=fb_feed_counter
		fb_total_reply_counter+=fb_reply_counter
	print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
	print "Script Finished"
	print "Total Scaned Feeds = " + str(fb_total_feed_counter)
	print "Total Scaned Comments = " + str(fb_total_comment_counter)
	print "Total Scaned Replys = " + str(fb_total_reply_counter)
