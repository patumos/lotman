from .models import Log, AdminUser, Order, Buyer, LotConfig, OrderStat
from .manager import RootManager, Manager
from itertools import permutations
from datetime import datetime
import sys
from random import randint
from .bc import BuyCommand
from lotman.db import MongoConnector

from faker import Faker
fake = Faker()

def funcName(frame):
    print(frame.f_code.co_name)

class BackendUI:
    pass



class User:
    pass

class NoManager:
    pass

class UserAdminManager(Manager):
    def __init__(self):
        pass


class AlertMan:
    pass

class PrizeMan:
    pass

class Prize:
    pass

class LogMan(Manager):
    def __init__(self):
        pass

    def list(self, **kwargs):
        return Log.find({}, (['created_at', -1]))

    def log(self, uid, data):
        l = Log(uid, data)
        l.commit()

    def create(self, **kwargs):
        pass

    def delete(self, **kwargs):
        pass

    def update(self, **kwargs):
        pass


class BuyerMan(Manager):

    def __init__(self, period):
        self.period = period

    def create(self, **kwargs):
        b = Buyer(**kwargs)
        return b.commit()

        #buyer

        #tel

    def list(self, **kwargs):
        buyers= Buyer.find(kwargs)

        if buyers:
            return buyers
        else:
            return None

    def delete(self, **kwargs):
        return Buyer.deleteAll()

    def update(self, **kwargs):
        pass

class AdminUserMan(Manager):
    def list(self, **kwargs):
        return AdminUser.find(kwargs, [("created_at", -1)])

    def login(self, email, passwd):
        ul = list(AdminUser.find({'email': email}))
        #print("login lot man", file=sys.stderr)
        #print(u, file=sys.stderr)
        if ul:
            u = ul[0]
            if  u.checkPasswd(passwd) == True :
                return u
            else:
                return None
        else:
            return None

    def create(self, **kwargs):
        pass

    def delete(self, **kwargs):
        pass

    def update(self, **kwargs):
        pass

class OrderMan:
    def __init__(self, period, lotConfig):
        self.period = period
        self.lotConfig = lotConfig
        self.nbets = 0
        self.rejects = 0

    def getOrderStat(self, no=None):
        if no:
            return OrderStat.findOne({'period': self.period, 'no': no})
        else:
            return OrderStat.find({'period': self.period}, [("totalBetSize", -1)])

    def resetOrderStat(self):
        return OrderStat.deleteAll({'period': self.period})

    def create(self,buyer, numbers ):

        allows = []

        for n in numbers:
            #print(n)
            self.nbets += 1
            no = n[1]
            betSize = n[2]

            #print(no, betSize)
            #continue

            orderStat = OrderStat.findOne({'period': self.period, 'no': no})

            if orderStat:
                #check limit
                orderStat.totalBetSize += betSize
                orderStat.nBets += 1
                orderStat.commit()
            else:
                orderStat = OrderStat(no, betSize, 1, self.period)
                orderStat.commit()

            isPass = True
            for sl in self.lotConfig.setLimit:
                #print(sl)
                if sl[0] == "*":
                    #print(orderStat.no, orderStat.totalBetSize)
                    if orderStat.totalBetSize > sl[1]:
                        #raise Exception("REACHLIMIT", "*")
                        print(f"REACHLIMIT * > {sl[1]}")
                        isPass = False
                        self.rejects += 1
                        break

                if sl[0] == orderStat.no:
                    if orderStat.totalBetSize > sl[1]:
                        #raise Exception("REACHLIMIT", no)
                        print(f"REACHLIMIT {no} > {sl[1]}")
                        isPass = False
                        self.rejects += 1
                        break

            if isPass == True:
                allows.append(n)


        order = Order(buyer = buyer, numbers = allows, period = self.period)

        return order.commit()

    def delete(self):
        return Order.deleteAll()

    def listAll(self, **kwargs):
        kwargs.update({'period': self.period})
        return Order.find(kwargs, [("created_at", -1)])

