from mongo_service import MongoService
from flask import Blueprint, render_template, make_response

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@dashboard.route('/home')
def home():
    """
    Render the home page for the 'dashboard' module
    This returns the names and URLs of adjacent directories
    """
    return render_template("register2.html", tagname = 'home')

@dashboard.route('/register2')
def register2():
    """
    Render the thing description register page for the 'dashboard' module
    """
    return render_template('register2.html', tagname = 'register2')

@dashboard.route('/delete2')
def delete2():
    """
    Render the delete page for the 'dashboard' module
    """
    mongo_service = MongoService()
    things = mongo_service.find_things(None)
    thing_ids = [thing["id"] for thing in things]
    return render_template('delete2.html', tagname = 'delete2', thing_ids=thing_ids)

@dashboard.route('/policy')
def policy():
    """
    Render the policy page for the 'dashboard' module
    """
    return render_template('policy.html', tagname = 'policy')

@dashboard.route('/command')
def command():
    """
    Render the command page for the 'dashboard' module
    """
    return render_template('command.html', tagname = 'command')

