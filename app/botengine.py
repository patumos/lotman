import spacy
from pythainlp.translate import EnThTranslator, ThEnTranslator
from spacytextblob.spacytextblob import SpacyTextBlob
from googletrans import Translator
from spacy.matcher import Matcher

from lotman.bc import BuyCommand, BuyCommandManger
from lotman.lotman import LotMan
from lotman.models  import LineEvent
from lotman.db import MongoConnector

import sys

from datetime import datetime

translator = Translator()

nlp = spacy.load("en_core_web_md")

matcher = Matcher(nlp.vocab)
lotMatcher = Matcher(nlp.vocab)

pattern = [{"POS": "ADP"}, {"ENT_TYPE": "GPE"}]
matcher.add("prepositionLocation", [pattern])

pattern = [{"TEXT": {"REGEX": "[0-9]+"}}, {"TEXT": "="}, {"TEXT": {"REGEX": "[0-9]+"}}, {"LOWER": {"IN": ["บน", "ล่าง"]}, "OP": "?"}]
matcher.add("lotCommand", [pattern])

nlp.add_pipe("spacytextblob")

class BotEngine:
    msg = {
        "processLotCommand": "รับแล้วครับ {name}"
    }
    COMMAND_ERROR = "บันทึกแล้วครับ"
    def __init__(self, userName):
        self.userName = userName
        self.lotman = None

    def setLotman(self, lotman: LotMan):
        self.lotman = lotman

    def getReply(self, cmdName, **kwargs):
       return  BotEngine.msg[cmdName].format(**kwargs)

    def compareSen(self, sen1, sen2):
        e1 = translator.translate(w1)
        e2 = translator.translate(w2)

        doc1 = nlp(e1.text)
        doc2 = nlp(e2.text)

        sim = doc1.similarity(doc2)
        print(f"similarity of {w1}({e1.text}) vs {w2}({e2.text}) = {sim}")
        print(f"polarity _ => {doc1._.polarity} vs {doc2._.polarity}")
        print(f"subjectivity _ => {doc1._.subjectivity} vs {doc2._.subjectivity}")

    def processLotCommand(self, command, profileName, messageId=None):
        #print(command)
        bcs = BuyCommandManger.genBuyCommand(command, profileName)

        if bcs:
            #print("commandList")
            for bc in bcs:
                #print("gen")
                rb = self.lotman.acceptBuyCommand(bc)
                print(rb, file=sys.stderr)
                rb.messageId = messageId
                rb.commit()
            return self.getReply(cmdName="processLotCommand", name=profileName)
        else:
            return BotEngine.COMMAND_ERROR

    def recordEvent(self, event, profile):
        e = LineEvent(event.as_json_dict(), profile.as_json_dict())
        e.commit()

    def listEvents(self):
        return LineEvent.find(sortOptions=[("created_at", -1)])

    def photoMessages(self):
        return MongoConnector.fs.find().sort("_id", -1)


    def processCommand(self, command, raw=True):
        print("==== process command ===")
        if raw == False:
            en = translator.translate(command)

            doc = nlp(en.text)
        else:
            doc = nlp(command)

        matches = matcher(doc)

        matchText = ""
        for mid, start, end in matches:
            stringId = nlp.vocab.strings[mid]
            print(f"MID = {stringId} #{mid}")
            print(doc[start:end])
            span = doc[start:end]
            if len(span) > len(matchText):
                matchText = span
        return matchText

    def genCommand(self, text):
        result = [x.strip() for x in text.split('= ')]
        targetNumber = result[0]
        amount = result[1]
        spec = ""
        if any(opt in result for opt in ["บน", "ล่าง"]):
            spec = result[2]


        print(f"{spec} buy {targetNumber} amount {amount}THB")

    @classmethod
    def translate(cls, text, dest="en"):
        return translator.translate(text, dest=dest)




if __name__ == "__main__":
    botEngine = BotEngine("Tum")
    lm = LotMan(datetime(2021, 1, 15))
    botEngine.setLotman(lm)

    lm.resetAll()

    lm.setSpecialNo(["12", "21", "22"], 40)
    lm.setPrize("3hi", 450)
    lm.setPrize("3lo", 100)
    lm.setPrize("2hilo", 65)
    lm.setPrize("swap", 100)
    lm.setPrize("runhi", 3)
    lm.setPrize("runlo", 3)


    lm.setNo("943647", ["239", "864"], ["006", "375"], "86")
    lm.printNo()
    lm.printPrize()

    lm.calNumbers()
    print("Cal no.")
    print("================")
    print(lm.numbers)

    while True:
        w1 = input("Enter sentence 1: ")
        #w2 = input("Enter sentence 2: ")

        if w1 == "exit":
            break

        #mt = botEngine.processCommand(w1, True)
        #botEngine.genCommand(mt.text)
        reply = botEngine.processLotCommand(w1)
        print(reply)
        #print(f"mt is => {mt}")
        #botEngine.compareSen(w1, w2)
        #e1 = ThEnTranslator().translate(w1)
        #e2 = ThEnTranslator().translate(w2)


    lm.riskReport()


