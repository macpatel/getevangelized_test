from flask import Blueprint, render_template, request, redirect, json, jsonify, url_for
from app import db
from app.mod_register.forms import RegisterInstagramUserForm
from app.shared.models.users import Users
from pprint import pprint
import requests as HTTPRequest
import config

mod_register = Blueprint('register', __name__,)

@mod_register.route('/register', methods=["GET", "POST"])
def save_instagram_user():
    form = RegisterInstagramUserForm()
    if request.method == "GET":
        return render_template('register.html', form=form)
    else:
        if request.method == "POST" and form.validate_on_submit():
            pprint(request.form['insta_handle'])
            insta_handle = request.form['insta_handle']
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
                
                return redirect(url_for('register.instagram_thank_you'))
            else:
                form.insta_handle.errors.append("There is no user with this instagram handle.")
                return render_template('register.html', form=form)
        return render_template('register.html', form=form)

@mod_register.route('/connect/instagram')
def redirect_to_instagram_oauth():
    return redirect(config.INSTA_AUTH_URL)

@mod_register.route('/instagram_callback')
def instagram_callback():
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

    return redirect(url_for('register.instagram_thank_you'))

@mod_register.route('/thank_you')
def instagram_thank_you():
    return render_template('thank_you.html')