import sys
import json
import uuid
import model
import urllib
import logging

sys.path.insert(0, 'lib')

from constants import *
from datetime import datetime
from oauth2client import client

from google.appengine.api import urlfetch
from google.appengine.api import app_identity

def CreatePlayer(userEmail, name, picture_url, source):
    logging.info("Creating player with email:{0} and source:{1}".format(userEmail, source))

    player                                  = model.Players(email=userEmail, key_name=userEmail)
    player.player_name                      = name
    player.player_picture_url               = picture_url
    player.source                           = source
    player.last_updated                     = datetime.utcnow()
    player.player_created_at                = datetime.utcnow()

    player.put()

def CreateGroup(name, owner, pictureUrl, players, timeCreated):
    logging.info("Creating group")

    groupID = GenerateUID()

    group                           = model.Groups(group_id=groupID, key_name=groupID)
    group.group_name                = name
    group.group_owner               = owner
    group.group_picture_url         = pictureUrl
    group.players                   = players
    group.last_updated              = timeCreated
    group.group_created_at          = timeCreated
    group.group_hidden              = False

    group.put()

    return groupID

def CreateSession(name, groupID, playerDetails, createdBy, isActive, currency, createdAt):
    logging.info("Creating session")

    sessionID = GenerateUID()

    session                         = model.Sessions(session_id=sessionID, key_name=sessionID)
    session.session_name            = name
    session.group_id                = groupID
    session.players_involved        = playerDetails.keys()
    session.session_created_by      = createdBy
    session.session_active          = True
    session.session_currency        = currency
    session.session_created_at      = createdAt
    session.last_updated            = createdAt

    session.put()

    return sessionID

def CreateTransaction(session_id, transaction_by, transaction_of, transaction_amount, txn_time):
    logging.info("Creating transaction")

    txnID = GenerateUID()

    transaction                             = model.Transactions(transaction_id=txnID, key_name=txnID)
    transaction.session_id                  = session_id
    transaction.transaction_by              = transaction_by
    transaction.transaction_of              = transaction_of
    transaction.transaction_amount          = transaction_amount
    transaction.transaction_time            = txn_time

    transaction.put()

    return txnID

def GetPlayerDetails(email):
    playerObj = GetPlayerEntityFromEmail(email)

    player = {}
    player["email"]                         = playerObj.email
    player["player_name"]                   = playerObj.player_name
    player["friends"]                       = playerObj.friends
    player["player_picture_url"]            = playerObj.player_picture_url
    player["player_created_at"]             = playerObj.player_created_at.strftime(TIME_FORMAT)

    playerGroups = playerObj.groups

    if playerGroups:
        groups = []
        for eachGroup in playerGroups:
            groups.append(GetGroupDetails(eachGroup))

        player["groups"] = groups

    return player

def GetGroupDetails(groupID):
    groupObj = GetGroupEntityFromID(groupID)

    group = {}
    group["group_id"]           = groupObj.group_id
    group["group_name"]         = groupObj.group_name
    group["group_owner"]        = groupObj.group_owner
    group["players"]            = groupObj.players
    group["group_picture_url"]  = groupObj.group_picture_url
    group["last_updated"]       = groupObj.last_updated.strftime(TIME_FORMAT)
    group["group_created_at"]   = groupObj.group_created_at.strftime(TIME_FORMAT)
    group["group_hidden"]       = groupObj.group_hidden

    group["sessions"]           = GetGroupSessions(groupID)

    return group

def GetGroupSessions(groupID):

    allSessions = model.Sessions.all().filter("group_id = ", groupID).fetch(None)

    sessions = []
    if allSessions:
        for eachSession in allSessions:
            session = {}
            session["session_id"]           = eachSession.session_id
            session["session_name"]         = eachSession.session_name
            session["session_created_by"]   = eachSession.session_created_by
            session["players_involved"]     = eachSession.players_involved
            session["session_active"]       = eachSession.session_active
            session["session_currency"]     = eachSession.session_currency
            session["session_hidden"]       = eachSession.session_hidden
            session["session_created_at"]   = eachSession.session_created_at.strftime(TIME_FORMAT)
            session["session_last_updated"] = eachSession.session_last_updated.strftime(TIME_FORMAT)

            session["transactions"] = GetSessionTransactions(eachSession.session_id)

            sessions.append(session)

    return sessions

def GetSessionTransactions(sessionID):
    transactions = model.Transactions.all().filter("session_id = ", sessionID.strip()).fetch(None)

    transactionsList = []
    if transactions:
        for eachTxn in transactions:
            transaction = {}
            transaction["transaction_id"]       = eachTxn.transaction_id
            transaction["transaction_by"]       = eachTxn.transaction_by
            transaction["transaction_of"]       = eachTxn.transaction_of
            transaction["transaction_amount"]   = eachTxn.transaction_amount
            transaction["transaction_time"]     = eachTxn.transaction_time.strftime(TIME_FORMAT)
            transaction["transaction_hidden"]   = eachTxn.transaction_hidden

            transactionsList.append(transaction)

    return transactionsList

