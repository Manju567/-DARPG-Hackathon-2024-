import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self):
        pass

    def send_email(self, receiver_email, subject, body):
        try:
            sender_email = 'pulakuntasomeshkumar8@gmail.com'  # Update with your Gmail email
            sender_password = 'Solo@somu7'  # Update with your Gmail password
            
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = receiver_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, sender_password)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
            print(f"Email sent successfully to {receiver_email}")
        except Exception as e:
            print(f"Failed to send email to {receiver_email}: {str(e)}")
        finally:
            server.quit()
