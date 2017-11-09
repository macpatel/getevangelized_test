from flask import Flask, url_for, render_template, request, redirect, session, json, jsonify
import requests as HTTPRequest
import config
from pprint import pprint
import re
from bs4 import BeautifulSoup
from math import ceil

#flask forms
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class RegisterInstagramUserForm(FlaskForm):
    class Meta:
        csrf=False
    insta_handle = StringField('Instagram Handle', validators=[DataRequired("Instagram Handle is Required.")])

#mongodb
from mongoengine import *
pprint(connect('getevangelized'))


class Users(Document):
    username = StringField(required=True,unique=True)
    name = StringField()
    bio = StringField()
    profile_image_url = StringField()
    website =StringField()
    followed_by_count=IntField()
    following_count=IntField()
    access_token=StringField()
    meta = {'indexes': [
        {'fields': ['$username', '$name', "$bio"],
         'default_language': 'english',
         'weights': {'username': 1, 'name': 2, 'bio': 10}
        }
    ]}

app = Flask(__name__)

#Flask, render_template, flash, redirect, url_for, session, logging
#passlib
#flask-wtf
#flask-mysqldb
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register')
def register():
    return render_template('register.html', form=RegisterInstagramUserForm())

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/connect/instagram')
def redirectToInstagramOAuth():
    return redirect(config.INSTA_AUTH_URL)

@app.route('/save_instagram_user', methods=["POST"])
def saveInstagramUser():
    form = RegisterInstagramUserForm()
    if request.method == "POST" and form.validate_on_submit():
        pprint(request.form['insta_handle'])
        insta_handle = request.form['insta_handle']
        #first check if the access token is not present in the db then generate new one
        #else get the user data from the existing access token
        #
        #if 
        user_profile_url = config.INSTAGRAM_URL + insta_handle + '/?__a=1'
        resp = HTTPRequest.get(user_profile_url)
        if resp.status_code == 200:
            dataHtml = resp.text
            json_data = json.loads(dataHtml)
            user_profile = json_data["user"]
            pprint(user_profile)
            #save the user in the database
            if Users.objects(username=insta_handle).first() is not None:
                form.insta_handle.errors.append("This Instagram handle is already registered with us.")    
                return render_template('register.html', form=form)
            else:
                user = Users()
                user.username = user_profile["username"]
                user.name = user_profile["full_name"]
                user.bio = user_profile["biography"]
                user.website = user_profile["external_url"]
                user.followed_by_count = user_profile["followed_by"]["count"]
                user.following_count = user_profile["follows"]["count"]
                user.profile_image_url = user_profile["profile_pic_url_hd"]
                user.save()
            
            return redirect(url_for('instagramThankYou'))
        else:
            form.insta_handle.errors.append("There is no user with this instagram handle.")
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)

@app.route('/instagram_callback')
def instagramCallback():
    if request.args.get('code', '') == "":
    	return render_template('register.html')
    code = request.args.get('code', '')
    payload = {
    	'client_id' : config.CLIENT_ID,
    	'client_secret' : config.CLIENT_SECRET,
    	'grant_type' : 'authorization_code',
    	'redirect_uri' : config.REDIRECT_URL,
    	'code' : code
    }

    resp = HTTPRequest.post(config.ACCESS_TOKEN_URL, data=payload)
    pprint(resp.json())
    #save the use details into database
    #u'{"access_token": "1943736698.487f423.0d7f8037021744b58b48276d52800650", "user": {"id": "1943736698", "username": "mac_patel0", "profile_picture": "https://scontent.cdninstagram.com/t51.2885-19/11357441_786307251483910_525950542_a.jpg", "full_name": "Mahesh Patel", "bio": "", "website": "", "is_business": false}}'
    #save the user in the database
    resp_json = resp.json()
    user_profile = resp_json["user"]
    insta_handle = user_profile["username"]
    
    user = Users()
    if Users.objects(username=insta_handle).first() is not None:
        user = Users.objects(username=insta_handle).first()
    else:
        user.username = user_profile["username"]
        user.name = user_profile["full_name"]
        user.bio = user_profile["bio"]
        user.website = user_profile["website"]
        user.profile_image_url = user_profile["profile_picture"]
        user.access_token = resp_json["access_token"]
        user.save()

    return redirect(url_for('instagramThankYou'))

@app.route('/thank_you')
def instagramThankYou():
    return render_template('thank_you.html')

@app.route('/search_user/')
def search_users():
    query = request.args.get('query', "")
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 3)
    resp = {}
    next_url = ""
    prev_url = ""
    users ={}
    pprint(query)
    pprint(page)
    pprint(per_page)
    page =int(page)
    per_page =int(per_page)
    skip = (page-1) * per_page
    if query =="":
        users = Users.objects().only('username', 'bio')
    else:
        users = Users.objects().only('username', 'bio').search_text(query)
    total_users = users.count()
    total_pages = int(ceil(total_users/per_page))
    is_next= (page <= total_pages)
    is_prev= (page > 1)

    if is_next == True:
        next_url = url_for("search_users", query=query, page=(page+1),per_page=per_page)
    if is_prev == True:
        prev_url = url_for("search_users", query=query, page=(page-1),per_page=per_page)
    results = [json.loads(o.to_json()) for o in users.skip(skip).limit(per_page)]

    resp['total']=total_users
    resp['results']=results
    resp['page']=page
    resp['per_page']=per_page
    resp['next_url']=next_url
    resp['prev_url']=prev_url
    
    return jsonify(resp)


if __name__ == "__main__":
	app.run(debug=True)
