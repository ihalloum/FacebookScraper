# -*- coding: utf-8 -*-

#---------------------------------- Graph Var ---------------------------------------
# Graph URL check version
graph_url = "https://graph.facebook.com/v2.6/"
#Access Token = App ID + App Secret
accesstoken=""+"|"+""

#---------------------------------- MySQL Var ---------------------------------------
# MySQL Server IP
host='127.0.0.1'
# Database UserName
username='root'
# Database Password
password='123'
# Database Name
DBName='fb_data'

#---------------------------------- Pages Var ---------------------------------------
# Add the Pages ID
#list_pages = ["345180182174204","63811549237"]
list_pages = ["63811549237"]
#Posts Details want to collect
posts_fields = "message,likes.limit(1).summary(true),from,created_time"
# Number of posts you want to collect from signal page , min=25
fb_post_max = 3
# Enable Scrape Page
scrape_page = 1
#---------------------------------- Groups Var --------------------------------------
# Add the Groups ID
#list_groups = ["345180182174204","63811549237"]
list_groups = ["1474176602870235"]
#Feeds Details want to collect
feeds_fields = "message,likes.limit(1).summary(true),from,created_time"
# Number of feeds you want to collect from signal group . min=25
fb_feed_max = 3
# Enable Scrape Group
scrape_group = 1
#---------------------------------- Pages & Groups Var ------------------------------
#Comments Details want to collect
comments_fields = "message,likes.limit(1).summary(true),from,created_time"
# tha max number of comments you want to collect from signal post
fb_comment_max = 3
# tha max number of Reply you want to collect from signal comment
fb_reply_max = 3
# Enable Scrape Comment
scrape_comment = 1
# Enable Scrape Reply
scrape_reply = 1
