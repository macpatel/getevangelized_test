from flask import Blueprint, render_template, request, redirect, json, jsonify, url_for
import config
from app.shared.models.users import Users
import math
from pprint import pprint

mod_search = Blueprint('search', __name__,)

@mod_search.route('/search_user/')
def search_users():
    resp = {}
    users ={}
    next_url = ""
    prev_url = ""
    query = request.args.get('query', "")
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 3)
    pprint(query)
    pprint(page)
    pprint(per_page)
    page =int(page)
    per_page =int(per_page)
    skip = (page-1) * per_page
    if query == "":
        users = Users.objects().only('username', 'bio')
    else:
        users = Users.objects().only('username', 'bio').search_text(query)
    total_users = users.count()
    total_pages = int(math.ceil(total_users/per_page))
    is_next= (page < total_pages) if (total_pages/per_page == 0) else (page <= total_pages)
    
    is_prev= (page > 1)

    if is_next == True:
        next_url = url_for("search.search_users", query=query, page=(page+1),per_page=per_page)
    if is_prev == True:
        prev_url = url_for("search.search_users", query=query, page=(page-1),per_page=per_page)
    results = [json.loads(o.to_json()) for o in users.skip(skip).limit(per_page)]

    resp['total']=total_users
    resp['results']=results
    resp['page']=page
    resp['per_page']=per_page
    resp['next_url']=next_url
    resp['prev_url']=prev_url
    
    return jsonify(resp)