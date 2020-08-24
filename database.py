import argparse

import peewee

import settings

db = peewee.SqliteDatabase(settings.DATABASE_PATH)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = peewee.IntegerField()
    bot_chat_id = peewee.IntegerField(null=True)
    username = peewee.CharField()
    full_name = peewee.CharField()
    language = peewee.CharField(null=True)
    wallet = peewee.CharField(null=True)

    def create_or_get(user_id, username, full_name, bot_chat_id=None):
        user = User.get_or_none(User.user_id == user_id)
        if user is None:
            return User.create(
                user_id=user_id, bot_chat_id=bot_chat_id,
                language='en', wallet=None,
                username=username, full_name=full_name
            )

        user.bot_chat_id = bot_chat_id
        user.username = username
        user.full_name = full_name

        user.save()
        return user

    def search_by_username(text):
        for user in User.select():
            if text in user.username:
                return user

    def search_by_name(text):
        for user in User.select():
            if text in user.full_name:
                return user

    def update_language(self, new_language):
        self.language = new_language
        self.save()

    def update_wallet(self, new_wallet):
        self.wallet = new_wallet
        self.save()

    def create_award(self, geocash, description=None):
        return Award.create(user=self, geocash=geocash, description=description)

    def drop_awards(self):
        Award.delete().where(Award.user == self)

    def retrieve_awards(self):
        if len(self.awards) == 0:
            return None

        return [
            {
                'geocash': award.geocash,
                'description': award.description
            } for award in self.awards
        ]

    def get_geocash(self):
        if len(self.awards) == 0:
            return None

        return sum([award.geocash for award in self.awards])


class Award(BaseModel):
    user = peewee.ForeignKeyField(User, backref='awards')
    geocash = peewee.IntegerField()
    description = peewee.CharField(null=True, default=None)


def create_tables():
    with db:
        db.create_tables([User, Award])


def make_migrations():
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create_tables',  action="store", required=False)
    parser.add_argument('--make_migrations', action="store", required=False)

    args = parser.parse_args()
    if args.create_tables:
        create_tables()
    if args.make_migrations:
        make_migrations()


if __name__ == '__main__':
    main()
