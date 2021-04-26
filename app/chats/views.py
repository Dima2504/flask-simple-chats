from flask.views import MethodView
from app.authentication.decorators import login_required
from flask import g
from flask import render_template


class UserChatsList(MethodView):
    decorators = [login_required, ]

    def get(self):
        """Return list of chats the current user has started"""
        user = g.user
        companions = user.chats
        return render_template('chats/list.html', user_companions=companions)
