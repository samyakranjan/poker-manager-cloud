'''
#We shouldn't expose a common functions, instead give them separate endpoints.
class UpdateGroupHandler(webapp2.RequestHandler):
  def post(self):
    try:
      groupKey = utils.GetGroupEntityFromKeyName(self.request.get("key_name"))
      utils.UpdateGroupDetail(self, groupKey)

    except ValueError as ve:
      WriteErrorJson(self, "", ve.message)
      return

    except Exception as e:
      logging.exception("Error occured while updating group details")
      WriteErrorJson(self, str(e))
      return

    WriteSuccessJson(self)

class UpdatePlayerHandler(webapp2.RequestHandler):
  def post(self):
    try:
      playerKey = utils.GetPlayerEntityFromKeyName(self.request.get("key_name"))
      utils.UpdatePlayerDetail(self, playerKey)

    except ValueError as ve:
      WriteErrorJson(self, "", ve.message)
      return

    except Exception as e:
      logging.exception("Error occured while updating player details")
      WriteErrorJson(self, str(e))
      return

    WriteSuccessJson(self)
'''

'''
Deprecated for now
class GoogleWebLoginHandler(BaseHandler):
    def get(self):
        return
        created_at = datetime.utcnow()

        flow = client.flow_from_clientsecrets(
            Secret.CLIENT_SECRET_FILE,
            scope=Google.SCOPE,
            redirect_uri=Redirect.SIGNIN_URL
        )

        authUri = str(flow.step1_get_authorize_url())
        errorCode = self.session.get("error_data")

        #if lang:
            #auth_uri += "&hl=" + str(lang.split("-")[0].lower())

        if errorCode == ReturnCodes.ASK_FOR_CONSENT:
            logging.info("Ask for consent")
            authUri += str(Google.CONSENT_PROMPT)

        logging.info("AuthURL: " + authUri)
        self.redirect(uri=authUri)

class GoogleWebLoginRedirectHandler(BaseHandler):
    def get(self):
        return
        error = str(self.request.get('error', ""))

        if error == "access_denied":
            logging.info("Access Denied")
            self.session["error"] = ReturnCodes.USER_DENIED_ACCESS
            self.redirect(uri=Redirect.DENIED_URL)
            return

        authCode = self.request.get('code')

        try:
            credentials = utils.GetTokenFromAuthCode(authCode)
        except client.FlowExchangeError or httplib.HTTPException as e:
            self.session["error"] = ReturnCodes.CODE_EXCHANGE_ERROR
            self.redirect(uri=Redirect.DENIED_URL)
            return

        email = str(credentials.id_token["email"]).lower()

        if utils.DoesPlayerExist(email):
            logging.info("Player already exists")
            player = utils.GetPlayerEntityFromKeyName(email)

            if player.access_revoked:
                #Handle the users access revoked case. Get a fresh token by reauthenticating
                logging.info("Access revoked for email: " + email)
                if not credentials.refresh_token:
                    player.refresh_token = credentials.refresh_token
                    player.put()
                else:
                    self.session["error_data"] = ReturnCodes.ASK_FOR_CONSENT
                    self.redirect(uri=Redirect.OAUTH2_URL)

        else:
            logging.info("New player")

            if not credentials.refresh_token:
                logging.error("No refresh token")
                self.session["error_data"] = ReturnCodes.ASK_FOR_CONSENT
                self.redirect(uri="/login/oauth2redirect")

            else:
                userProfile = utils.GetGoogleUserInfo(credentials.access_token)

                source = UserSource.WINDOWS
                emailID = CreatePlayer(credentials, userProfile, source)


        self.redirect(uri=Redirect.WELCOME_URL)
'''


