import os
import time
import imaplib
import smtplib
import email
from email.message import EmailMessage
import logging
from dotenv import load_dotenv
from sofia_v9_app import SofiaLinV9Engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EmailWorker")

load_dotenv()
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

engine = SofiaLinV9Engine()

def check_and_reply():
    try:
        # Conectar a IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        
        status, messages = mail.search(None, '(UNSEEN)')
        if status != "OK":
            return
            
        mail_ids = messages[0].split()
        for mail_id in mail_ids:
            status, msg_data = mail.fetch(mail_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"]
                    sender = msg["from"]
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                        
                    logger.info(f"Nuevo Email de {sender}: {subject}")
                    
                    # Procesar con Motor V9
                    call_data = {
                        "caller_id": sender,
                        "transcript": f"{subject}\n{body}",
                        "channel": "email"
                    }
                    result = engine.process_incoming_call(call_data)
                    reply_text = result.get("audio_response_text", "Recibido. Procesando...")
                    
                    # Enviar respuesta vía SMTP
                    send_reply(sender, f"Re: {subject}", reply_text)
                    
        mail.logout()
    except Exception as e:
        logger.error(f"Error procesando email: {e}")

def send_reply(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        logger.info(f"Respuesta enviada a {to_email}")
    except Exception as e:
        logger.error(f"Error enviando email: {e}")

if __name__ == "__main__":
    logger.info("Iniciando Email Worker V9...")
    while True:
        check_and_reply()
        time.sleep(15) # Revisar cada 15 segundos
