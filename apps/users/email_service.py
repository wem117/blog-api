from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import translation

def send_welcome_email(user):
    lang = user.preferred_language or 'en'
    
    with translation.override(lang):
        subject = 'Welcome to Blog!'
        html_message = render_to_string('emails/welcome.html', {'user': user})
        
        send_mail(
            subject=subject,
            message=f'Hello, {user.first_name}!',
            from_email='noreply@blog.com',
            recipient_list=[user.email],
            html_message=html_message,
        )
