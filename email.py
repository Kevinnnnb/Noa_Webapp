import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#This is a code that I save in case I need it in ein andere Project

def send_email(sender_email, sender_password, recipient_email, subject, body):
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = recipient_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, html_message.as_string())

    print("Email envoyé !")

# Exécution de la fonction

sender_email = "yourname@mail.com"
sender_password = "your security key" # For the password you need to go to your google account and search for app password -> you will have a 16 digits password for your script 

recipient_email = "yourname@mail.com"
subject = "Hello World !"
body = """ Your content here ! """

send_email(sender_email, sender_password, recipient_email, subject, body)