def UpdatePlayer(req):
    """This will update the player when he logs in again"""
    try:
        email = req.get("email")
        playerKey = GetPlayerEntityFromEmail(email)

        pName = req.get("displayName")
        photo = req.get("photoUrl")
        token = req.get("access_token")

        playerKey.player_name = pName
        playerKey.player_picture_url = photo
        playerKey.access_token = token
        playerKey.last_updated = datetime.utcnow()

        playerKey.put()

    except Exception as e:
        logging.exception("Could not update player")
        raise ValueError(ReturnCodes.COULD_NOT_UPDATE_PLAYER)

def UpdatePlayerDetails(req):
    """This will update the player's key details."""
    try:
        email = req.get("email")
        playerKey = GetPlayerEntityFromEmail(email)

        #validParams = ["player_name", "player_picture_url", "groups"]

        if req.get("displayName"):
            playerKey.player_name = req.get("player_name")
        if req.get("photoUrl"):
            playerKey.player_picture_url = req.get("photoUrl")
        if req.get("friend"):
            for eachFriend in json.loads(req.get("friend")):
                playerKey.friends.append(eachFriend)
        if req.get("group"):
            groupID = req.get("group")
            groupObj = GetGroupEntityFromID(groupID)

            if not groupID in playerKey.groups:
                playerKey.groups.append(req.get("group"))

            if not email in groupObj.players:
                groupObj.players.append(email)
                groupObj.last_updated = datetime.utcnow()

                groupObj.put()

        playerKey.last_updated = datetime.utcnow()
        playerKey.put()

    except Exception as e:
        logging.exception("Could not update player")
        raise ValueError(ReturnCodes.COULD_NOT_UPDATE_PLAYER)

def UpdateGroupDetails(req):
    """This will update the group's key details."""
    try:
        #group_name, player, group_picture_url, group_hidden     

        groupKey = GetGroupEntityFromID(req.get("group_id"))
        #validParams = ["group_name", "player", "group_picture_url", "group_hidden"]

        if req.get("group_name"):
            groupKey.group_name = req.get("group_name")
        if req.get("players"):
            groupKey.players = groupKey.players + json.loads(req.get("players"))
        if req.get("group_picture_url"):
            groupKey.group_picture_url = req.get("group_picture_url")
        if req.get("group_hidden"):
            groupKey.group_hidden = json.loads(req.get("group_hidden"))

        groupKey.last_updated = datetime.utcnow()
        groupKey.put()

    except Exception as e:
        logging.exception(str(e))
        raise ValueError(ReturnCodes.COULD_NOT_UPDATE_GROUP)

def AddPlayersToGroup(groupID, playerList):
    for player in playerList:
        playerKey = GetPlayerEntityFromEmail(player)
        playerKey.groups.append(groupID)
        playerKey.put()

def GenerateUID():
    """This will generate a unique ID which will be assigned"""
    return str(uuid.uuid1()).lower()

def DoesPlayerExist(email):
    """This will return a boolean whether a player exists or not"""
    entity = model.Players.get_by_key_name(email)
    if not entity:
        return False

    return True

def GetPlayerPictureAndName(email):
    player = model.Players.get_by_key_name(email)
    returnJson = {}

    returnJson["player_name"] = player.player_name
    returnJson["player_picture_url"] = player.player_picture_url

    return returnJson

def GetPlayerEntityFromEmail(email):
    """This will return a player entity object from the key name. If not found, will raise a PLAYER_NOT_FOUND ValueError exception"""
    entity = model.Players.get_by_key_name(email)
    if not entity:
        raise ValueError(ReturnCodes.PLAYER_NOT_FOUND)

    return entity

def GetGroupEntityFromID(keyName):
    """This will return a group entity object from the key name. If not found, will raise a GROUP_NOT_FOUND ValueError exception"""
    entity = model.Groups.get_by_key_name(keyName)
    if not entity:
        raise ValueError(ReturnCodes.GROUP_NOT_FOUND)

    return entity

def GetSessionEntityFromID(keyName):
    """This will return a group entity object from the key name. If not found, will raise a SESSION_NOT_FOUND ValueError exception"""
    entity = model.Sessions.get_by_key_name(keyName)
    if not entity:
        raise ValueError(ReturnCodes.SESSION_NOT_FOUND)

    return entity

def GetTransactionEntityFromID(keyName):
    """This will return a txn entity object from the key name. If not found, will raise a TRANSACTION_NOT_FOUND ValueError exception"""
    entity = model.Sessions.get_by_key_name(keyName)
    if not entity:
        raise ValueError(ReturnCodes.SESSION_NOT_FOUND)

    return entity

def ValidateParams(session, params):
    for eachParam in params:
        logging.info("Validating: " + eachParam)
        if not session.get(eachParam):
            return False

    return True

def AuthenticateUser(self, targetURL=''):
    """Check if the user is authorized, and if he's not"""
    #WebUI??
    user = users.get_current_user()
    if user:
        if user.email() in Secret.AUTH_USERS:
            ShowErrorPage(self)
            return False
        else:
            return user.email()
    else:
        self.response.headers["Content-Type"] = "text/html"
        self.response.out.write("Please <a href=" + users.create_login_url(targetURL) + ">Login</a>")
        return False
