from smtplib import SMTPException
from email.errors import MessageError
from hotel_business_module.utils.email_sender import send_email
import logging
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
email_logger = logging.getLogger('email_logger')


def send_email_to_user(send_to: str, subject: str, content: str):
    """
    Задача для отправки письм
    :param send_to:
    :param subject:
    :param content:
    :return:
    """
    email_logger.info(f'Отправка письма пользователю {send_to[0:4]}***')
    try:
        send_email(subject=subject, content=content, send_to=send_to)
    except (SMTPException, MessageError) as err:
        email_logger.error(f'Ошибка при отправке письма пользователю {send_to[0:4]}***. {str(err)}')
