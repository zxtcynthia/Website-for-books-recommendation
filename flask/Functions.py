from pymongo import MongoClient
import random
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale

import os
import sys
from flask import Flask, request, session, g, redirect, url_for, abort, render_template,redirect,session

from flaskext.mysql import MySQL
from flask_wtf import FlaskForm,Form
from wtforms.fields.html5 import DateField
from wtforms import SelectField, TextField, RadioField
from datetime import date
import time
import gmplot
from Functions import *

import wordcloud
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import io
import string
import matplotlib
from sklearn.preprocessing import scale

Others=['Deals','Libros en espa ol',"Children's",'Mystery, Thriller & Suspense','Teens','on CD']
Religion=['Christian & Bibles','Religion & Spirituality','Self-Help']
Arts_Science=['Computers & Technology','Education & Teaching','Engineering & Transportation','Textbooks','History','Law','Biographies & Memoirs','Textbooks','Science & Math','Reference','Politics & Social Sciences','Arts & Photography','History']
Relaxing=['Comics & Graphic Novels','Humor & Entertainment','Novelty & More','Science Fiction & Fantasy','Literature & Fiction',"Children's"]
relationship=['Gay & Lesbian','Romance','Parenting & Relationships','Teens']
Life=['Cookbooks, Food & Wine','Crafts, Hobbies & Home','Health, Fitness & Dieting','Medical','Sports & Outdoors','Travel','Outdoor D cor','Business & Money']



def category_tuples():
	c=[('','Choose Category'),
	('Science Fiction & Fantasy', 'Science Fiction & Fantasy'),
	('Gay & Lesbian', 'Gay & Lesbian'),
	('on CD', 'on CD'),
	('Libros en espa ol', 'Libros en espa ol'),
	('Literature & Fiction', 'Literature & Fiction'),
	('Science & Math', 'Science & Math'),
	('Comics & Graphic Novels', 'Comics & Graphic Novels'),
	('Textbooks', 'Textbooks'),
	('Reference', 'Reference'),
	('Teens', 'Teens'),
	('Medical', 'Medical'),
	('Christian  & Bibles', 'Christian  & Bibles'),
	("Children's", "Children's"),
	('Law', 'Law'),
	('Cookbooks, Food & Wine', 'Cookbooks, Food & Wine'),
	('Religion & Spirituality', 'Religion & Spirituality'),
	('Health, Fitness & Dieting', 'Health, Fitness & Dieting'),
	('Crafts, Hobbies & Home', 'Crafts, Hobbies & Home'),
	('Biographies & Memoirs', 'Biographies & Memoirs'),
	('Outdoor D cor', 'Outdoor D cor'),
	('Education & Teaching', 'Education & Teaching'),
	('Arts & Photography', 'Arts & Photography'),
	('Politics & Social Sciences', 'Politics & Social Sciences'),
	('Business & Money', 'Business & Money'),
	('Sports & Outdoors', 'Sports & Outdoors'),
	('Engineering & Transportation', 'Engineering & Transportation'),
	('Computers & Technology', 'Computers & Technology'),
	('Deals', 'Deals'),
	('Romance', 'Romance'),
	('Mystery, Thriller & Suspense', 'Mystery, Thriller & Suspense'),
	('History', 'History'),
	('Parenting & Relationships', 'Parenting & Relationships'),
	('Travel', 'Travel'),
	('Humor & Entertainment', 'Humor & Entertainment'),
	('Self-Help', 'Self-Help'),
	('Novelty & More', 'Novelty & More')]
	return c

def language_tuples():
	l=[('','Choose Language'),
	('Italian', 'Italian'),
	('English', 'English'),
	('German', 'German'),
	('Catalan', 'Catalan'),
	('Taiwanese Chinese', 'Taiwanese Chinese'),
	('Spanish', 'Spanish'),
	('Japanese', 'Japanese'),
	('Portuguese Brazilian', 'Portuguese Brazilian'),
	('Greek', 'Greek'),
	('Dutch', 'Dutch'),
	('Latin', 'Latin'),
	('French', 'French'),
	('Old English', 'Old English'),
	('Multilingual', 'Multilingual'),
	('Portuguese', 'Portuguese'),
	('Serbian', 'Serbian'),
	('Chinese', 'Chinese')]
	return l



def database():
	client = MongoClient()
	db = client.Project
	books = db.books 
	return books

def usersbase():
	client = MongoClient()
	db = client.Project
	users = db.users 
	return users

def around(region,users,books):
    string=""
    for i in users.find({'region':region}):
        isbn=i['ISBN'].zfill(10)
        tag=books.find_one({'ISBN':isbn})['tags']
        for j in tag:
            string+=' '+j
    return string

