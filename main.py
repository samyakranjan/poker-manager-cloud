import sys
import json
import model
import httplib
import logging
import webapp2

import utils
sys.path.insert(0, 'lib')

from constants import *
from datetime import datetime
from oauth2client import client
from webapp2_extras import sessions
from google.appengine.api import users

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

def UserAuthorized(self):
    authKey = self.request.get('auth_id')
    if not authKey or authKey != Secret.SECRET_KEY:
        logging.error("Unauthorized request")
        ShowErrorPage(self)
        return False
    else:
        return True

def ShowErrorPage(self):
    logging.info("Redirecting to: " + self.request.host + Redirect.HELLO_URL)
    self.redirect(self.request.host + Redirect.HELLO_URL)

def WriteSuccessJson(self, data=None):
    out = {}
    out["success"] = True

    if data:
        out.update(data)

    self.response.headers["Content-Type"] = "application/json"
    self.response.status_int = 200
    self.response.write(json.dumps(out))
    logging.info("Writing success json:" + json.dumps(out))

def WriteErrorJson(self, reason, data=None, errorCode=500):
    out = {}
    out["success"] = False
    out["reason"] = reason
    if data:
        out.update(data)

    self.response.status_int = errorCode
    self.response.headers["Content-Type"] = "application/json"
    self.response.write(json.dumps(out))
    logging.info("Writing error json:" + json.dumps(out))

##################################################
#                  Handlers                      #
##################################################

class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        ShowErrorPage(self)

class LoginDeniedHandler(webapp2.RequestHandler):
    def get(self):
        ShowErrorPage(self)

##################################################
#              Player Handlers                   #
##################################################

