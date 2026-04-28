from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.models.task import Task


@dataclass(frozen=True)
class BotUserContact:
    user_id: str
    telegram_chat_id: int | None = None
    email: str | None = None
    phone: str | None = None


@dataclass(frozen=True)
class BotMessage:
    title: str
    body: str


@dataclass(frozen=True)
class DeliveryReceipt:
    channel: str
    target: str
    external_id: str


class NotificationSender(ABC):
    """Target interface used by bot services."""

    @abstractmethod
    def send(self, contact: BotUserContact, message: BotMessage) -> DeliveryReceipt:
        pass


class TelegramBotApi:
    """Simulated Telegram API with a method specific to python-telegram-bot."""

    def send_message(
        self, chat_id: int, text: str, parse_mode: str = "Markdown"
    ) -> str:
        return f"telegram:{chat_id}:{parse_mode}:{len(text)}"


class EmailClient:
    """Simulated email client with another incompatible interface."""

    def deliver(self, to_address: str, subject: str, html_body: str) -> dict:
        return {
            "message_id": f"email:{to_address}:{subject}",
            "status": "sent",
            "html": html_body,
        }


class SmsGateway:
    """Simulated SMS gateway that returns a numeric status code."""

    def push(self, msisdn: str, text: str) -> int:
        return 202 if msisdn and text else 400


class TelegramNotificationAdapter(NotificationSender):
    def __init__(self, telegram_api: TelegramBotApi):
        self.telegram_api = telegram_api

    def send(self, contact: BotUserContact, message: BotMessage) -> DeliveryReceipt:
        if contact.telegram_chat_id is None:
            raise ValueError("Telegram chat id is required")
        text = f"*{message.title}*\n{message.body}"
        external_id = self.telegram_api.send_message(contact.telegram_chat_id, text)
        return DeliveryReceipt("telegram", str(contact.telegram_chat_id), external_id)


class EmailNotificationAdapter(NotificationSender):
    def __init__(self, email_client: EmailClient):
        self.email_client = email_client

    def send(self, contact: BotUserContact, message: BotMessage) -> DeliveryReceipt:
        if not contact.email:
            raise ValueError("Email address is required")
        response = self.email_client.deliver(
            contact.email,
            message.title,
            f"<h1>{message.title}</h1><p>{message.body}</p>",
        )
        return DeliveryReceipt("email", contact.email, response["message_id"])


class SmsNotificationAdapter(NotificationSender):
    def __init__(self, sms_gateway: SmsGateway):
        self.sms_gateway = sms_gateway

    def send(self, contact: BotUserContact, message: BotMessage) -> DeliveryReceipt:
        if not contact.phone:
            raise ValueError("Phone number is required")
        status_code = self.sms_gateway.push(contact.phone, message.body)
        if status_code != 202:
            raise RuntimeError("SMS gateway rejected the message")
        return DeliveryReceipt(
            "sms", contact.phone, f"sms:{contact.phone}:{status_code}"
        )


class DeadlineReminderService:
    """Bot service that does not know which notification API is used."""

    def __init__(self, sender: NotificationSender):
        self.sender = sender

    def remind(self, contact: BotUserContact, task: Task) -> DeliveryReceipt:
        deadline = task.deadline.isoformat() if task.deadline else "no deadline"
        message = BotMessage(
            title="Task deadline reminder",
            body=f"Task '{task.title}' has deadline: {deadline}.",
        )
        return self.sender.send(contact, message)
