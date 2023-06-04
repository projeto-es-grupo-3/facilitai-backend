import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def notify(current_user):
    """
    Notifica o usuário sobre atualizações em anúncios.
    Esse método é chamado dentro de outros métodos, quando houverem atualizações em 
    anúncios do interesse do usuário.
    """

    user = current_user

    to_email = current_user.email
    subject = 'Houveram atualizações desde a sua última visita ao Facilitaí!'
    message = 'Olá! Anúncios de seu interesse foram atualizados desde a sua última visita.'    

    if send_email_notification(to_email, subject, message):
        return 'Notification sent successfully'
    else:
        return 'Failed to send notification'


def send_email_notification(to_email, subject, message):
    from_email = 'facilitai-ufcg@gmail.com'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465
    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    body = message
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False