class LotConfigMan(Manager):
    def __init__(self, period):
        self.period = period

    def create(self, **kwargs):
        lc = LotConfig(**kwargs)
        lc.commit()

    def list(self, **kwargs):
        return LotConfig.find({}, [("created_at", -1)])


    def findOne(self, **kwargs):
        return LotConfig.findOne(kwargs)

    def delete(self, **kwargs):
        pass

    def update(self, **kwargs):
        pass

    def findOneOrCreate(self, period = None):
        if period == None:
            lotConfig = LotConfig.findOne({'period': self.period})
        else:
            lotConfig = LotConfig.findOne({'period': period})
        print("lotConfig")
        print(lotConfig)
        if lotConfig:
            return lotConfig
        else:
            if period == None:
                lotConfig = LotConfig(period=self.period)
            else:
                lotConfig = LotConfig(period=period)

            lotConfig.commit()
            print(lotConfig, self.period)
            return lotConfig

class LotMan:
    def __init__(self, period):
        self.prize = {
            '3hi': 800,
            '3lo': 400,
            '2hilo': 92,
            'swap': 150,
            'runhi': 5,
            'runlo': 5
        }
        self.specialNo = []
        self.logManager = LogMan()

        self.period = period
        self.adminUserManager = AdminUserMan()
        self.buyerMan = BuyerMan(self.period)
        self.restoreLotConfigActive()
        '''
        self.lotConfigMan = LotConfigMan(self.period)
        self.lotConfig = self.lotConfigMan.findOneOrCreate()
        print("Lot Config")
        print(vars(self.lotConfig))
        '''

        self.orderMan = OrderMan(self.period, self.lotConfig)
        #self.orderMan.resetOrderStat()

        self.numbers = {}

    def setLotConfig(self, lc):
        self.lotConfigMan = LotConfigMan(lc.period)
        self.lotConfig = lc
        self.period = lc.period
        self.orderMan = OrderMan(self.period, self.lotConfig)

    def restoreLotConfigActive(self):
        lc = MongoConnector.db['LotConfig'].find_one({'isActive': True})
        if lc is not None:
            lco = LotConfig.findById(str(lc['_id']))
            self.period = lco.period
            self.setLotConfig(lco)

    def stats(self):
        return self.orderMan.getOrderStat()

    def getConfig(self, period):
        return self.lotConfigMan.findOne(period = period)

    def listConfig(self):
        return self.lotConfigMan.list()

    def listAdminUser(self):
        return self.adminUserManager.list()

    def setNo(self, hi, front3, tail3, tail2):
        self.lotConfig.hi = self.hi = hi
        self.lotConfig.front3 = self.front3 = front3
        self.lotConfig.tail3 = self.tail3 = tail3
        self.lotConfig.tail2 = self.tail2 = tail2

        self.lotConfig.commit()

    def setNoPeriod(self, period, hi, front3, tail3, tail2):

        lotConfig = self.lotConfigMan.findOneOrCreate(period)
        lotConfig.hi = self.hi = hi
        lotConfig.front3 = self.front3 = front3
        lotConfig.tail3 = self.tail3 = tail3
        lotConfig.tail2 = self.tail2 = tail2

        return lotConfig.commit()


    def printNo(self):
        print("Lottery No.")
        print("============")
        print(f"hi = {self.lotConfig.hi}")
        print(f"front3 = {self.lotConfig.front3}")
        print(f"tail3 = {self.lotConfig.tail3}")
        print(f"tail2 = {self.lotConfig.tail2}")

    def printPrize(self):
        print("Prizes")
        print("============")
        print(f"{self.lotConfig.prize}")

    def resetNoLimit(self):
        self.lotConfig.setLimit = []
        self.lotConfig.commit()

    def setPrize(self, pos, prize):
        self.prize[pos] = prize
        self.lotConfig.prize = self.prize
        self.lotConfig.commit()

    def setSpecialNo(self, no, prize):
        self.specialNo.append((no, prize))
        self.lotConfig.specialNo = self.specialNo
        self.lotConfig.commit()



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

        self.lotConfig.numbers = self.numbers
        self.lotConfig.commit()

    def getNumber(self, pos):
        return self.number[pos]

    def acceptBuyCommand(self, bc: BuyCommand):
        if bc.no == "" or len(bc.no) > 3:
            return False

        numbers = []
        if len(bc.no) == 3:
            if bc.spec == "n/a":
                if bc.leaf:
                    numbers.append(["3hi", bc.no, bc.up, "leaf"])
                    #numbers.append(["3lo", bc.no, bc.under])
                    numbers.append(["swap3hi", bc.no, bc.swap, "leaf"])
                else:
                    numbers.append(["3hi", bc.no, bc.up])
                    #numbers.append(["3lo", bc.no, bc.under])
                    numbers.append(["swap3hi", bc.no, bc.swap])
            elif bc.spec == "hi":
                if bc.leaf:
                    numbers.append(["3hi", bc.no, bc.up, "leaf"])
                else:
                    numbers.append(["3hi", bc.no, bc.up])
                #numbers.append(["swap3hi", bc.no, bc.up])
            elif bc.spec == "swap":
                if bc.leaf:
                    numbers.append(["swap3hi", bc.no, bc.swap, "leaf"])
                else:
                    numbers.append(["swap3hi", bc.no, bc.swap])

        elif len(bc.no) == 2:
            if bc.spec == "n/a":
                if bc.leaf:
                    numbers.append(["2hi", bc.no, bc.up, "leaf"])
                    numbers.append(["2lo", bc.no, bc.under, "leaf"])
                else:
                    numbers.append(["2hi", bc.no, bc.up])
                    numbers.append(["2lo", bc.no, bc.under])
                #numbers.append(["swap2hi", bc.no, bc.up])
                #numbers.append(["swap2lo", bc.no, bc.under])
            elif bc.spec == "hi":
                if bc.leaf:
                    numbers.append(["2hi", bc.no, bc.up, "leaf"])
                else:
                    numbers.append(["2hi", bc.no, bc.up])
                #numbers.append(["swap2hi", bc.no, bc.up])
            elif bc.spec == "lo":
                if bc.leaf:
                    numbers.append(["2lo", bc.no, bc.under, "leaf"])
                else:
                    numbers.append(["2lo", bc.no, bc.under])
                #numbers.append(["swap2lo", bc.no, bc.under])
        elif len(bc.no) == 1:
            if bc.spec == "n/a":
                numbers.append(["runhi", bc.no, bc.up])
                numbers.append(["runlo", bc.no, bc.under])
            elif bc.spec == "hi":
                numbers.append(["runhi", bc.no, bc.up])
            elif bc.spec == "lo":
                numbers.append(["runlo", bc.no, bc.under])

        #print(f"numbers = {numbers}")
        order = self.putOrder2(buyer = bc.userName, numbers=numbers)
        if order:
            self.confirmOrder(order)
        return order

    def login(self, email, passwd):
        self.currentUser = self.adminUserManager.login(email,passwd)
        return self.currentUser

    def registerUser(self, passwd, confirmPass):
        return self.adminUserManager.create(email, passwd, confirmPass)

    def loginUser(self, email, passwd):
        pass

    def createBuyer(self, tel="", account="", bank="", nickName=""):
        return self.buyerMan.create(tel=tel, account=account, bank=bank, nickName=nickName)

    def putOrder(self, buyer,  numbers):
        try:
            return self.orderMan.create(buyer=buyer.tel, numbers=numbers)
        except Exception as e:
            print(e)
            return None

    def putOrder2(self, buyer,  numbers):
        try:
            return self.orderMan.create(buyer=buyer, numbers=numbers)
        except Exception as e:
            print(e)
            return None

    def orderIsValid(self, order):
        return True

    def checkPrize(self, order):
        #funcName(sys._getframe())
        result = []
        #print(f"order numbers = {order.numbers}")
        if order.isConfirm == False:
            return result

        if order.isConfirm == True:
            for number in order.numbers:
                #print(f"number = {number}")
                p0 = number[0]
                p1 = number[1]
                p2 = number[2]
                #print(f"=== ({p0}, {p1}, {p2}) ===")
                if p1 in self.lotConfig.numbers[p0]:
                    pz = p0
                    if p0 in ["2hi", "2lo"]:
                        pz = "2hilo"
                    if "swap" in p0:
                        pz = "swap"

                    result.append((p0, p1, p2, p2*self.lotConfig.prize.get(pz)))
                    #print(f"({p0}, {p1}, {p2})", end="")
                    print(f"{p1}", end="")
                else:
                    print(".", end="")
                    #print("Wrong")
            return result

    def checkPrize2(self, order):
        #funcName(sys._getframe())
        result = []
        #print(f"order numbers = {order.numbers}")
        if order.isConfirm == False:
            return result

        if order.isConfirm == True:
            #print(f"numbers => {order.numbers}")
            for number in order.numbers:
                #print(f"number = {number}")
                p0 = number[0]
                p1 = number[1]
                p2 = number[2]
                #print("p1, p2", file=sys.stderr)
                #print(number, file=sys.stderr)
                #print(f"=== ({p0}, {p1}, {p2}) ===")
                for k in self.lotConfig.numbers.keys():
                    for v in self.lotConfig.numbers[k]:
                        isHiPrize = "hi" in k
                        isHiNum = "hi" in p0

                        isLowPrize = "lo" in k
                        isLowNum = "lo" in p0

                        if p1 == v:

                            if isHiPrize != isHiNum:
                                continue
                            if isLowPrize != isLowNum:
                                continue

                            pz = k
                            if k in ["2hi", "2lo"]:
                                pz = "2hilo"
                            if "swap" in k:
                                pz = "swap"

                            #print(f"lotconfig {pz} {self.lotConfig.prize}", file=sys.stderr)
                            #print(self.lotConfig.prize.get(pz), file=sys.stderr)
                            t12 = (k, p1, p2, p2*self.lotConfig.prize.get(pz))
                            #print("xxddd bb cc", file=sys.stderr)
                            #print(t12, file=sys.stderr)
                            result.append((k, p1, p2, p2* int(self.lotConfig.prize.get(pz))))
                            #print(f"({p0}, {p1}, {p2})", end="")
                            #print(f"{p1}#{k}", end="")
                        else:
                            print(".", end="")
                            #print("Wrong")
                print("x")
            return result




    def menus(self):
        pass

    def generateDummyOrder(self):
        self.removeAllOrder()
        for buyer in self.buyerMan.list():
            numbers = []
            r0 = randint(1,3)
            r1 = randint(1,4)
            r2 = r0
            #print(r0)
            if r0 == 1:
                numbers.append( [ "3hi", fake.bothify(text='###'), fake.random_number(digits=r2)  ])
                numbers.append( [ "3lo", fake.bothify(text='###'), fake.random_number( digits=r2) ])
                numbers.append( [ "2hi", fake.bothify(text='##'), fake.random_number(digits=r2)  ])
            if r0 == 2:
                numbers.append( [ "2lo", fake.bothify(text='##'), fake.random_number(digits=r2)  ])
                numbers.append( [ "runhi", fake.bothify(text='#'), fake.random_number(digits=r2)  ])
                numbers.append( [ "runlo", fake.bothify(text='#'), fake.random_number(digits=r2)  ])
                numbers.append( [ "swap2lo", fake.bothify(text='##'), fake.random_number(digits=r2)  ])
            if r0 == 3:
                numbers.append( [ "swap3hi", fake.bothify(text='###'), fake.random_number(digits=r2)  ])
                numbers.append( [ "swap2hi", fake.bothify(text='##'), fake.random_number(digits=r2)  ])

            order = self.putOrder(buyer = buyer, numbers=numbers)
            if order:
                self.confirmOrder(order)


    def riskReport(self):
        print("============== Risk Report =========")
        total = 0
        bets = 0
        totalPrize = 0

        if self.orderMan is None:
            return ""

        for o in self.orderMan.listAll():
            for n in o.numbers:
                total += n[2]
                bets += 1

            #prizes = self.checkPrize(o)
            prizes = self.checkPrize2(o)
            if prizes:
                for p in prizes:
                    #print(prizes)
                    print(totalPrize, p, file=sys.stderr)
                    totalPrize += int(p[3])

        if bets == 0:
            return None
        avg = total / bets
        profit = total - totalPrize

        txt = f"""
        Total In {total:,} THB\n
        Incomming bets {self.orderMan.nbets:,}\n
        Reject bets {self.orderMan.rejects:,}"
        Total bets(n) {bets:,}\n
        Avg bet size  {avg:,.2f} THB\n
        Total Prize  {totalPrize:,.2f} THB\n
        Profit  {profit:,.2f} THB\n
        """
        result = {
                "Total In":f"{total:,} THB",
                "Incomming bets ":f"{self.orderMan.nbets:,}",
                "Reject bets":f"{self.orderMan.rejects:,}",
                "Total bets(n)":f"{bets:,}",
                "Avg bet size":f"{avg:,.2f} THB",
                "Total Prize":f"{totalPrize:,.2f} THB",
                "Profit":f"{profit:,.2f}THB"
                }

        print(txt)
        return result

    def setNoLimit(self, no, limit):
        if (no, limit) not in self.lotConfig.setLimit:
            self.lotConfig.setLimit.append((no, limit))
            self.lotConfig.commit()

    def generateDummyBuyer(self):
        self.removeAllBuyer()
        #Faker.seed(0)
        for _ in range(2000):
            self.createBuyer(fake.phone_number(), fake.bban(), fake.swift(length=8), fake.name())

        #self.createBuyer('')



    def removeAllBuyer(self):
        return self.buyerMan.delete()

    def removeAllOrder(self):
        return self.orderMan.delete()

    def findBuyer(self, tel):
        buyers = self.buyerMan.list(tel=tel)
        print(list(buyers))

    def closeNo(self, no):
        if no not in self.lotConfig.closeNumbers:
            self.lotConfig.closeNumbers.append(no)
            self.lotConfig.commit()
        else:
            print(f"Number {no} is in closeNumbers")

    def confirmOrder(self, order):
        #check slip payment
        order.isConfirm = True
        return order.commit()

    def resetAll(self):
        self.removeAllBuyer()
        self.removeAllOrder()
        self.resetNoLimit()

    def listOrders(self):
        return self.orderMan.listAll()

    def searchOrder(self, buyerName):
        print(buyerName, file=sys.stderr)
        return self.orderMan.listAll(buyer = {'$regex': f".*{buyerName}.*", '$options' : 'i'})




