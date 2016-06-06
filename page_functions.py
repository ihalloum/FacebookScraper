# -*- coding: utf-8 -*-

import urllib2
import json


from config import *
from mysql_functions import *


fb_post_counter = 0
fb_comment_counter = 0
fb_reply_counter = 0
fb_like_counter = 0
fb_total_post_counter = 0
fb_total_comment_counter = 0
fb_total_reply_counter = 0
fb_total_like_counter = 0
posts_parametrs = "/posts/?fields="+posts_fields+"&access_token="+accesstoken
comments_parametrs = "?fields="+comments_fields+"&access_token="+accesstoken

# This function update next record in status tables which contains page id and last post page scanned for this page
def update_page_status(page_id,status):
	try:
		statement="INSERT INTO status (pageid,next) VALUES ('"+page_id+"', '"+status+"') ON DUPLICATE KEY UPDATE  next ='"+status+"'"
		excuteQuery(statement)	
	except Exception as ex:
		print str(ex);
                pass

# This function store  likes for  selected posts,comments,replys  in the likes table	
def get_fb_like ( page_id,post_id ,comment_id,reply_id,want_str):
	if (want_str=="post"):
		want_id=post_id
	elif (want_str=="comment"):
		want_id=comment_id
	elif (want_str == "reply"):
		want_id=reply_id
	else :
		print "LIKES FUNCTION want_str Error Value"
		return
		
	current_page = graph_url + want_id + "/likes"  + "?limit=" + str(fb_like_max) +"&access_token="+accesstoken
	web_response = urllib2.urlopen(current_page)
	readable_page = web_response.read()
	json_fbpage = json.loads(readable_page)
	for data in json_fbpage["data"]:
		try :
			
			from_id = data["id"]
			from_name = data["name"]
			add_query=("INSERT INTO likes "
               			"(pageid, postid,commentid,replyid,fromname,fromid) "
               			"VALUES (%s,%s,%s,%s,%s,%s)")
			add_data = (page_id,post_id,comment_id,reply_id,from_name,from_id)
			insert_row(add_query,add_data)
			global fb_like_counter
			fb_like_counter+=1
			
		except Exception as ex:
			print str(ex)
			pass

# This function store  replys for  selected comments (comment_id) in the replys table	
def get_fb_Post_reply ( post_id , page_id ,comment_id):
	
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
			add_data = (page_id,post_id,comment_id,reply_id,message,from_id,from_name,created_time,total_likes)
			insert_row(add_query,add_data)
			global fb_reply_counter
			fb_reply_counter+=1
			reply_num +=1
			if(scrape_like):
				get_fb_like(page_id,post_id ,comment_id,reply_id,"reply")

		except Exception as ex:
			print str(ex)
			pass

# This function store  comments for  selected posts (post_id) in the comments table	
def get_fb_Post_comment ( post_id , page_id ):
	
	current_page = graph_url + post_id + "/comments/" + comments_parametrs + "&limit=" + str(fb_comment_max)
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
			add_data = (page_id,post_id,comment_id,message,from_id,from_name,created_time,total_likes)
			insert_row(add_query,add_data)
			global fb_comment_counter
			fb_comment_counter+=1
			comment_num +=1
			if(scrape_like):
				get_fb_like(page_id,post_id ,comment_id,"NULL","comment")
			if(scrape_reply):
				get_fb_Post_reply(post_id,page_id,comment_id)


		except Exception as ex:
			print str(ex)
			pass

# This function store posts which exist in data_url and update last page scanned by update next record in status table
def get_fb_page_posts( data_url ,page_id):

	current_page = data_url
	web_response = urllib2.urlopen(current_page)
	readable_page = web_response.read()
	json_fbpage = json.loads(readable_page)
	
	for data in json_fbpage["data"]:
		try :
			message = data["message"]
			created_time = data["created_time"]
			post_id = data["id"]
			post_from = data["from"]
			from_name = post_from["name"]
			from_id = post_from["id"]
			likes = data["likes"]
			summary_likes = likes["summary"]
			total_likes= summary_likes["total_count"]
			#print total_likes
			add_query=("INSERT INTO Posts "
               			"(pageid, postid,message,fromid,fromname,createdtime,total_likes) "
               			"VALUES (%s,%s,%s,%s,%s,%s,%s)")
			add_data = (page_id,post_id,message,from_id,from_name,created_time,total_likes)
			insert_row(add_query,add_data)
			global fb_post_counter
			fb_post_counter+=1
			if(scrape_like):
				get_fb_like(page_id,post_id ,"NULL","NULL","post")
			if(scrape_comment):
				get_fb_Post_comment(post_id,page_id)
			
			if fb_post_counter%10==0:
				print "\t"+str(fb_post_counter) +" posts and "+ str(fb_comment_counter)+ " comments and "+str(fb_reply_counter)+" reply and "+str(fb_like_counter)+" like is scanned for page "+page_id
		
		except Exception as ex:
			#print str(ex)
			pass
	
	try :
		fb_paging = json_fbpage["paging"]
		next_post_page = fb_paging["next"]
		update_page_status(page_id,next_post_page)
		return next_post_page
	except Exception as ex:
		return None

# This function store posts for selected page by execute get_fb_page_posts() more than one until reach to fb_post_max
def scan_fb_page(page_id):
	
	try:
		sql="select next from status where pageid='{}'"
		statement=sql.format(page_id)
		rows=excuteQuery(statement)
		if len(rows)  == 0:
			current_page = graph_url + page_id + posts_parametrs
		else :
			current_page = rows[0]['next']
		
		while (fb_post_counter<fb_post_max):
			if current_page != "None":
				current_page=get_fb_page_posts(current_page,page_id)
			else :
				print "\tThe Script Scan all the Posts in this page"+ page_id	
	except Exception as ex:
		print str(ex)
		pass


def scan_fb_pages(scrape_comments,scrape_replys,scrape_likes):
	global scrape_comment
	global scrape_reply
	global scrape_like
	scrape_comment=scrape_comments
	scrape_reply=scrape_replys
	scrape_like=scrape_likes
	for page_id in list_pages :
		global fb_comment_counter
		global fb_post_counter
		global fb_reply_counter
		global fb_like_counter
		fb_comment_counter=0
		fb_post_counter=0
		fb_reply_counter=0
		fb_like_counter=0
		print "########################################################################################################"
		print "Scan Started For Page "+page_id
		scan_fb_page(page_id)
		print "Scan Finished For Page "+page_id
		print "Total posts = " + str(fb_post_counter)
		print "Total comments = " + str(fb_comment_counter)
		print "Total replys = " + str(fb_reply_counter)
		print "Total likes = " + str(fb_like_counter)
		global fb_total_comment_counter
		global fb_total_post_counter
		global fb_total_reply_counter
		global fb_total_like_counter
		fb_total_comment_counter+=fb_comment_counter
		fb_total_post_counter+=fb_post_counter
		fb_total_reply_counter+=fb_reply_counter
		fb_total_like_counter+=fb_like_counter
	print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
	print "Pages Script Finished"
	print "Total Scaned Psges Posts = " + str(fb_total_post_counter)
	print "Total Scaned Psges Comments = " + str(fb_total_comment_counter)
	print "Total Scaned Psges Replys = " + str(fb_total_reply_counter)
	print "Total Scaned Psges likes = " + str(fb_total_like_counter)
