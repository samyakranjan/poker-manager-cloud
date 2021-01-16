TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class Secret:       # This is a placeholder class
    SECRET_KEY                      = ""
    AUTH_USERS                      = ["", ""]
    CLIENT_SECRET_FILE              = ""
    CLIENT_ID                       = ""
    CLIENT_SECRET                   = ""
    APP_CONFIG                      = { "1": { "2": "3" } }

class Redirect:
    ''' Authorized Redirect URL's '''
    SIGNIN_URL                      = "/login/signin"
    DENIED_URL                      = "/login/userdenied"
    OAUTH2_URL                      = "/login/oauth2redirect"
    WELCOME_URL                     = "/welcome"
    HELLO_URL                       = "/error"

class ReturnCodes:
    UNAUTHORIZED_REQUEST            = {"exitcode": 101, "reason": "UNAUTHORIZED_REQUEST"}

    PLAYER_NOT_FOUND                = {"exitcode": 110, "reason": "PLAYER_NOT_FOUND"}
    GROUP_NOT_FOUND                 = {"exitcode": 111, "reason": "GROUP_NOT_FOUND"}
    SESSION_NOT_FOUND               = {"exitcode": 112, "reason": "SESSION_NOT_FOUND"}
    TRANSACTION_NOT_FOUND           = {"exitcode": 113, "reason": "TRANSACTION_NOT_FOUND"}

    COULD_NOT_UPDATE_GROUP          = {"exitcode": 105, "reason": "COULD_NOT_UPDATE_GROUP"}
    COULD_NOT_UPDATE_PLAYER         = {"exitcode": 106, "reason": "COULD_NOT_UPDATE_PLAYER"}
    PLAYER_ALREADY_EXISTS           = {"exitcode": 107, "reason": "PLAYER_ALREADY_EXISTS"}
    GROUP_ALREADY_EXISTS            = {"exitcode": 108, "reason": "GROUP_ALREADY_EXISTS"}
    INVALID_GROUP_KEY               = {"exitcode": 109, "reason": "INVALID_GROUP_KEY"}
    INVALID_PLAYER_KEY              = {"exitcode": 110, "reason": "INVALID_PLAYER_KEY"}
    INVALID_PARAMETER_PROVIDED      = {"exitcode": 111, "reason": "INVALID_PARAMETER_PROVIDED"}
    INCOMPLETE_PARAMETER_PROVIDED   = {"exitcode": 112, "reason": "INCOMPLETE_PARAMETER_PROVIDED"}
    USER_DENIED_ACCESS              = {"exitcode": 113, "reason": "USER_DENIED_ACCESS"}
    CODE_EXCHANGE_ERROR             = {"exitcode": 114, "reason": "CODE_EXCHANGE_ERROR"}
    ASK_FOR_CONSENT                 = {"exitcode": 115, "reason": "ASK_FOR_CONSENT"}
    EMAIL_NOT_RECEIVED_IN_USER_INFO = {"exitcode": 116, "reason": "EMAIL_NOT_RECEIVED_IN_USER_INFO"}
    PERMISSION_REVOKED              = {"exitcode": 117, "reason": "PERMISSION_REVOKED"}

class Google:
    GOOGLE_USER_INFO_URL            = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token"
    GOOGLE_USER_INFO_URL2           = "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token"
    GOOGLE_ACCESS_TOKEN_RENEW_URL   = "https://www.googleapis.com/oauth2/v4/token"
    SCOPE                           = ['openid', 'profile', 'email']
    CONSENT_PROMPT                  = "&prompt=consent"
    ACCOUNT_PROMPT                  = "&prompt=select_account"

class UserSource:
    WINDOWS                         = "windows"
    ANDROID                         = "android"
    IOS                             = "ios"
    UNKNOWN                         = "unknown"

class PokerConstants:
    DEFAULT_AVATAR_URL              = ""