if __name__ == "__main__":
    lm = LotMan(datetime(2021, 1, 15))
    #assert lm.login('xxx', '1234')
    #print(vars(lm.currentUser))
    #print(lm.listAdminUser())

    lm.setNo("943647", ["239", "864"], ["006", "375"], "86")

    lm.printNo()

    lm.setSpecialNo(["12", "21", "22"], 40)
    lm.setPrize("3hi", 450)
    lm.setPrize("3lo", 100)
    lm.setPrize("2hilo", 65)
    lm.setPrize("swap", 100)
    lm.setPrize("runhi", 3)
    lm.setPrize("runlo", 3)

    lm.printPrize()

    lm.calNumbers()
    print("Cal no.")
    print("================")
    #print(lm.numbers)
    #buyer = Buyer("0830010222", "232313", "bkk", "tum")
    #buyer.commit()
    lm.removeAllBuyer()
    lm.removeAllOrder()

    '''
    lm.createBuyer("0830010222", "232313", "bkk", "tum")

    buyer = lm.findBuyer("0830010299")
    if not buyer:
        print("Create buyer")
        buyer = lm.createBuyer("0830010299", "11111", "bkk", "tum2")
        print(buyer)

    orderId = lm.putOrder(buyer = buyer, numbers=[
        ("3hi", "647", 100),
        ("3hi", "007", 200),
        ("swap3hi", "674", 100)
    ])
    '''

    lm.resetNoLimit()

    lm.setNoLimit("*", 7000)
    lm.setNoLimit("89", 3000)
    lm.setNoLimit("649", 3000)
    lm.setNoLimit("647", 1000)
    lm.setNoLimit("123", 0)
    #lm.closeNo("611")

    lm.generateDummyBuyer()
    lm.generateDummyOrder()

    lm.riskReport()


    '''
    order = lm.putOrder(buyer = buyer, numbers=[("3hi", "647", 100),
                                                ("3lo", "211", 100),
                                                ("3lo", "006", 50),
                                                ("swap2lo", "12", 100),
                                                ("swap2lo", "68", 30)
                                                ])
    '''
    #print(order)

    #lm.confirmOrder(order)

    #prizes = lm.checkPrize(order)
    #print(prizes)




    '''
    order = Order(buyer=buyer.id,  numbers=[
        ("3hi", "647", 100),
        ("3hi", "007", 200),
        ("swap3hi", "674", 100)
    ])
    order.commit()
    '''

    #order.comfirm()
    #order.commit()

    #lm.putOrder(order)


