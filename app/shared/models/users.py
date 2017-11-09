from app import db

class Users(db.Document):
    __tablename__       =   'users'
    username            =   db.StringField(required=True,unique=True)
    name                =   db.StringField()
    bio                 =   db.StringField()
    profile_image_url   =   db.StringField()
    website             =   db.StringField()
    followed_by_count   =   db.IntField()
    following_count     =   db.IntField()
    access_token        =   db.StringField()
    meta                =   {
                                'indexes': [
                                            {
                                                'fields': ['$username', '$name', "$bio"],
                                                'default_language': 'english',
                                                'weights': {'username': 1, 'name': 2, 'bio': 10}
                                            }
                                        ]
                            }