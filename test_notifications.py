
# -*- coding: utf-8 -*-
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_telegram():
    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
    tg_chat = os.getenv('TELEGRAM_OWNER_ID')
    print(f'Telegram Token: {tg_token[:10]}...')
    if tg_token and tg_chat:
        msg = 'NUEVA CITA (ORION BOT) - PRUEBA\n\nID: MP-9999\nNombre: Prueba\nTelefono: 123456789\nHora: 10:00 AM'
        r = requests.post(f'https://api.telegram.org/bot{tg_token}/sendMessage', data={'chat_id': tg_chat, 'text': msg})
        print('Telegram response:', r.status_code, r.text)

def test_email():
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    print(f'Email User: {email_user}')
    if email_user and email_pass:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_user
        msg['Subject'] = 'Nueva Cita - Prueba (MP-9999)'
        body = 'NUEVA CITA AGENDADA POR BOT TELEFONICO\n\nID: MP-9999\nNombre: Prueba\nTelefono: 123456789\nHora: 10:00 AM\nOrigen: phone_call'
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        text = msg.as_string()
        server.sendmail(email_user, email_user, text)
        server.quit()
        print('Email sent successfully')

if __name__ == '__main__':
    test_telegram()
    test_email()

