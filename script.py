# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# ------ This script code by Ibraheem (@ihalloum) and Sumaia (@sumaia-a-k)------ 
# ------ For educational purposes only .                                  ------
# ------------------------------------------------------------------------------

import urllib2
import json
import _mysql
import MySQLdb as mdb

# ------------------------------------------------------------------------------
# --------------------- Edit var below to fit your systeam ---------------------
# ------------------------------------------------------------------------------

# Graph URL check version
graph_url = "https://graph.facebook.com/v2.5/"
# Add the Pages ID
#list_pages = ["345180182174204","63811549237"]
list_pages = [""]
#Access Token = App ID + App Secret
accesstoken=""+"|"+""
#Posts Details want to collect
posts_fields = "message,from,created_time"
#Comments Details want to collect
comments_fields = "message,from,created_time"
# Number of post you want to collect from signal page
fb_post_max = 500
# tha max number of comments you want to collect from signal post
fb_comment_max = 100
# MySQL Server IP
host='127.0.0.1'
# Database UserName
username='root'
# Database Password
password='123'
# Database Name
DBName='fb_data'

# ------------------------------------------------------------------------------
#------------------------ Don't edit after this line ---------------------------
# ------------------------------------------------------------------------------

fb_post_counter = 0
fb_comment_counter = 0
fb_total_post_counter = 0
fb_total_comment_counter = 0
con = mdb.connect(host, username, password, DBName , charset='utf8')
posts_parametrs = "/posts/?fields="+posts_fields+"&access_token="+accesstoken
comments_parametrs = "?fields="+comments_fields+"&access_token="+accesstoken


# Execute Mysql Query ( select , update , insert , delete ----) , we use this function to update next record
def excuteQuery(query):
        try:
                with con:
                        cur = con.cursor(mdb.cursors.DictCursor)
                        tt=cur.execute(query)
                        rows = cur.fetchall()
			return rows
		return []
        except Exception as ex:
                print str(ex)
		return None

# For insert new row , we use this function to insert posts and comments
def insert_row(query , data):
        try:
                with con:
                        cur = con.cursor()
                        tt=cur.execute(query,data)
			return 1
        except Exception as ex:
                print str(ex);
		return -1

# This function update next record in status tables which contains page id and last post page scanned for this page
def update_page_status(page_id,status):
	try:
		statement="INSERT INTO status (pageid,next) VALUES ('"+page_id+"', '"+status+"') ON DUPLICATE KEY UPDATE  next ='"+status+"'"
		excuteQuery(statement)	
	except Exception as ex:
		print str(ex);
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
			add_query=("INSERT INTO comments "
               			"(pageid, postid,commentid,message,fromid,fromname,createdtime) "
               			"VALUES (%s,%s,%s,%s,%s,%s,%s)")
			add_data = (page_id,post_id,comment_id,message,from_id,from_name,created_time)
			insert_row(add_query,add_data)
			global fb_comment_counter
			fb_comment_counter+=1
			comment_num +=1

		except Exception as ex:
			print str(ex)
			pass

# This function store posts which exist in data_url and update last page scanned by update next record in status table
def get_fb_pages_posts( data_url ,page_id):

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
			
			add_query=("INSERT INTO Posts "
               			"(pageid, postid,message,fromid,fromname,createdtime) "
               			"VALUES (%s,%s,%s,%s,%s,%s)")
			add_data = (page_id,post_id,message,from_id,from_name,created_time)
			insert_row(add_query,add_data)
			global fb_post_counter
			fb_post_counter+=1
			get_fb_Post_comment(post_id,page_id)
			
			if fb_post_counter%10==0:
				print "\t"+str(fb_post_counter) +" post is Scaned and "+ str(fb_comment_counter)+ " comments for page "+page_id
		
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

# This function store posts for selected page by execute get_fb_pages_posts() more than one until reach to fb_post_max
def scan_fb_pages(page_id):
	
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
				current_page=get_fb_pages_posts(current_page,page_id)
			else :
				print "\tThe Script Scan all the Posts in this page"+ page_id	
	except Exception as ex:
		print str(ex)
		pass
def main():
	
	for page_id in list_pages :
		global fb_comment_counter
		global fb_post_counter
		fb_comment_counter=0
		fb_post_counter=0
		print "##########################################################################"
		print "Scan Started For Page "+page_id
		scan_fb_pages(page_id)
		print "Scan Finished For Page "+page_id
		print "Total posts = " + str(fb_post_counter)
		print "Total comments = " + str(fb_comment_counter)
		global fb_total_comment_counter
		global fb_total_post_counter
		fb_total_comment_counter+=fb_comment_counter
		fb_total_post_counter+=fb_post_counter
	print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
	print "Script Finished"
	print "Total Scaned Posts =" + str(fb_total_post_counter)
	print "Total Scaned Comments =" + str(fb_total_comment_counter)
main()
