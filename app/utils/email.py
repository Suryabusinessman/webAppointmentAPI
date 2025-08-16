from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel
from typing import List

class EmailSchema(BaseModel):
    email: str
    subject: str
    body: str

conf = ConnectionConfig(
    MAIL_USERNAME = "your_email@example.com",
    MAIL_PASSWORD = "your_password",
    MAIL_FROM = "your_email@example.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.example.com",
    MAIL_FROM_NAME = "Your Name",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
)

async def send_email(email: EmailSchema, background_tasks: BackgroundTasks):
    message = MessageSchema(
        subject=email.subject,
        recipients=[email.email],
        body=email.body,
        subtype="html"
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)