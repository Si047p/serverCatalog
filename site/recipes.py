from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, distinct, desc
from sqlalchemy.orm import sessionmaker
# from catalog import Base, Recipe, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from database import User, Recipe, Base

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('/var/www/serverCatalog/site/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu App"


# Connect to Database and create database session
engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    # creates a random state variable for authentication
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/serverCatalog/site/client_secrets.json', scope='')
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
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
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
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already'
                                 ' connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
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
    creator = getUserInfo(user_id)
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px'
    output += ';-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print ("done!")
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                    'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps(
                                 'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')

    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    logout = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % logout
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return redirect('/')


# JSON APIs to view recipes
@app.route('/recipes/JSON')
def recipesJSON():
    items = session.query(Recipe).all()
    return jsonify(recipes=[i.serialize for i in items])


@app.route('/recipes/<int:user_id>/JSON')
def userRecipesJSON(user_id):
    items = session.query(Recipe).filter_by(user_id=user_id).all()
    return jsonify(recipes=[i.serialize for i in items])


@app.route('/recipes/<string:type>/JSON')
def typeRecipesJSON(type):
    items = session.query(Recipe).filter_by(type=type).all()
    return jsonify(recipes=[i.serialize for i in items])


# Show all recipes
@app.route('/')
def home():
    types = ['Beverage', 'Appetizer', 'Side', 'Entree', 'Desert']
    recipes = session.query(Recipe).order_by(desc(Recipe.id)).limit(5)
    return render_template('home.html', types=types, recipes=recipes,
                           login_session=login_session)


@app.route('/recipes/')
def showRecipes():
    recipes = session.query(Recipe).order_by(asc(Recipe.name))
    return render_template('recipes.html', recipes=recipes,
                           login_session=login_session)


# Show single recipe
@app.route('/recipes/<int:recipe_id>/')
def singleRecipe(recipe_id):
    item = session.query(Recipe).filter_by(
        id=recipe_id).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session:
        return render_template('publicsingleRecipe.html', recipe=item,
                               login_session=login_session,
                               creator=creator)
    else:
        if item.user_id == getUserID(login_session['email']):
            return render_template('singleRecipe.html', recipe=item,
                                   login_session=login_session,
                                   creator=creator)
        else:
            return render_template('publicsingleRecipe.html', recipe=item,
                                   login_session=login_session,
                                   creator=creator)


@app.route('/recipes/<string:type_name>/items')
def oneType(type_name):
    recipes = session.query(Recipe).filter_by(
        type=type_name).all()
    return render_template('recipetype.html', recipes=recipes,
                           login_session=login_session)


# Show a user's recipes
@app.route('/recipes/chef/<int:creator_id>/')
def oneUserRecipe(creator_id):
    creator = getUserInfo(creator_id)
    recipes = session.query(Recipe).filter_by(
        user_id=creator_id).all()
    if 'username' not in login_session:
        return render_template('publiconeuser.html', creator=creator,
                               recipes=recipes, login_session=login_session)
    else:
        user_id = getUserID(login_session['email'])
        if creator_id == user_id:
            return render_template('oneuser.html', creator=creator,
                                   recipes=recipes,
                                   login_session=login_session)
        else:
            return render_template('publiconeuser.html', creator=creator,
                                   recipes=recipes,
                                   login_session=login_session)


# Create a new recipe
@app.route('/recipes/new/', methods=['GET', 'POST'])
def newRecipe():
    if 'username' not in login_session:
        return redirect('/login')
    else:
        currentUser = login_session['user_id']
    if request.method == 'POST':
        newItem = Recipe(name=request.form['name'], instructions=request.form[
            'instructions'], type=request.form['type'], picture=request.form[
            'picture'], user_id=currentUser)
        session.add(newItem)
        session.commit()
        flash('New Recipe %s Created Successfully' % (newItem.name))
        return redirect(url_for('showRecipes'))
    else:
        return render_template('newrecipe.html', login_session=login_session)


# Edit a recipe
@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def editRecipe(recipe_id):
    if 'username' not in login_session:
        return redirect('/login')
    else:
        editedItem = session.query(Recipe).filter_by(id=recipe_id).one()
        user_id = getUserID(login_session['email'])
        if user_id == editedItem.user_id:
            if request.method == 'POST':
                if request.form['name']:
                    editedItem.name = request.form['name']
                if request.form['instructions']:
                    editedItem.instructions = request.form['instructions']
                if request.form['picture']:
                    editedItem.picture = request.form['picture']
                if request.form['type']:
                    editedItem.type = request.form['type']
                session.add(editedItem)
                session.commit()
                flash('Recipe Successfully Edited')
                return redirect(url_for('showRecipes'))
            else:
                return render_template('editrecipe.html',
                                       login_session=login_session,
                                       recipe_id=recipe_id, item=editedItem)
        else:
            flash('%s is not your item.' % (editedItem.name))
            return redirect(url_for('showRecipes'))


# Delete a menu item
@app.route('/recipes/<int:recipe_id>/delete', methods=['GET', 'POST'])
def deleteRecipe(recipe_id):
    if 'username' not in login_session:
        return redirect('/login')
    else:
        itemToDelete = session.query(Recipe).filter_by(id=recipe_id).one()
        user_id = getUserID(login_session['email'])
        if user_id == itemToDelete.user_id:
            if request.method == 'POST':
                session.delete(itemToDelete)
                session.commit()
                flash('Menu Item Successfully Deleted')
                return redirect(url_for('showRecipes'))
            else:
                return render_template('deleterecipe.html',
                                       login_session=login_session,
                                       item=itemToDelete)
        else:
            flash('%s is not your item.' % (itemToDelete.name))
            return redirect(url_for('showRecipes'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
