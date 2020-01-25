import time, re, hashlib


class AuthToken():
    __DEFAULT_EXPIRED_TIME_INTERVAL = 1 * 60
    __token = ''

    def __init__(self, token='', createTime=time.time()):
        self.__expiredTimeInterval = self.__DEFAULT_EXPIRED_TIME_INTERVAL
        self.__token = token
        self.__createTime = int(createTime)
        return

    def generate(self, baseUrl, appId, password, timestamp):
        self.__baseUrl = baseUrl
        self.__appId = appId
        self.__password = password
        self.__createTime = int(timestamp)
        return self.create()

    def create(self):
        if self.__password:
            Url = '{}&appid={}&token={}&ts={}'.format(self.__baseUrl, self.__appId, self.__password, self.__createTime)
            self.__token = hashlib.sha256(Url.encode('utf-8')).hexdigest()
        return self.__token

    def getToken(self):
        return str(self.__token)

    def isExpired(self):
        return self.__createTime > time.time() + self.__DEFAULT_EXPIRED_TIME_INTERVAL

    def match(self, token):
        return str(token) == self.getToken()


class ApiRequest():
    def createFromFullUrl(self, url):
        try:
            urlReg = re.findall(re.compile(r'(.*?)&appid=(.*?)&token=(.*?)&ts=(\d+?)', re.S), url)[0]
            self.__baseUrl = urlReg[0]
            self.__appId = urlReg[1]
            self.__token = urlReg[2]
            self.__timestamp = urlReg[3]
        except IndexError:
            raise IndexError
        return

    def getBaseUrl(self):
        return self.__baseUrl

    def getToken(self):
        return self.__token

    def getAppId(self):
        return self.__appId

    def getTimestamp(self):
        return self.__timestamp


class CredentialStorage():
    def getPasswordByAppId(self, appId):
        return '123'


class DefaultApiAuthenticator():
    def DefaultApiAuthenticator(self):
        self.credentialStorage = CredentialStorage()
        return

    def auth(self, Url):
        apiRequest = ApiRequest()
        apiRequest.createFromFullUrl(Url)
        appId = apiRequest.getAppId()
        token = apiRequest.getToken()
        timestamp = apiRequest.getTimestamp()
        baseUrl = apiRequest.getBaseUrl()

        clientAutoToken = AuthToken(token, timestamp)
        if clientAutoToken.isExpired():
            raise runtimeError('token expired')
        password = CredentialStorage().getPasswordByAppId(appId)

        serverAuthToken = AuthToken()
        serverAuthToken.generate(baseUrl, appId, password, timestamp)

        if not serverAuthToken.match(token):
            raise runtimeError('token not matched')

        return


if __name__ == '__main__':
    Url = 'http://api.billyu.cn/auth?id=123&appid=abc&token=xxx&ts={}'.format(int(time.time()))
    DefaultApiAuthenticator().auth(Url)
    Url = 'http://api.billyu.cn/auth?id=123&appid=abc&token' \
          '=5721a6183dfbc0e5b699da8b27e1fb709448a16575ebfa4901f0d481961ed7ed&ts={}'.format(int(time.time()))
    DefaultApiAuthenticator().auth(Url)
