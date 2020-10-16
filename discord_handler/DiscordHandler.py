import logging
import json
from socket import gethostname

try:
    import requests
except ImportError as ex:
    print("Please Install requests")
    raise ImportError(ex)


class DiscordHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a Discord Server using webhooks.
    """

    def __init__(self, webhook_url, agent=None, notify_users=None):
        logging.Handler.__init__(self)

        if webhook_url is None or webhook_url == "":
            raise ValueError(
                "webhook_url parameter must be given and can not be empty!"
            )

        if agent is None or agent == "":
            agent = gethostname()

        if notify_users is None:
            notify_users = []

        self._notify_users = notify_users
        self._url = webhook_url
        self._agent = agent
        self._header = self.create_header()
        self._name = ""

    def create_header(self):
        return {
            'User-Agent': self._agent,
            "Content-Type": "application/json"
        }

    def write_to_discord(self, message):
        content = json.dumps({"content": message})

        request = requests.post(self._url,
                                headers=self._header,
                                data=content)

        if request.status_code == 404:
            raise requests.exceptions.InvalidURL(
                "This URL seams wrong... Response = %s" % request.text)

        if request.ok is False:
            raise requests.exceptions.HTTPError(
                "Request not successful... Code = %s, Message = %s"
                % request.status_code, request.text
            )

    def emit(self, record):
        try:
            msg = self.format(record)
            users = ''
            for user in self._notify_users:
                users = '<@%s>\n%s' % (user, users)

            self.write_to_discord("```%s```%s" % (msg, users))
        except Exception:
            self.handleError(record)