import os
import sys
from flask import Flask, request, session, g, redirect, url_for, abort, render_template,redirect,session
import random
from flaskext.mysql import MySQL
from flask_wtf import FlaskForm,Form
from wtforms.fields.html5 import DateField
from wtforms import SelectField, TextField, RadioField
from datetime import date
import time
import gmplot
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale
from Functions import *

import wordcloud
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import io
import string
import matplotlib


category_tuple=category_tuples()
language_tuple=language_tuples()
#user_match = pd.read_csv(directory+'all_user_match.csv')
directory="/Users/zou/Desktop/flask/"

app = Flask(__name__)

app.secret_key = 'A0Zr98slkjdf984jnflskj_sdkfjhT'

class SearchForm(FlaskForm):
	keyword = TextField('keyword')
	category = SelectField('category', choices=category_tuple)
	language = SelectField('language', choices=language_tuple)
	userID = TextField('userID')

class MapForm(FlaskForm):
	location=SelectField('location',choices=[('','Region'),('MidEast','MidEast'),('NouthEast','NouthEast'),('SouthEast','SouthEast'),('West','West'),('SouthWest','SouthWest')])

class recommendForm(FlaskForm):
	style_choice = RadioField('style_choice', choices=[('p1', 'Art and Science'), ('p2', 'Faith'), ('p3', 'Relationship'), ('p4', 'Relaxing'), ('p5', 'Life'), ('p6', 'Others')])

class booklistForm(FlaskForm):
	book_choice = RadioField('book_choice', choices=[('b1', 'I Want This'), ('b2', 'I Want This'), ('b3', 'I Want This'), ('b4', 'I Want This'), ('b5', 'I Want This'), ('b6', 'I Want This'), ('b7', 'I Want This'), ('b8', 'I Want This')])

class booklistForm0(FlaskForm):
	book_choice = RadioField('book_choice', choices=[('b1', 'I Want This')])

class infoForm(FlaskForm):
	book_choice = RadioField('book_choice', choices=[('b1', 'I Want This'), ('b2', 'I Want This'), ('b3', 'I Want This'), ('b4', 'I Want This')])


@app.route("/")
@app.route("/homepage/")
def homepage():
	return render_template('homepage.html')

@app.route("/error/")
def error():
	return render_template('error.html')

@app.route("/userheatmap/")
def userheatmap():
	return render_template('userheatmap.html')

@app.route("/bokehplots/")
def bokehplots():
	return render_template('bokehplots.html')


@app.route("/info/<infokey>",methods=['GET','POST'])
def info(infokey):
	form=infoForm()
	books=database()
	ISBN_list=find_nn(infokey)
	knn_info=[]
	knn_pics=[]
	for isbn in ISBN_list:
		knn_info.append(books.find_one({'ISBN':isbn}))
		knn_pics.append('http://images.amazon.com/images/P/'+isbn+'.01.LZZZZZZZ.jpg')
	this_detail=books.find_one({"ISBN":infokey})
	this_pic='http://images.amazon.com/images/P/'+infokey+'.01.LZZZZZZZ.jpg'
	a=this_detail["Introduction"]
	intro_url=drawwordcloud(a,'cloud')
	l=float(this_detail["Ratings"]['average score'])
	star=this_detail["Stars"]
	if star:
		stars=[]
		for k,v in star.items():
			stars.append(v)
		stars
		hh=str(stars)
		if l<2.5:
			rat_url=drawwordcloud(hh,'down')
		else:
			rat_url=drawwordcloud(hh,'up')
	
	if form.validate_on_submit():
		book_choice = request.form.get('book_choice')
		rank=int(book_choice[-1])-1
		infokey2=knn_info[rank]['ISBN']
		return redirect(url_for('info',infokey=infokey2))
	return render_template('info.html',form=form,book_choice=list(form.book_choice),this_detail=this_detail,this_pic=this_pic,knn_pics=knn_pics,knn_info=knn_info,rat_url=rat_url,intro_url=intro_url)


@app.route("/recommendation/",methods=['GET','POST'])
def recommendation():
	form = recommendForm()
	books=database()
	pic1=['images/Knowledge.jpg', 'images/Faith.jpg', 'images/Relationship.jpg']
	pic2=['images/Relaxing.jpg', 'images/Life.jpg', 'images/Other.jpg']
	if form.validate_on_submit():
		style_choice = request.form.get('style_choice')
		if style_choice=='p1':
			categorylist=['Computers & Technology','Education & Teaching','Engineering & Transportation','Textbooks','History','Law','Biographies & Memoirs','Textbooks','Science & Math','Reference','Politics & Social Sciences','Arts & Photography','History']
		elif style_choice=='p2':
			categorylist=['Christian  & Bibles','Religion & Spirituality','Self-Help']
		elif style_choice=='p3':
			categorylist=['Gay & Lesbian','Romance','Parenting & Relationships','Teens']
		elif style_choice=='p4':
			categorylist=['Comics & Graphic Novels','Humor & Entertainment','Novelty & More','Science Fiction & Fantasy','Literature & Fiction',"Children's"]
		elif style_choice=='p5':
			categorylist=['Cookbooks, Food & Wine','Crafts, Hobbies & Home','Health, Fitness & Dieting','Medical','Sports & Outdoors','Travel','Outdoor D cor','Business & Money']
		else:
			categorylist=['Deals','Libros en espa ol',"Children's",'Mystery, Thriller & Suspense','Teens','on CD',]
		staff=[]
		for c in categorylist:
			for item in books.find({'category':c}):
				staff.append(item)
		randnum=np.random.randint(low=0, high=len(staff))
		infokey=staff[randnum]['ISBN']
		return redirect(url_for('info',infokey=infokey))
	return render_template('recommendation.html', form=form, styles=list(form.style_choice), pic1=pic1, pic2=pic2)

