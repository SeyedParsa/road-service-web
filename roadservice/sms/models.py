from django.conf import settings
from kavenegar import KavenegarAPI

from sms.exceptions import SingletonInitError


class SmsSender(KavenegarAPI):
    __instance = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if SmsSender.__instance is not None:
            raise SingletonInitError()
        super().__init__(settings.KAVENEGAR_API_KEY)
        SmsSender.__instance = self

    def send_to_number(self, phone_number, message):
        params = {
            'receptor': phone_number,
            'message': message,
        }
        self.sms_send(params)
