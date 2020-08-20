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
    language = peewee.CharField(null=True)
    wallet = peewee.CharField(null=True)

    def update_or_create(user_id, bot_chat_id=None, language=None, wallet=None):
        user = User.get_or_none(User.user_id == user_id)
        if user is None:
            return User.create(user_id=user_id, bot_chat_id=bot_chat_id, language=language, wallet=wallet)

        if bot_chat_id:
            user.bot_chat_id = bot_chat_id
        if language:
            user.language = language
        if bot_chat_id:
            user.wallet = wallet

        user.save()
        return user


class Award(BaseModel):
    user = peewee.ForeignKeyField(User, backref='users')
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
