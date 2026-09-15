from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend


class EmailBackend(ConsoleEmailBackend):

    def write_message(self, message):
        message.encoding = "utf-8"

        print("\n========== EMAIL ==========")
        print(message.body)
        print("===========================\n")

        return super().write_message(message)