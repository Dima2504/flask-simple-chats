from flask.views import MethodView
from app.authentication.decorators import login_required
from app import db
from app.authentication import User
from sqlalchemy.sql import exists
from flask import g
from flask import session
from flask import render_template
from flask import abort
from flask import redirect
from flask import url_for


class UserChatsList(MethodView):
    decorators = [login_required, ]

    def get(self):
        """Return list of chats the current user has started"""
        user = g.user
        companions = user.chats
        return render_template('chats/list.html', user_companions=companions)


class UserChatBegin(MethodView):
    decorators = [login_required, ]

    def get(self, companion_username: str):
        """Prepares the current user to communication, creates unique room name, based on names of users.
        Saves data into session and redirects into chat room. If username is not valid, it means that the url was
        inputted directly, so, it is likely wrong. If it is so, returns page not found.
        :param companion_username: username of user, which the current user wants to talk to"""
        user = g.user
        if not db.session.query(exists().where(User.username == companion_username)).scalar():
            abort(404)
        room_name = '_'.join(sorted([user.username, companion_username]))    # FIXME
        session['room_name'] = room_name
        session['user_name'] = user.name
        return redirect(url_for('chats.going'))


class UsersChatGoing(MethodView):
    decorators = [login_required, ]

    def get(self):
        """Checks whether the session has obligatory params of not. If not, return page not found.
        If everything is OK, renders chat room template"""
        user_name = session.get('user_name')
        room_name = session.get('room_name')
        if user_name is None or room_name is None:
            abort(404)
        return render_template('chats/going.html')