@app.route("/user0/<userID>",methods=['GET','POST'])
def user0(userID):
	form=infoForm()
	books=database()
	userID=np.int64(userID)
	isbnlist=find_books(userID)
	l=[]
	pic=[]
	for isbn in isbnlist:
		l.append(books.find_one({"ISBN":isbn}))
		pic.append('http://images.amazon.com/images/P/'+isbn+'.01.LZZZZZZZ.jpg')
	if form.validate_on_submit():
		book_choice = request.form.get('book_choice')
		rank=int(book_choice[-1])-1
		infokey=l[rank]['ISBN']
		return redirect(url_for('info',infokey=infokey))
	return render_template('user0.html',l=l,pic=pic,form=form,book_choice=list(form.book_choice))


@app.route("/user1/",methods=['GET','POST'])
def user1():
	form=MapForm()
	users=usersbase()
	books=database()
	if form.validate_on_submit():
		location = request.form.get('location')
		if location:
			string_=around(location,users,books)
			file = open(directory+'static/testlocation.txt','w')
			file.write(string_) 
			file.close() 
			dd = os.path.dirname(__file__)
			text = open(os.path.join(dd, directory+'static/testlocation.txt')).read()
			STOPWORDS.add("text")
			STOPWORDS.add("book")
			alice_mask = np.array(Image.open(os.path.join(dd, directory+"static/charts/cloud.jpg")))
			wordcloud = WordCloud(stopwords=STOPWORDS,mask=alice_mask, background_color='white',width=1000,height=850).generate(string_)
			timestring=str(int(time.time()))
			filename = directory+'static/charts/location_figure_'+timestring+".png"
			wordcloud.to_file(filename)
			fff='../static/charts/location_figure_'+timestring+".png"
			return render_template('user2.html',chart_src=fff)
	return render_template('user1.html',form=form)


@app.route("/search/",methods=['GET','POST'])
def search():
	form=SearchForm(request.form)
	if request.method =="POST":
		keyword=form.keyword.data
		category=form.category.data
		language=form.language.data
		userID=form.userID.data
		books=database()
		isbn=[]
		author=[]
		rating=[]
		name=[]
		for bbb in books.find():
			isbn.append(bbb["ISBN"])
			author.append(bbb['author'])
			rating.append(bbb['Ratings'])
			name.append(bbb['Name'])
		if keyword:
			if keyword in isbn:
				key=keyword
				return redirect(url_for('book_title',key=key))
			
			elif keyword in author:
				key=books.find_one({"author":keyword})["ISBN"]
				return redirect(url_for('book_title',key=key))
			elif keyword in name:
				key=books.find_one({"Name":keyword})["ISBN"]
				return redirect(url_for('book_title',key=key))
			else:
				return render_template('error.html')
		if category and language:
			t=category+'_'+language
			return redirect(url_for('book_title2',t=t))
		elif category:
			return redirect(url_for('book_title2',t=category))#x=x,y=y,z=z,w=w,u=u)
		elif language:
			return redirect(url_for('book_title2',t=language))#x=x,y=y,z=z,w=w,u=u)
		if userID:
			return redirect(url_for('user0',userID=userID))

	return render_template('search.html',form=form)			

@app.route("/booklist2/<t>/",methods=['GET','POST'])
def book_title2(t):
	category=[]
	language=[]
	books=database()
	for bbb in books.find():
		category.append(bbb["category"])
		language.append(bbb['language'])
	info=[]
	pics=[]
	count=0
	if t.split('_')[0] in category and t.split('_')[-1] in language:
		for i in books.find({'category':t.split('_')[0],'language':t.split('_')[-1]}):
			info.append(i)
			pics.append('http://images.amazon.com/images/P/'+i['ISBN']+'.01.LZZZZZZZ.jpg')
			count+=1
			if count ==8:
				break
	elif t in category:
		for i in books.find({'category':t}):
			info.append(i)
			pics.append('http://images.amazon.com/images/P/'+i['ISBN']+'.01.LZZZZZZZ.jpg')
			count+=1
			if count ==8:
				break
	elif t in language:
		for i in books.find({'language':t}):
			info.append(i)
			pics.append('http://images.amazon.com/images/P/'+i['ISBN']+'.01.LZZZZZZZ.jpg')
			count+=1
			if count ==8:
				break
	else:
		return render_template('error.html')
	form = booklistForm()
	if form.validate_on_submit():
		book_choice = request.form.get('book_choice')
		rank=int(book_choice[-1])-1
		infokey=info[rank]['ISBN']
		return redirect(url_for('info',infokey=infokey))
	return render_template('booklist2.html',info=info,pics=pics,form=form,book_choice=list(form.book_choice))

@app.route("/booklist1/<key>",methods=['GET','POST'])
def book_title(key):
	books=database()
	this_detail=books.find_one({"ISBN":key})
	this_pic='http://images.amazon.com/images/P/'+key+'.01.LZZZZZZZ.jpg'
	form = booklistForm0()
	if form.validate_on_submit():
		infokey=key
		return redirect(url_for('info',infokey=infokey))
	return render_template('booklist1.html',this_detail=this_detail,this_pic=this_pic,form=form,book_choice=list(form.book_choice))


if __name__ == "__main__":
    app.run(debug = True)

