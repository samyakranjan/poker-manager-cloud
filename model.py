from constants import *
from google.appengine.ext import db

'''
Players are unique. Players can create groups.
Each group will have multiple sessions
A session will essentially be a game played. It will have multiple transactions unique for every user
'''

class Players(db.Model):
    '''All the players'''
    email                           = db.EmailProperty(required=True)                   # Email-ID of the player (Primary Key)
    player_name                     = db.StringProperty(default="Player")               # Name of the Player
    player_picture_url              = db.StringProperty()                               # Profile Picture
    source                          = db.StringProperty(default=UserSource.UNKNOWN)     # Source where the profile was created from (UserSourceConstant)
    groups                          = db.StringListProperty(default=[])                 # User is part of the following groups
    friends                         = db.StringListProperty(default=[])                 # User is friends with the following
    last_updated                    = db.DateTimeProperty()                             # Timestamp of Transaction
    player_created_at               = db.DateTimeProperty()                             # Time at which the player joined
    player_auth_token               = db.StringProperty()                               # User's Auth token through which all calls will be made. TO IMPLEMENT

class Groups(db.Model):
    '''Groups which are created by the user'''
    group_id                        = db.StringProperty(required=True)                  # Unique ID of the group (Primary Key)
    group_name                      = db.StringProperty()                               # Name of the group
    group_owner                     = db.StringProperty()                               # Owner of the group
    players                         = db.StringListProperty(default=[])                 # List of Players in the group
    group_picture_url               = db.StringProperty()                               # Picture of the group
    last_updated                    = db.DateTimeProperty()                             # Timestamp of Transaction
    group_created_at                = db.DateTimeProperty()                             # Time at which the group detail was updated
    group_hidden                    = db.BooleanProperty(default=False)                 # Time at which the group detail was updated

class Sessions(db.Model):
    '''Session details which have a game involved'''
    session_id                      = db.StringProperty(required=True)                  # Unique ID of the session (Primary Key)
    group_id                        = db.StringProperty()                               # Group ID for which it's a part of
    session_name                    = db.StringProperty()                               # Refresh Token got by GoogleAuth
    session_created_by              = db.EmailProperty()                                # If the session is active or not
    players_involved                = db.StringListProperty(default=[])                 # The players playing in that session
    session_active                  = db.BooleanProperty(default=True)                  # If the session is active or not
    session_currency                = db.StringProperty()                               # Currency
    session_hidden                  = db.BooleanProperty(default=False)                 # Whether it's hidden/deleted or not
    session_created_at              = db.DateTimeProperty()                             # Time at which the game started
    session_last_updated            = db.DateTimeProperty()                             # Time of the last transaction, modification
    session_ended_at                = db.DateTimeProperty(default=None)                 # Time at which the game ended

class Transactions(db.Model):
    '''Each player's transaction in a session'''
    transaction_id                  = db.StringProperty(required=True)                  # Unique ID of the transaction (Primary Key)
    session_id                      = db.StringProperty()                               # Unique ID of the session the txn is part of
    transaction_by                  = db.EmailProperty()                                # Email-ID of the person who initiated the transaction
    transaction_of                  = db.EmailProperty()                                # The JSon of the transaction which occured { 'email': 'amount' }
    transaction_amount              = db.IntegerProperty()                              # The JSon of the transaction which occured { 'email': 'amount' }
    transaction_time                = db.DateTimeProperty()                             # Time at which the transaction happened
    transaction_hidden              = db.BooleanProperty()                              # Whether it's hidden/deleted or not
