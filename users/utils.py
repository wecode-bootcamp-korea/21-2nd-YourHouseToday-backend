import jwt,smtplib,ssl
from email.message import EmailMessage

from django.http import JsonResponse
from django.template.loader import get_template

from .models     import User
from my_settings import SECRET_KEY, ALGORITHM, EMAIL_HOST,EMAIL_PASSWORD, EMAIL_PORT

def authorize_user(func):
    def wrapper(self,request, **kwarg):
        try:
            self_token = request.headers['Authorization']
            payload    = jwt.decode(self_token, SECRET_KEY, ALGORITHM)

            if not User.objects.filter(id=payload['id']).exists():
                return JsonResponse({'message' : 'INVALID USER'}, status=401)

            request.user = User.objects.get(id=payload['id'])

        except KeyError:
            return JsonResponse({'message' : 'KEY ERROR'},status=401)     

        except jwt.DecodeError:
            return JsonResponse({'message' : 'JWT DECODE ERROR'},status=401)

        return func(self,request,**kwarg)

    return wrapper

def sort_user(func):
    def wrapper(self,request):
        try:
            self_token = request.headers.get('Authorization')

            if self_token == None:
                return func(self,request)

            payload    = jwt.decode(self_token, SECRET_KEY, ALGORITHM)

            if not User.objects.filter(id=payload['id']).exists():
                return JsonResponse({'message':'INVALID USER'}, status=401)

            request.user = User.objects.get(id=payload['id'])

        except jwt.DecodeError:
            return JsonResponse({'message':'JWT DECODE ERROR'},status=401)

        return func(self,request)

    return wrapper

def send_mail_all(self,receiver_email,email_message):
    try:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com',EMAIL_PORT,context=context) as server:
            server.login(EMAIL_HOST,EMAIL_PASSWORD)
            server.sendmail(EMAIL_HOST,receiver_email,email_message.as_string())
            server.quit()
    except:
        pass

class Mail:
    def create(self, receiver, subject, template):
        try:
            self.receiver = receiver
            self.message  = EmailMessage()

            self.message["Subject"] = subject
            self.message["From"]    = EMAIL_HOST
            self.message["To"]      = receiver

            content          = get_template(template)
            content_rendered = content.render(context={'receiver':receiver})
            self.message.set_content((content_rendered),'html')
            
        except:
            pass        

    def send(self):
        try:
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com',EMAIL_PORT,context=context) as server:
                server.login(EMAIL_HOST,EMAIL_PASSWORD)
                server.sendmail(EMAIL_HOST,self.receiver, self.message.as_string())
                server.quit()
        except:
            pass