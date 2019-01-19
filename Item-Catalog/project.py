from flask import Flask, render_template, url_for, request
from flask import redirect, flash, jsonify, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Library, MenuItem, User
from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Library Menu Application"


# Connect to Database and create database session
engine = create_engine(
    'sqlite:///librarymenuwithusers.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase +
            string.digits) for x in xrange(32))
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
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # See if a user exists, if it doesn't make a new one
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
    output += ' " style = "width: 300px; height: 300px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


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
    except BaseException:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        # del login_session['access_token']
        # del login_session['gplus_id']
        # del login_session['username']
        # del login_session['email']
        # del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print "this is the status " + result['status']
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON APIs to view Library Information


@app.route('/library/<int:library_id>/menu/JSON')
def libraryMenuJSON(library_id):
    library = session.query(Library).filter_by(id=library_id).one()
    items = session.query(MenuItem).filter_by(
        library_id=library_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/library/<int:library_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(library_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/library/JSON')
def librarysJSON():
    librarys = session.query(Library).all()
    return jsonify(librarys=[r.serialize for r in librarys])


# Show all librarys
@app.route('/')
@app.route('/library/')
def showLibrarys():
    librarys = session.query(Library).order_by(asc(Library.name))
    if 'username' not in login_session:
        return render_template('publiclibrarys.html', librarys=librarys)
    else:
        return render_template('librarys.html', librarys=librarys)

# Create a new library


@app.route('/library/new/', methods=['GET', 'POST'])
def newLibrary():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newLibrary = Library(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newLibrary)
        flash('New Library %s Successfully Created' % newLibrary.name)
        session.commit()
        return redirect(url_for('showLibrarys'))
    else:
        return render_template('newLibrary.html')

# Edit a library


@app.route('/library/<int:library_id>/edit/', methods=['GET', 'POST'])
def editLibrary(library_id):
    editedLibrary = session.query(
        Library).filter_by(id=library_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedLibrary.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        if request.form['name']:
            editedLibrary.name = request.form['name']
            flash('Library Successfully Edited %s' % editedLibrary.name)
            return redirect(url_for('showLibrays'))
    else:
        return render_template('editLibrary.html', library=editedLibrary)


# Delete a library
@app.route('/library/<int:library_id>/delete/', methods=['GET', 'POST'])
def deleteLibrary(library_id):
    libraryToDelete = session.query(
        Library).filter_by(id=library_id).one()

    if 'username' not in login_session:
        return redirect('/login')
    if libraryToDelete.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        session.delete(libraryToDelete)
        flash('%s Successfully Deleted' % libraryToDelete.name)
        session.commit()
        return redirect(url_for('showLibrarys', library_id=library_id))
    else:
        return render_template('deleteLibrary.html', library=libraryToDelete)

# Show a library menu


@app.route('/library/<int:library_id>/')
@app.route('/library/<int:library_id>/menu/')
def showMenu(library_id):
    library = session.query(Library).filter_by(id=library_id).one()
    items = session.query(MenuItem).filter_by(library_id=library_id).all()
    creator = getUserInfo(library.user_id)
    if 'username' not in login_session:
        return render_template(
            'publicmenu.html', items=items, library=library, creator=creator)
    else:
        return render_template('menu.html', items=items,
                               library=library, creator=creator)


# Create a new menu item
@app.route('/library/<int:library_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(library_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = connect_to_database()
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           course=request.form['course'],
                           library_id=library_id,
                           user_id=library.user_id)
        session.add(newItem)
        session.commit()
        flash('New Menu %s Item Successfully Created')
        return redirect(url_for('showMenu', library_id=library_id))
    else:
        return render_template('newmenuitem.html', library_id=library_id)

# Edit a menu item


@app.route('/library/<int:library_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(library_id, menu_id):
    editedItem = session.query(
        MenuItem).filter_by(id=menu_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedItem.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', library_id=library_id))
    else:
        return render_template(
            'editmenuitem.html', library_id=library_id,
            menu_id=menu_id, item=editedItem)


# Delete a menu item
@app.route('/library/<int:library_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(library_id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', library_id=library_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)

# Disconnect based on provider


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            # del login_session['gplus_id']
            # del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showLibrarys'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showLibrarys'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)