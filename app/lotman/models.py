from .db import MongoConnector
from werkzeug.security import generate_password_hash, check_password_hash
from itertools import permutations
from datetime import datetime, timedelta

class Log(MongoConnector):
    def __init__(self, uid, data):
        self.fields = ['uid', 'data', 'created_at']
        self.uid = uid
        self.data = data
        MongoConnector.__init__(self)

class AdminUser(MongoConnector):
    def __init__(self, email="", passwd="", confirmPasswd=""):
        self.fields = ['email', 'passwd', 'created_at']
        self.email = email
        self.passwd = passwd
        self.comfirmPasswd = confirmPasswd
        MongoConnector.__init__(self)

    def commit(self):
        if self.passwd != self.comfirmPasswd:
            raise Exception("passwd not match")
        else:
            self.passwd = generate_password_hash(self.passwd)
            MongoConnector.commit(self)

    def checkPasswd(self, passwd):
        return check_password_hash(self.passwd, passwd)


class Buyer(MongoConnector):
    def __init__(self, tel="", account="", bank="", nickName=""):
        self.fields = ['tel', 'account', 'bank', 'nickName', 'created_at']
        self.tel = tel
        self.account = account
        self.bank = bank
        self.nickName = nickName
        MongoConnector.__init__(self)

class Order(MongoConnector):
    def __init__(self, buyer=None, numbers="", period=None, messageId=None):
        self.fields = ['buyer', 'numbers',  'period', 'isConfirm',  'created_at', 'messageId']
        self.buyer = buyer
        self.numbers = numbers
        self.period = period
        self.isConfirm = False
        self.messageId = messageId
        MongoConnector.__init__(self)

    def confirm(self):
        self.isConfirm = True

    def cancel(self):
        self.isConfirm = False

class LotConfig(MongoConnector):
    def __init__(self, hi="", front3=[], tail3=[], tail2="", period=None):
        self.fields = ['hi', 'front3', 'tail3',  'tail2',  'prize', 'specialNo','numbers', 'period', 'closeNumbers', 'setLimit','created_at', 'isActive']
        self.hi = hi
        self.front3 = front3
        self.tail3 = tail3
        self.tail2 = tail2
        self.prize = {}
        self.specialNo = []
        self.numbers = {}
        self.period = period
        self.closeNumbers = []
        self.setLimit = []
        self.isActive = False
        self.prize = {
            '3hi': 800,
            '3lo': 400,
            '2hilo': 92,
            'swap': 150,
            'runhi': 5,
            'runlo': 5
        }
        MongoConnector.__init__(self)

    def calNumbers(self):
        self.numbers = {}
        self.numbers['3hi'] = [self.hi[-3:]]
        self.numbers['3lo']  =  self.front3 + self.tail3
        self.numbers['2hi'] = [self.hi[-2:]]
        self.numbers['2lo'] = [self.tail2]
        self.numbers['swap3hi'] = [''.join(p) for p in permutations(self.hi[-3:])]
        self.numbers['swap2hi'] = [''.join(p) for p in permutations(self.hi[-3:], 2)]
        self.numbers['swap2lo'] = [''.join(p) for p in permutations(self.tail2)]
        self.numbers['runhi'] = [self.hi[3], self.hi[4], self.hi[5]]
        self.numbers['runlo'] = [self.tail2[0], self.tail2[1]]
        self.commit()


class OrderStat(MongoConnector):
    def __init__(self, no="", totalBetSize=0, nBets=0, period=None):
        self.fields = ['no', 'totalBetSize', 'nBets', 'period', 'created_at']

        self.no = no
        self.totalBetSize = totalBetSize
        self.nBets = nBets
        self.period = period

        MongoConnector.__init__(self)


class LineEvent(MongoConnector):
    def __init__(self, event=None, profile=None):
        #self.tblName = self.__class__.__name__
        self.fields = ['event', 'profile', 'created_at']
        self.event = event
        self.profile = profile
        MongoConnector.__init__(self)

if __name__ == "__main__":
    l = Log(uid=123, data={'from': 1, 'to': 2})
    l.commit()

    AdminUser.deleteAll()

    u = AdminUser(email="patumos@hotmail.com", passwd='dbovtwisinvpy', confirmPasswd='dbovtwisinvpy')
    u.commit()

    u = AdminUser(email="johndoe@mail.com", passwd='dbovtwisinvpy', confirmPasswd='dbovtwisinvpy')
    u.commit()

    lc = LotConfig(period=datetime(2021,1,15))
    lc.isActive = True
    lc.commit()