'''
def ToBool(s):
    return s.lower() in ['true', '1', 'y', 't', 'yes']

def ToCsv(sList):
    returnStr = ""

    for eachEle in sList:
        returnStr += eachEle + ","

    returnStr = returnStr[:-1]

    return returnStr

def GetTokenFromAuthCode(authCode):
    """Handshake with Google, exchange the authorization code with the access credentials"""
    credentials = client.credentials_from_clientsecrets_and_code(
        filename=Secret.CLIENT_SECRET_FILE,
        scope=Google.SCOPE,
        code=authCode,
        redirect_uri=Redirect.SIGNIN_URL
        )
    return credentials

def GetGoogleUserInfo(token):
    """Get all the user's Google information required to build the profile"""
    response = urlfetch.fetch("{0}={1}".format(Google.GOOGLE_USER_INFO_URL, token), deadline=600)

    profile = json.loads(response.content)
    ret = {}

    if profile.has_key("email"):
        ret["email"] = str(profile["email"]).lower()
    else:
        raise ValueError(ReturnCodes.EMAIL_NOT_RECEIVED_IN_USER_INFO)

    if profile.has_key("full_name"):
        ret["player_name"] = profile["name"].strip()
    else:
        ret["player_name"] = "{0} {1}".format(first_name, last_name)

    if profile.has_key("picture"):
        ret["player_picture_url"] = profile["picture"]
    else:
        ret["player_picture_url"] = PokerConstants.DEFAULT_AVATAR_URL

    return ret

def ShouldUpdateGooglePermissions(player):
    """Check whether the google access token is still valid and you don't need to refresh it"""
    tokenTimestamp = player.access_token_expire_check

    #2 days is a relatively safe check. Do we want access more frequently?
    #Is it days or hours? XXX: Verify
    if tokenTimestamp:
        if (datetime.now() - tokenTimestamp).days < 2:
            return False

    refreshToken = player.refresh_token
    payload = {
        "refresh_token": str(refreshToken),
        "client_id": Secret.CLIENT_ID,
        "client_secret": Secret.CLIENT_SECRET,
        "grant_type": "refresh_token"
    }

    try:
        resp = urlfetch.fetch(Google.GOOGLE_ACCESS_TOKEN_RENEW_URL, payload=urllib.urlencode(payload),
                                method=urlfetch.POST, deadline=600)
        response = json.loads(resp.content)
        player.access_token_expire_check = datetime.now()
        player.put()

        if "error" in response.lower():
            return True
        else:
            return False

    except Exception as e:
        logging.exception("Error while getting checking for refresh token")
        return False

def UpdatePlayerDetail(self, entity):
  """This will update all the details of a player which are there in the request."""
  try:
    #Cannot update email for now(Primary Key)
    for eachArg in self.request.arguments():
      if eachArg == "player_name":
        entity.player_name = self.request.get(eachArg)
      elif eachArg == "player_picture_url":
        entity.player_picture_url = self.request.get(eachArg)
      elif eachArg == "groups":
        entity.groups = self.request.get(eachArg)

    entity.timestamp = datetime.utcnow()
    entity.put()

  except Exception as e:
    logging.error("Couldn't update player, err: " + str(e))
    raise ValueError(ReturnCodes.COULD_NOT_UPDATE_PLAYER)

def UpdateGroupDetail(self, entity):
  """This will update all the details of a group which are there in the request"""
  try:
    #Cannot update group_id for now(Primary Key)
    for eachArg in self.request.arguments():
      if eachArg == "group_name":
        entity.group_name = self.request.get(eachArg)
      elif eachArg == "group_owner":
        entity.group_owner = self.request.get(eachArg)
      elif eachArg == "players":
        entity.players = self.request.get(eachArg)
      elif eachArg == "group_picture_url":
        entity.group_picture_url = self.request.get(eachArg)

    entity.timestamp = datetime.utcnow()
    entity.put()

  except Exception as e:
    logging.error("Couldn't update group, err: " + str(e))
    raise ValueError(ReturnCodes.COULD_NOT_UPDATE_GROUP)

def ValidateParams(session, mandatoryParams):
    if not ValidateParams(session, mandatoryParams):
        WriteErrorJson(self, "", ReturnCodes.INCOMPLETE_PARAMETER_PROVIDED)
                return


'''
