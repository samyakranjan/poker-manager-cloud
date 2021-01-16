import json
import datetime
import requests

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def Get(url, headers, timeout=10):
    try:
        if not headers:
            r = requests.get(url, timeout=timeout)
        else:
            r = requests.get(url, headers=headers, timeout=timeout)

        return r.text

        '''
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        data = res.read()

        return data
        '''

    except Exception, e:
        print("Error in getting HTTP Data\n" + str(e))
        return ""

def Post(url, headers, body, timeout=10):
    try:
        if not headers:
            if not body:
                r = requests.post(url, timeout=timeout)
            else:
                r = requests.post(url, data=body, timeout=timeout)

        else:
            r = requests.post(url, headers=headers, data=body, timeout=timeout)
            print("Headers: " + str(headers))
            print("body: " + str(body))

        print r.text
        return r.text

    except Exception, e:
        print("Error in getting HTTP Data\n" + str(e))
        return ""

BASEURL = "http://localhost:8090/"

def CreatePlayer(email, photoUrl, name, source):
    url = BASEURL + "login/googleapp"

    data = {}
    data["email"]               = email
    data["photoUrl"]            = photoUrl
    data["displayName"]         = name
    data["device_source"]       = source

    return Post(url, None, data)


def CreateGroup(name, owner, players, picture=None):
    url = BASEURL + "group/create"

    data = {}
    data["group_name"]          = name
    data["group_owner"]         = owner
    data["players"]             = players

    if picture:
        data["group_picutre_url"]   = name

    return Post(url, None, data)

def GetGroupDetails(groupID):
    url = BASEURL + "group/getdetails"

    data = {}
    data["group_id"]             = groupID

    return Post(url, None, data)

def StartSession(name, groupID, playerDetails, createdBy, currency, createdAt):
    url = BASEURL + "session/start"

    data = {}
    data["session_name"]        = name
    data["group_id"]            = groupID
    data["player_details"]      = json.dumps(playerDetails)
    data["session_created_by"]  = createdBy
    data["session_currency"]    = currency
    data["created_at"]          = createdAt

    return Post(url, None, data)

def UpdateSession(sID, name, currency):
    url = BASEURL + "session/update"

    data = {}
    data["session_id"]          = sID
    data["session_name"]        = name
    data["session_currency"]    = currency

    return Post(url, None, data)

def AddPlayersSession(sID, playerDetails, createdBy, createdAt):
    url = BASEURL + "session/addplayers"

    data = {}
    data["session_id"]          = sID
    data["player_details"]      = json.dumps(playerDetails)
    data["created_at"]          = createdAt
    data["created_by"]          = createdBy

    return Post(url, None, data)

def GetSessionTransactions(sID):
    url = BASEURL + "session/gettransactions"

    data = {}
    data["session_id"]          = sID

    return Post(url, None, data)

def EndSession(sID, playerDetails, timeat, createdBy):
    url = BASEURL + "session/end"

    data = {}
    data["session_id"]          = sID
    data["player_details"]      = json.dumps(playerDetails)
    data["created_at"]          = timeat.strftime(TIME_FORMAT)
    data["created_by"]          = createdBy

    return Post(url, None, data)

def GetPlayerDetails(pID):
    url = BASEURL + "player/getdetails"

    data = {}
    data["email"]          = pID

    return Post(url, None, data)

def UpdatePlayer(pID, name="", pic="", group=""):
    url = BASEURL + "player/update"

    data = {}
    data["email"]           = pID
    #data["displayName"]     = name
    #data["photoUrl"]        = pic
    data["group"]           = group

    return Post(url, None, data)

def UpdateGroup(gID, name="", players=[], pic="", hidden=True):
    url = BASEURL + "group/update"

    data = {}
    data["group_id"]            = gID
    data["group_name"]          = name
    data["players"]             = json.dumps(players)
    data["group_picture_url"]   = pic
    data["group_hidden"]        = json.dumps(hidden)

    return Post(url, None, data)

if __name__ == "__main__":
    vikramEmail = "vikram@bst.com"
    myEmail     = "m.r@gmail.com"
    noobieEmail = "noobie@gmail.com"
    randomEmail = "someuser@gmail.com"

    groupID     = "5bc7a0ab-54f2-11e7-9095-17fa2f45a70c"
    groupID2    = "93c6d333-54ec-11e7-9eb5-e30a7fffaeb6"
    sessionID   = "554f3d0c-5501-11e7-a061-39853acdfddb"

    CreatePlayer(myEmail, "http://sammu.jpg", "Samyak Ranjan", "android")
    CreatePlayer(vikramEmail, "http://vikram.jpg", "VikG", "ios")
    CreatePlayer(noobieEmail, "http://noobie.jpg", "SohA", "android")
    CreatePlayer(randomEmail, "http://foo.jpg", "Some User", "foo")
    #CreatePlayer(noobieEmail, "http://newpicture.jpg", "Some User", "foo")

    #ret = CreateGroup("GroupA", myEmail, json.dumps([vikramEmail, noobieEmail]))
    #groupID = json.loads(ret)["group_id"]
    #GetGroupDetails(groupID)

    #playerDetails = { myEmail: 500, vikramEmail: 500 }
    #playerDetails = { myEmail: 1000, noobieEmail: 500 }
    #playerDetails = { myEmail: -1000, noobieEmail: -500 }

    #StartSession("19thJune", groupID, playerDetails, noobieEmail, "INR", datetime.datetime.utcnow().strftime(TIME_FORMAT))
    #UpdateSession(sessionID, "OldName", "USD")
    #AddPlayersSession(sessionID, playerDetails, myEmail, datetime.datetime.utcnow().strftime(TIME_FORMAT))
    #GetSessionTransactions(sessionID)

    #GetPlayerDetails(myEmail)
    #UpdatePlayer(randomEmail, "SomeName", "www.newurl.com", groupID2)
    #UpdateGroup(groupID2, "SomeName")
    #EndSession(sessionID, playerDetails, datetime.datetime.now(), noobieEmail)