def grey_color_func(word, font_size, position, orientation, random_state=None,**kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(0, 40)


def find_books(user_id):
    from operator import itemgetter
    user_match = pd.read_csv('/Users/zou/Desktop/flask/all_user_match.csv')
    all_isbn = list(user_match[user_match['User.ID'] == user_id]['ISBN'])
    all_id = list()
    for i in range(len(all_isbn)):
        all_id.extend(list(user_match[user_match['ISBN'] == all_isbn[i]]['User.ID']))
    all_isbn_1 = list()
    for j in range(len(all_id)):
        all_isbn_1.extend(list(user_match[user_match['User.ID'] == all_id[j]]['ISBN']))
    unique_isbn = list(set(all_isbn_1))
    if len(unique_isbn) <= 4:
        return unique_isbn
    else:
        find_score = dict()
        order_isbn = list()
        for i in range(len(unique_isbn)):
            find_score[unique_isbn[i]] = (np.sum(user_match[user_match['ISBN'] == unique_isbn[i]]['Book.Rating']))/len(user_match[user_match['ISBN'] == unique_isbn[i]]['Book.Rating'])
        result = sorted(find_score.items(), key = itemgetter(1), reverse = True)
        for item in range(4):
            order_isbn.append(result[item][0])
        return order_isbn


def find_nn(input_isbn):
    user = pd.read_csv('/Users/zou/Desktop/flask/all_user_match.csv')
    data_knn_final = pd.read_csv('/Users/zou/Desktop/flask/data_knn_final.csv')
    user = user.drop('Book.Rating', 1)
    user_1 = data_knn_final[data_knn_final['ISBN'].isin(user['ISBN'])]
    d = pd.merge(user, user_1, on='ISBN')
    data_knn = d.drop(d.columns[2:6], axis=1)
    data_knn_scaled = pd.DataFrame(scale(data_knn.iloc[:, 2:7]), index=data_knn.index, columns=data_knn.columns[2:7])
    d_new = data_knn.drop(data_knn.columns[2:7],axis = 1)
    data_knn_1 = pd.concat([data_knn_scaled,d_new],axis=1,join_axes=[data_knn_scaled.index])
    
    if input_isbn not in list(data_knn['ISBN']): # for the data we have user info, we return k-nn results
        find_index = data_knn_final[data_knn_final['ISBN'] == input_isbn].index
        row_select = pd.DataFrame(data_knn_final.iloc[find_index].iloc[0,10:]).T
        category = row_select.columns[(row_select == 1).iloc[0]][0]
        all_same_cat = data_knn_final[data_knn_final[category] == 1]
        get_ave_score = all_same_cat.sort_values(by = 'Average score', ascending=False)
        index_list = list(get_ave_score.index[0:5])
        ISBN_list = list(get_ave_score.loc[index_list]['ISBN'])
        if input_isbn in ISBN_list:
            ISBN_list.remove(input_isbn)
        else:
        	ISBN_list=ISBN_list[:4]
    else:
        test_x = (pd.DataFrame(data_knn_1[data_knn_1['ISBN'] == input_isbn].iloc[0,:]).T).drop(['User.ID','ISBN'],axis = 1)
        train_x = (data_knn_1[data_knn_1['ISBN'] != input_isbn].iloc[:,:]).drop_duplicates('ISBN')
        train_x_1 = train_x.drop(['User.ID','ISBN'],1)
        d = np.zeros(shape=(len(train_x_1), 1))
        for j in range(len(train_x_1)):
             d[j] = np.sum(abs(test_x.values - train_x_1.values[j, ]))
        distance_df = pd.DataFrame(d)
        distance_df.columns = ['distance']
        distance_sort = pd.DataFrame(distance_df.iloc[:, 0].sort_values(ascending=True))
        index_list = distance_sort.index[0:5]
        data_list = train_x_1.iloc[index_list]
        index_list_1 = data_list.index.values.tolist()
        ISBN_list = list(data_knn_1.iloc[index_list_1]['ISBN'])
        if input_isbn in ISBN_list:
            ISBN_list.remove(input_isbn)
        else:
        	ISBN_list=ISBN_list[:4]
    return ISBN_list


def info(isbn):
	books=database()
	pic='http://images.amazon.com/images/P/'+isbn+'.01.LZZZZZZZ.jpg'
	title = books.find_one({"ISBN":isbn})["Name"]
	author = books.find_one({"ISBN":isbn})["author"]
	rating = books.find_one({"ISBN":isbn})["Ratings"]['average score']
	l=[pic,title,author,rating,isbn]
	return l


def drawwordcloud(sentence,option):
	directory="/Users/zou/Desktop/flask/"
	textfile=directory+'static/textfile'+option+'.txt'
	file = open(textfile,'w')
	file.write(sentence) 
	file.close() 
	dd = os.path.dirname(__file__)
	text = open(os.path.join(dd, textfile)).read()
	STOPWORDS.add("text")
	STOPWORDS.add("book")
	STOPWORDS.add("read")
	if option=='cloud':
		cloudfile=directory+'static/charts/cloud.jpg'
	elif option=='up':
		cloudfile=directory+'static/charts/thumb_up.jpg'
	elif option=='down':
		cloudfile=directory+'static/charts/thumb_down.jpg'
	alice_mask = np.array(Image.open(os.path.join(dd, cloudfile)))
	wordcloud = WordCloud(stopwords=STOPWORDS,mask=alice_mask, background_color='white',width=1200,height=1000).generate(sentence)
	timestring=str(int(time.time()))
	figurename = directory+'static/charts/figure_'+option+timestring+".png"
	fff='../static/charts/figure_'+option+timestring+".png"
	wordcloud.recolor(color_func=grey_color_func, random_state=8).to_file(figurename)
	return fff