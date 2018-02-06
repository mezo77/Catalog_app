from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, distinct, desc, asc, func
from sqlalchemy.sql import exists
from database_config import Base, Category, CategoryItem, User

from flask import (Flask, request, url_for, flash, redirect, render_template,
                    jsonify, abort, session as login_session, make_response)
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///Catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None




@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code (obtain the one-time-code from the sever)
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print("result is: %s" % result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received %s ") % access_token


    # Exchange client token for long-lived server-side token
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.12/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)
    print("data is: %s" % data)

    # Extract the access token from response
    token = 'access_token=' + data['access_token']

    # Use token to get user info from API.
    url = 'https://graph.facebook.com/v2.12/me?%s&fields=name,id,email,picture' % token
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    # print("URL sent for API access: %s" % url)
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['picture'] = data["picture"]["data"]["url"]
    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    # url = 'https://graph.facebook.com/v2.12/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    # h = httplib2.Http()
    # result = h.request(url, 'GET')[1]
    # data = json.loads(result)



    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        elif login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
            del login_session['access_token']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showAllCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showAllCategories'))

@app.route('/')
@app.route('/categories')
def showAllCategories():
    categories = session.query(Category).all()
    categories_count = session.query(Category).count()
    items = session.query(CategoryItem).order_by(desc(CategoryItem.id)).limit(categories_count).all()
    if 'username' not in login_session:
        return render_template("publicCategoriesPage.html", categories=categories, items=items)
    else:
        category = session.query(Category).filter_by(user_id=login_session['user_id']).first()
        creator = getUserInfo(login_session['user_id'])
        return render_template("categories.html", categories=categories, items=items, creator=creator)


@app.route('/categories/<string:category_name>/items')
def showItemsInACategory(category_name):
    category = session.query(Category).filter_by(name=category_name).first()
    categories = session.query(Category).all()
    items = session.query(CategoryItem).filter_by(cat_name=category.name).all()
    items_count = session.query(CategoryItem).filter_by(cat_name=category.name).count()
    creator = getUserInfo(login_session['user_id'])
    if 'username' not in login_session:
        return render_template('publicCategoryPage.html', items=items, category=category, count=items_count, categories=categories, category_name=category.name)
    else:
        return render_template("category.html", items=items, category=category, count=items_count, categories=categories, category_name=category.name, creator=creator)


@app.route('/categories/<string:category_name>/<string:item_name>')
def showItemDescription(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).first()
    item = session.query(CategoryItem).filter_by(name=item_name).first()
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template("publicItemPage.html", item=item, creator=creator)
    else:
        return render_template('itemDescription.html', item=item, creator=creator)


@app.route('/categories/add-category', methods=['GET', 'POST'])
def addANewCategory():
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(user_id=login_session['user_id']).first()
    creator = getUserInfo(category.user_id)
    if request.method == 'POST':
        name = request.form['input']
        if name != '':
            exist = session.query(Category).filter_by(name=name).scalar()
            if exist is None:
                category_to_add = Category(name=name, user_id=login_session['user_id'])
                session.add(category_to_add)
                session.commit()
                flash("a new category has been added successfully")
                return redirect(url_for('showAllCategories'))
            else:
                flash("This category already exists")
                return redirect(url_for('showAllCategories'))
        else:
            flash("you didn't specify the category name")
            return redirect(url_for('showAllCategories'))
    else:
        return render_template('addcategory.html', creator=creator)


@app.route('/categories/<string:category_name>/delete', methods=['GET', 'POST'])
def deleteACategory(category_name):
    category_to_delete = session.query(Category).filter_by(name=category_name).first()
    creator = getUserInfo(category_to_delete.user_id)
    if 'username' not in login_session:
        return redirect('/login')
    if category_to_delete.user_id != login_session['user_id']:
        return '''<script>function myFunction() {
                alert('you are not authorized to do this operation.');}
                 </script><body onload="myFunction()"> '''
    if request.method == 'POST':
        session.delete(category_to_delete)
        session.commit()
        flash("a category has been deleted successfully")
        return redirect(url_for('showAllCategories',))
    else:
        return render_template('deleteCategory.html', category_name=category_to_delete.name, category_to_delete=category_to_delete, category=category_to_delete, creator=creator)


@app.route('/categories/<string:category_name>/edit', methods=['GET', 'POST'])
def editACategory(category_name):
    category_to_edit = session.query(Category).filter_by(name=category_name).first()
    creator = getUserInfo(category_to_edit.user_id)
    if 'username' not in login_session:
        return redirect('/login')
    if category_to_edit.user_id != login_session['user_id']:
        return '''<script>function myFunction() {
                alert('you are not authorized to do this operation.');}
                 </script><body onload="myFunction()"> '''
    if request.method == 'POST':
        edited_name = request.form['input']
        if edited_name != '':
            category_to_edit.name = edited_name
            session.add(category_to_edit)
            session.commit()
            flash("you have successfully updated a category")
            return redirect(url_for('showItemsInACategory', category_name=category_to_edit.name))
        else:
            flash("you have NOT edited the category, text field was left blank")
            return redirect(url_for('showItemsInACategory', category_name=category_to_edit.name))
    else:
        return render_template('editCategory.html', category_name=category_to_edit.name, category=category_to_edit, creator=creator)


@app.route('/categories/<string:category_name>/addnewitem', methods=['GET', 'POST'])
def addNewItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).first()
    creator = getUserInfo(category.user_id)
    new_item = CategoryItem(cat_name=category_name, user_id=login_session['user_id'])
    if request.method == 'POST':
        name = request.form['name']
        if name != '':
            new_item.name = name
            new_item.description = request.form['description']
            session.add(new_item)
            session.commit()
            flash("a new item has been added seccessfully")
            return redirect(url_for('showItemsInACategory', category_name=category.name))
        else:
            flash("you have NOT specified the item name, Try again")
            return redirect(url_for('showItemsInACategory', category_name=category.name))
    else:
        return render_template('addItemToCategory.html', category=category, creator=creator)



@app.route('/categories/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).first()
    creator = getUserInfo(category.user_id)
    item = session.query(CategoryItem).filter_by(name=item_name).first()
    name = item.name
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("item %s has been deleted successfully" % name)
        return redirect(url_for('showItemsInACategory', category_name=category.name))
    else:
        return render_template('deleteItem.html', category_name=category.name, item_name=item.name, item=item, category=category, creator=creator)



@app.route('/categories/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).first()
    creator = getUserInfo(category.user_id)
    categories = session.query(Category).all()
    item = session.query(CategoryItem).filter_by(name=item_name).first()
    if request.method == 'POST':
        name = request.form['name']
        if name != '':
            item.name = name
            item.description = request.form['description']
            item.cat_name = request.form['category']
            session.add(item)
            session.commit()
            flash("you have edited %s item successfully" % name)
            return redirect(url_for('showItemsInACategory', category_name=category.name))
        else:
            flash("editing %s item was NOT successfull" % name)
            return redirect(url_for('showItemsInACategory', category_name=category.name))
    else:
        return render_template('editItem.html', category_name=category.name, item_name=item.name, item=item, category=category, categories=categories, creator=creator)


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/catalog.json')
def showITEMSJSON():
    # categories = session.query(Category).all()
    items = session.query(CategoryItem).all()
    return jsonify(items=[i.serialize for i in items])



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
