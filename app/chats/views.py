from app.chats import chats as chats_bp
from app.chats.utils import search_for_users_by
from flask.views import MethodView
from app.authentication.decorators import login_required
from app import db
from app.authentication import User
from flask import current_app
from flask import g
from flask import session
from flask import render_template
from flask import abort
from flask import redirect
from flask import url_for
from flask import request
from flask import jsonify
from .utils import get_users_unique_room_name
from .utils import get_user_chats_and_last_messages


class UserSearchForChat(MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('chats/search.html')


@chats_bp.route('/ajax-search', methods=['GET'])
@login_required
def ajax_search():
    """
    The route is used when a certain user searches for the companion. It receives only ajax requests and returns list of
    dicts dumped in json format. Each dict represent information about one potential recipient. A string for searching
    is taken from requests url parameter: 'search-string'.
    If the request is not ajax, 404 error is raised.
    """
    x_requested_with = request.headers.get('X-Requested-With', default='')
    if x_requested_with != 'XMLHttpRequest':
        abort(404, description='Allowed only for ajax')

    current_user_id = g.user.user_id
    search_string = request.args.get('search-string', default='')
    result_data = search_for_users_by(search_string, current_user_id=current_user_id).all()
    result_data = [row._asdict() for row in result_data]
    return jsonify(data=result_data)


class UserChatsList(MethodView):
    decorators = [login_required, ]

    def get(self) -> str:
        """Return list of chats the current user has started and their last messages. The list is sorted by last
        message time writing. Uses paginator to represent chats using pages."""
        user = g.user
        current_page_num = request.args.get('page_num', default=1, type=int)
        chats_per_page = current_app.config['CHATS_PER_PAGE']
        paginator = get_user_chats_and_last_messages(user.user_id).paginate(current_page_num, chats_per_page, error_out=False)
        users_last_chats_info = paginator.items
        return render_template('chats/list.html', users_last_chats_info=users_last_chats_info, paginator=paginator)


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
