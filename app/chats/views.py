from flask.views import MethodView
from app.authentication.decorators import login_required
from app import db
from app.authentication import User
from flask import g
from flask import session
from flask import render_template
from flask import abort
from flask import redirect
from flask import url_for
from .utils import get_users_unique_room_name


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
        companion = User.query.filter_by(username=companion_username).first_or_404()
        room_name = None
        try:
            room_name = get_users_unique_room_name(user.username, companion_username)
        except ValueError:
            abort(404)
        session['room_name'] = room_name
        session['user_name'] = user.name
        session['companion_id'] = companion.user_id
        return redirect(url_for('chats.going'))


class UserChatEnd(MethodView):
    decorators = [login_required]

    def get(self):
        """Removes information from user session when he leaves the room"""
        session.pop('room_name')
        session.pop('user_name')
        session.pop('companion_id')
        return redirect(url_for('view.index'))


class UsersChatGoing(MethodView):
    decorators = [login_required, ]

    def get(self):
        """Checks whether the session has obligatory params or not. If not, return page not found.
        If everything is OK, renders chat room template"""
        user_name = session.get('user_name')
        room_name = session.get('room_name')
        companion_id = session.get('companion_id')
        companion_user_name = db.session.query(User.name).filter(User.user_id == companion_id).scalar()
        if user_name is None or room_name is None or companion_id is None:
            abort(404)

        return render_template('chats/going.html', companion_user_name=companion_user_name)

