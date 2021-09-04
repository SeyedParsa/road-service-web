import logging

from django.conf import settings
from kavenegar import KavenegarAPI, APIException, HTTPException

from sms.exceptions import SingletonInitError


class SmsSender:
    __instance = None
    logger = logging.getLogger('SmsSenderLogger')

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if SmsSender.__instance is not None:
            raise SingletonInitError()
        api_key = settings.KAVENEGAR_API_KEY
        self.kavenegar = KavenegarAPI(api_key) if api_key else None
        SmsSender.__instance = self

    def send_to_number(self, phone_number, message):
        params = {
            'receptor': phone_number,
            'message': message,
        }
        if self.kavenegar:
            try:
                self.kavenegar.sms_send(params)
            except (HTTPException, APIException):
                self.logger.error('Could not send the message to %s.' % phone_number)
        else:
            self.logger.warning('The SMS API-Key is not setup correctly.')
