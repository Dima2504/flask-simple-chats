from app.authentication import authentication as auth_bp
from app.authentication.models import User
from app import db
from flask import request
from flask import redirect
from flask import url_for
from flask import session, g
from flask import flash
from flask import render_template
from flask.views import MethodView


@auth_bp.before_app_request
def recognize_logged_in_user():
    current_user_id = session.get('current_user_id')
    g.user = User.get_user_by_id(current_user_id) if current_user_id is not None else None


class LoginView(MethodView):
    def get(self):
        """Renders login page"""
        return render_template('authentication/login.html')

    def post(self):
        """
        Get user's email and password form html form, checks them and allow or permit user to log in.
        Saves user's id for comfortable use in the certain session.
        :return: rendered html code or :class:`Response` (redirect)
        :rtype:str, Response
        """
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Wrong email! Maybe, you have not registered')
        elif not user.verify_password(password):
            flash('Wrong password! Try again')
        else:
            flash('Successfully logged in!')
            session['current_user_id'] = user.user_id
            return redirect(url_for('view.index'))

        return render_template('authentication/login.html')


class RegisterView(MethodView):
    def get(self):
        """Renders registration page"""
        return render_template('authentication/register.html')

    def post(self):
        """
        Receives user data, verify it and add new user to database.
        :return: rendered html code or :class:`Response` (redirect)
        :rtype:str, Response
        """
        email = request.form['email']
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('User with such an email has been registered!')
        elif User.query.filter_by(username=username).first():
            flash('This username is busy! Try putting another one')
        else:
            flash('Successfully registered!')
            user = User(email=email, username=username, name=name)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('authentication.login'))

        return render_template('authentication/register.html')


@auth_bp.route('/logout')
def logout():
    """Clears user`s id from session"""
    session.clear()
    return redirect(url_for('view.index'))