class PlayerGetDetailsHandler(webapp2.RequestHandler):
    def post(self):
        try:
            mandatoryParams = ["email"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            playerDetails = utils.GetPlayerDetails(self.request.get("email"))

            WriteSuccessJson(self, playerDetails)

        except ValueError as ve:
            WriteErrorJson(self, "", ve.message)

        except Exception as e:
            logging.exception("Error occured while getting player details")
            WriteErrorJson(self, str(e))

class PlayerUpdateHandler(webapp2.RequestHandler):
    def post(self):
        try:
            mandatoryParams = ["email"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            utils.UpdatePlayerDetails(self.request)

            WriteSuccessJson(self)

        except ValueError as ve:
            WriteErrorJson(self, "", ve.message)

class PlayerGetExistingFriendsHandler(webapp2.RequestHandler):
    def post(self):
        try:
            mandatoryParams = ["email", "email_list"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            returnList = []
            for eachEmail in json.loads(email_list):
                if utils.DoesPlayerExist(eachEmail):
                    returnList.append(utils.GetPlayerPictureAndName(eachEmail))

            returnJson = { "existing_players": returnList }

            WriteSuccessJson(self, returnJson)

        except ValueError as ve:
            WriteErrorJson(self, "", ve.message)


##################################################
#               Group Handlers                   #
##################################################
class GroupCreateHandler(webapp2.RequestHandler):
    def post(self):
        try:
            mandatoryParams = ["group_name", "group_owner", "players", "time_created"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            for eachParam in mandatoryParams:
                logging.info(self.request.get(eachParam))

            name = self.request.get("group_name")
            owner = self.request.get("group_owner")
            picture = self.request.get("group_picture_url")
            players = json.loads(self.request.get("players"))
            timeCreated = datetime.strptime(self.request.get("time_created"), TIME_FORMAT)

            #Add yourself to the group
            if owner not in players:
                players.append(owner)

            groupID = utils.CreateGroup(name, owner, picture, players, timeCreated)
            utils.AddPlayersToGroup(groupID, players)

        except Exception as e:
            logging.exception("Error occured while creating group")
            WriteErrorJson(self, str(e))
            return

        returnJson = {}
        returnJson["group_id"] = groupID
        returnJson["group_created_at"] = datetime.strftime(timeCreated, TIME_FORMAT)

        WriteSuccessJson(self, returnJson)

class GroupGetDetailsHandler(webapp2.RequestHandler):
    def post(self):
        try:
            mandatoryParams = ["group_id"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            groupDetails = {"group":  utils.GetGroupDetails(self.request.get("group_id")) }
            WriteSuccessJson(self, groupDetails)

        except ValueError as ve:
            WriteErrorJson(self, "", ve.message)

        except Exception as e:
            logging.exception("Error occured while getting group details")
            WriteErrorJson(self, str(e))

class GroupUpdateHandler(webapp2.RequestHandler):
    def post(self):
        try:
            mandatoryParams = ["group_id"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            utils.UpdateGroupDetails(self.request)
            WriteSuccessJson(self)

        except ValueError as ve:
            WriteErrorJson(self, "", ve.message)

class GroupGetSessionsHandler(webapp2.RequestHandler):
    def post(self):
        try:
            mandatoryParams = ["group_id"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            groupID = self.request.get("group_id")
            sessions = utils.GetGroupSessions(groupID)

            returnJson = {}
            returnJson["sessions"] = sessions

            WriteSuccessJson(self, returnJson)

        except Exception as e:
            logging.exception("Error occured while getting the transactions")
            WriteErrorJson(self, e.message)

##################################################
#               Session Handlers                 #
##################################################

class SessionStartHandler(webapp2.RequestHandler):
    def get(self):
        WriteErrorJson(self, "", ReturnCodes.UNAUTHORIZED_REQUEST)
        return

    def post(self):
        try:
            mandatoryParams = ["session_name", "group_id", "player_details", "session_created_by", "session_currency", "created_at"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            returnJson = {}

            createdAt       = datetime.strptime(self.request.get("created_at"), TIME_FORMAT)
            playerDetails   = json.loads(self.request.get("player_details"))
            groupID         = self.request.get("group_id")
            createdBy       = self.request.get("session_created_by")
            name            = self.request.get("session_name")
            currency        = self.request.get("session_currency")
            isActive        = json.loads(self.request.get("session_active"))

            sessionID = utils.CreateSession(name, groupID, playerDetails, createdBy, isActive, currency, createdAt)

            txnIDs = []
            for name,buyin in playerDetails.iteritems():
                txnID = utils.CreateTransaction(sessionID, createdBy, name, buyin, createdAt)

                transaction = {}
                transaction["email"] = name
                transaction["transaction_id"] = txnID
                txnIDs.append(transaction)

            returnJson["session_id"] = sessionID
            returnJson["transactions"] = txnIDs

            WriteSuccessJson(self, returnJson)
            return

        except Exception as e:
            logging.exception("Error occured creating a session")
            WriteErrorJson(self, e.message)
            return

class SessionUpdateHandler(webapp2.RequestHandler):
    def get(self):
        WriteErrorJson(self, "", ReturnCodes.UNAUTHORIZED_REQUEST)
        return

    def post(self):
        try:
            mandatoryParams = ["session_id", "session_currency", "session_name"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            sessionID       = self.request.get("session_id")
            name            = self.request.get("session_name")
            currency        = self.request.get("session_currency")

            sessionObj                      = utils.GetSessionEntityFromID(sessionID)
            sessionObj.session_name         = name
            sessionObj.session_currency     = currency
            sessionObj.session_last_updated = datetime.utcnow()
            sessionObj.put()

            WriteSuccessJson(self)
            return

        except Exception as e:
            logging.exception("Error occured while creating a session")
            WriteErrorJson(self, e.message)
            return


        WriteSuccessJson(self)

class SessionAddPlayersHandler(webapp2.RequestHandler):
    def get(self):
        WriteErrorJson(self, "", ReturnCodes.UNAUTHORIZED_REQUEST)
        return

    def post(self):
        try:
            mandatoryParams = ["session_id", "player_details", "created_at", "created_by"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            returnJson = {}
            playerDetails   = json.loads(self.request.get("player_details"))
            createdBy       = self.request.get("created_by")
            sessionID       = self.request.get("session_id")
            createdAt       = datetime.strptime(self.request.get("created_at"), TIME_FORMAT)

            sessionObj = utils.GetSessionEntityFromID(sessionID)

            txnIDs = []
            for name,buyin in playerDetails.iteritems():
                txnIDs.append(utils.CreateTransaction(sessionID, createdBy, name, buyin, createdAt))
                if name not in sessionObj.players_involved:
                    sessionObj.players_involved.append(name)

            sessionObj.put()

            returnJson["transactions"] = txnIDs

            WriteSuccessJson(self, returnJson)
            return

        except Exception as e:
            logging.exception("Error occured while creating a session")
            WriteErrorJson(self, e.message)
            return


        WriteSuccessJson(self)

class SessionGetTransactionsHandler(webapp2.RequestHandler):
    def get(self):
        WriteErrorJson(self, "", ReturnCodes.UNAUTHORIZED_REQUEST)
        return

    def post(self):
        try:
            mandatoryParams = ["session_id"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            sessionID = self.request.get("session_id")
            transactionsObj = model.Transactions.all().filter("session_id = ", sessionID.strip()).fetch(None)
            returnJson = {}

            transactionsList = []
            if transactionsObj:
                for eachTxn in transactionsObj:
                    txn = {}
                    txn["transaction_by"] = eachTxn.transaction_by
                    txn["transaction_of"] = eachTxn.transaction_of
                    txn["transaction_amount"] = eachTxn.transaction_amount
                    txn["transaction_time"] = eachTxn.transaction_time.strftime(TIME_FORMAT)
                    txn["transaction_id"] = eachTxn.transaction_id

                    transactionsList.append(txn)

            returnJson["session_id"] = sessionID
            returnJson["transactions"] = transactionsList

            WriteSuccessJson(self, returnJson)
            return

        except Exception as e:
            logging.exception("Error occured while getting the transactions")
            WriteErrorJson(self, e.message)
            return

class SessionEndHandler(webapp2.RequestHandler):
    def get(self):
        WriteErrorJson(self, "", ReturnCodes.UNAUTHORIZED_REQUEST)
        return

    def post(self):
        try:
            mandatoryParams = ["session_id", "player_details", "created_by", "created_at"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            returnJson = {}
            createdAt = datetime.strptime(self.request.get("created_at"), TIME_FORMAT)
            playerDetails = json.loads(self.request.get("player_details"))
            createdBy = self.request.get("created_by")
            sessionID = self.request.get("session_id")

            #Create transactions
            txnIDs = []
            for name,buyin in playerDetails.iteritems():
                txnIDs.append(utils.CreateTransaction(sessionID, createdBy, name, buyin, createdAt))

            #Update Session
            sessionObj = utils.GetSessionEntityFromID(sessionID)
            sessionObj.session_ended_at = createdAt
            sessionObj.last_updated = createdAt
            sessionObj.session_active = False
            sessionObj.put()

            returnJson["transactions"] = txnIDs

            WriteSuccessJson(self, returnJson)
            return

        except Exception as e:
            logging.exception("Error occured creating a session")
            WriteErrorJson(self, e.message)
            return

        WriteSuccessJson(self)

class CreateTransactionHandler(webapp2.RequestHandler):
    def get(self):
        WriteErrorJson(self, "", ReturnCodes.UNAUTHORIZED_REQUEST)
        return

    def post(self):
        try:
            mandatoryParams = ["session_id", "transaction_by", "player_details", "created_at"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            sessionID = self.request.get("session_id")
            createdBy = self.request.get("transaction_by")
            playerDetails = json.loads(self.request.get("player_details"))
            createdAt = datetime.strftime(self.request.get("created_at"), TIME_FORMAT)

            txnIDs = []
            for name,buyin in playerDetails.iteritems():
                txnIDs.append(utils.CreateTransaction(sessionID, createdBy, name, buyin, createdAt))

            returnJson["transactions"] = txnIDs

            WriteSuccessJson(self, returnJson)
            return

        except Exception as e:
            logging.exception("Error occured while saving the transaction")
            WriteErrorJson(self, e.message)
            return

        WriteSuccessJson(self)
        return

class UpdateTransactionHandler(webapp2.RequestHandler):
    def get(self):
        WriteErrorJson(self, "", ReturnCodes.UNAUTHORIZED_REQUEST)
        return

    def post(self):
        try:
            mandatoryParams = ["transaction_id", "transaction_hidden", "transaction_amount"]
            if not utils.ValidateParams(self.request, mandatoryParams):
                WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return

            txnID = self.request.get("transaction_id")
            isHidden = json.loads(self.request.get("transaction_hidden"))
            txnAmount = int(self.request.get("transaction_amount"))

            txnObj = model.Transactions.all().filter("transaction_id = ", txnID.strip()).fetch(1)

            if not txnObj:
                WriteErrorJson(self, "", ReturnCodes.TRANSACTION_NOT_FOUND)

            txnObj.transaction_hidden = isHidden
            txnObj.transaction_amount = txnAmount

            txnObj.put()

            WriteSuccessJson(self)
            return

        except Exception as e:
            logging.exception("Error occured while saving the transaction")
            WriteErrorJson(self, e.message)
            return

        WriteSuccessJson(self)
        return

class LoginGoogleAppHandler(webapp2.RequestHandler):
    def post(self):
        try:
            email = self.request.get("email")
            logging.info("email: " + email)

            if utils.DoesPlayerExist(email):
                logging.info("Player already exists")
                utils.UpdatePlayer(self.request)

                ret = utils.GetPlayerDetails(email)
                ret["new_user"] = False

                WriteSuccessJson(self, ret)
                return

            else:
                logging.info("New player")

                source = UserSource.UNKNOWN
                name = self.request.get("displayName")
                picUrl = self.request.get("photoUrl").lower()

                if (self.request.get("device_source").lower() == UserSource.ANDROID):
                    source = UserSource.ANDROID
                elif (self.request.get("device_source").lower() == UserSource.IOS):
                    source = UserSource.IOS

                utils.CreatePlayer(email, name, picUrl, source)

                WriteSuccessJson(self, {"new_user": True})
                return

            WriteErrorJson(self, "Unknown")

        except Exception as e:
            logging.exception("Could not create player")
            WriteErrorJson(self, e.message)

app = webapp2.WSGIApplication([
  ("/",                                 MainPageHandler),
  ("/player/getdetails",                PlayerGetDetailsHandler),
  ("/player/update",                    PlayerUpdateHandler),
  ("/player/getexistingfriends",        PlayerGetExistingFriendsHandler),
  ("/group/create",                     GroupCreateHandler),
  ("/group/getdetails",                 GroupGetDetailsHandler),
  ("/group/update",                     GroupUpdateHandler),
  ("/group/getsessions",                GroupGetSessionsHandler),
  ("/transaction/create",               CreateTransactionHandler),
  ("/transaction/update",               UpdateTransactionHandler),
  ("/session/start",                    SessionStartHandler),
  ("/session/update",                   SessionUpdateHandler),
  ("/session/addplayers",               SessionAddPlayersHandler),
  ("/session/gettransactions",          SessionGetTransactionsHandler),
  ("/session/end",                      SessionEndHandler),
  ("/login/userdenied",                 LoginDeniedHandler),
  ("/login/googleapp",                  LoginGoogleAppHandler)
  #("/login/googleweblogin",             GoogleWebLoginHandler),
  #("/login/googlewebredirect",          GoogleWebLoginRedirectHandler),
],
config=Secret.APP_CONFIG,
debug=True)
