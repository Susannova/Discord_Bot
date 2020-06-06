import time

class PlayRequest():
    subscriber_ids = []

    def __init__(self, message_id: int, author_id: int, category: str):
        self.message_id = message_id
        self.author_id = author_id
        self.timestamp_ = time.time()
        self.category = category
        self.clash_date = ''

    def add_clash_date(self, clash_date):
        if self.category == "clash":
            self.clash_date = clash_date

    def add_subscriber_id(self, user_id: int):
        self.subscriber_ids.append(user_id)

    def remove_subscriber_id(self, user_id: int):
        self.subscriber_ids.remove(user_id)

    def generate_all_players(self):
        for subscriber in self.subscriber_ids:
            yield subscriber
        yield self.author_id


    def is_already_subscriber(self, user):
        if user.id in self.subscriber_ids:
            return True
        return False

    def is_play_request_author(self, user):
        if user.id == self.author_id:
            return True
        return False