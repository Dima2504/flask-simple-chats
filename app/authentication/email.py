import smtplib
from flask import current_app
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread


def _send_mail(app: object, server: smtplib.SMTP, from_addr: str, to_addr: str, message: str):
    """
    Private function for a separate thread. It sends prepared :attr:`massage` using given connected instance of
    :class:`SMTP` from one address to another one.
    :param app: instance of flask app, but not a LocalProxy. It is an object we get after
                using :method:`current_app._get_current_object`
    :param server: instance of already connected smtp server.
    :param from_addr: sender's adress.
    :param to_addr: recipient's address
    :param message: string of message to be sent.
    """
    with app.app_context():
        server.sendmail(from_addr, to_addr, message)
    server.close()


def build_message(from_addr: str, to_addr:str, subject: str, text:str) -> str:
    """
    Creates correct message according to the format.
    """
    message = MIMEMultipart()
    message['FROM'] = from_addr
    message['TO'] = to_addr
    message['SUBJECT'] = subject
    message.attach(MIMEText(text))
    return message.as_string()


def send_mail(to_addr: str, subject: str, text: str) -> Thread:
    """
    Function receives mail data from config, built message and sends it in separate
    thread not to block the main one. Uses the function above.
    :param to_addr:recipient's address.
    :type to_addr: str
    :param subject: The subject of the message.
    :type subject: str
    :param text: The text of the message.
    :type text: str
    :return: the instance of started thread
    :rtype: Thread
    """
    mail_host = current_app.config['MAIL_SERVER']
    mail_port = current_app.config['MAIL_PORT']
    mail_username = current_app.config['MAIL_USERNAME']
    mail_password = current_app.config['MAIL_PASSWORD']
    from_addr = mail_username

    message = build_message(from_addr, to_addr, subject, text)

    server = smtplib.SMTP(host=mail_host, port=mail_port)
    server.starttls()
    server.login(mail_username, mail_password)

    thread = Thread(target=_send_mail, args=(current_app._get_current_object(),
                    server, from_addr, to_addr, message))
    thread.start()
    return thread

