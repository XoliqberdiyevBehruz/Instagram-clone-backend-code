from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import re
import threading
from twilio.rest import Client
from rest_framework.exceptions import ValidationError
from decouple import config
regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
phone_regex = re.compile(r"^(\+\d{12}|\d{12}|\(\d{2}\)\s?\d{3}[\s-]?\d{2}[\s-]?\d{2})$")

def check_email_or_phone_number(email_phone_number):
    if re.fullmatch(regex,email_phone_number):
        email_phone_number = 'email'

    elif re.fullmatch(phone_regex, email_phone_number):
        email_phone_number = 'phone'

    else:
        data = {
            'success':False,
            'message': 'email yoki porol notogri'
        }
        raise ValidationError(data)
    return email_phone_number


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        return self.email.send()
    
class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )

        if data.get("context_type") == 'html':
            email.content_subtype = 'html'
        
        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'email/active_account.html',
        {'code':code}
    )
    Email.send_email(
        {
            'subject':'Royxatdan otish',
            'to_email':email,
            'body':html_content,
            'content_type':'html'
        }
    )


def send_phone_token(phone, code):
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    client.message.create(
        body=f'salom, sizninh tasiqlash kodingiz {code}',
        from_='+998947099974',
        to=f'{phone}'
    )
