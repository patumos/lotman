import re
from googletrans import Translator
import spacy
import sys

translator = Translator()

txt = "The rain in Spain"

pdict = {
    #"nl_com": r"(\w+)*=(\d+)\*(\d+)",
    "3up_spec": r"(\d{3})=(\d+)\(*(บน|โต๊ด)?\)*",
    "3up": r"(\d{3})=(\d+)",
    "3up_swap": r"(\d{3})=(\d+)\*(\d+)",
    "2no_spec": r"(\d{2})=(\d+)\(*(บน|ล่าง)?\)*",
    "2no": r"(\d{2})=(\d+)\*(\d+)",
    "2no_spec_leaf": r"(\d{2})=\((\d+)\)\(*(บน|ล่าง)?\)*",
    "2no_leaf": r"(\d{2})=\((\d+)\)\*\((\d+)\)",
    "3up_multi": r"(\d{3},\d{3})=(\d+)",
    "3up_spec_multi": r"(\d{3},\d{3})=(\d+)\(*(บน|โต๊ด)?\)*",
    "3up_swap_multi": r"(\d{3},\d{3})=(\d+)\*(\d+)",
    "2no_spec_leaf_multi": r"(\d{2},\d{2})=\((\d+)\)\(*(บน|ล่าง)?\)*",
    "2no_leaf_multi": r"(\d{2},\d{2})=\((\d+)\)\*\((\d+)\)",
    "2no_spec_multi": r"(\d{2},\d{2})=(\d+)\(*(บน|ล่าง)?\)*",
    "2no_multi": r"(\d{2},\d{2})=(\d+)\*(\d+)",
    }

pattern0 = r"(\d{3})\s*=\s*(\d+)\s*\*?\s*(\d+)?"
pattern1 = r"(\d{1,3})\s*=\s*(\d+)\s*\*?\s*(\d+)?\s*\(*(บน|ล่าง|โต๊ด)?\)*"
pattern2 = r"(\d{1,3})\s*=\s*\(\s*(\d+)\s*\)\s*\*?\s*\(\s*(\d+)?\s*\)\s*\(*(บน|ล่าง|โต๊ด)?\)*"

class BuyCommandManger:
    @classmethod
    def _genBuyCommand(self, text, userName):
        commandList = []
        for c in text.splitlines():
            x = re.search(pattern, c)
            #x = re.fullmatch(pattern, c)
            if x:
                #print("pattern 1")
                gs = x.groups()
                #print(f"gs = {gs}")
                if gs[2]:
                    bc = BuyCommand(no=gs[0], up=int(gs[1] or "0"), under=int(gs[2] or "0"), spec=gs[3], leaf=False, userName=userName)
                else:
                    if gs[3] == "บน":
                        bc = BuyCommand(no=gs[0], up=int(gs[1] or "0"), under=0, spec=gs[3], leaf=False, userName=userName)
                    elif gs[3] == "ล่าง":
                        bc = BuyCommand(no=gs[0], up = 0, under=int(gs[1] or "0"), spec=gs[3], leaf=False, userName=userName)

                commandList.append(bc)



            x = re.search(pattern2, c)
            if x:
                #print("pattern 2")
                gs = x.groups()
                bc = BuyCommand(no=gs[0], up=int(gs[1] or "0") , under=int(gs[2] or "0"), spec=gs[3], leaf=True)
                commandList.append(bc)
        return commandList

    @classmethod
    def genBuyCommand(self, text, userName, messageId=None):
        text = text.replace(" ", "").strip("\n")
        text = text.replace("\n", ",")
        print(f"text = {text}")
        commandList = []
        for c in text.splitlines():
            #x = re.search(pattern, c)
            for k,p in pdict.items():
                x = re.fullmatch(p, c)
                if x:
                    print(f"k = {k}")
                    gs = x.groups()
                    print(f"gs = {gs}")

                    bc = None
                    bc2 = None

                    if k == "3up_spec":
                        if gs[2] == "บน":
                            bc = BuyCommand(no=gs[0], up=int(gs[1] or "0"), spec=gs[2], leaf=False, userName=userName)
                        if gs[2] == "โต๊ด":
                            bc = BuyCommand(no=gs[0], swap=int(gs[1] or "0"),  spec=gs[2], leaf=False, userName=userName)

                    elif k == "3up_spec_multi":
                        n1, n2 = gs[0].split(',')
                        if gs[2] == "บน":
                            bc = BuyCommand(no=n1, up=int(gs[1] or "0"), spec=gs[2], leaf=False, userName=userName)
                            bc2 = BuyCommand(no=n2, up=int(gs[1] or "0"), spec=gs[2], leaf=False, userName=userName)

                        if gs[2] == "โต๊ด":
                            bc = BuyCommand(no=n1, swap=int(gs[1] or "0"),  spec=gs[2], leaf=False, userName=userName)
                            bc2 = BuyCommand(no=n2, swap=int(gs[1] or "0"),  spec=gs[2], leaf=False, userName=userName)

                    elif k == "3up":
                        bc = BuyCommand(no=gs[0], up=int(gs[1] or "0"),  leaf=False, userName=userName)
                    elif k == "3up_multi":
                        n1, n2 = gs[0].split(',')
                        bc = BuyCommand(no=n1, up=int(gs[1] or "0"),  leaf=False, userName=userName)
                        bc2 = BuyCommand(no=n2, up=int(gs[1] or "0"),  leaf=False, userName=userName)
                    elif k == "3up_swap":
                        bc = BuyCommand(no=gs[0], up=int(gs[1] or "0"),  swap=int(gs[1] or "0"),  leaf=False, userName=userName)
                    elif k == "3up_swap_multi":
                        n1, n2 = gs[0].split(',')
                        bc = BuyCommand(no=n1, up=int(gs[1] or "0"),  swap=int(gs[1] or "0"),  leaf=False, userName=userName)
                        bc2 = BuyCommand(no=n2, up=int(gs[1] or "0"),  swap=int(gs[1] or "0"),  leaf=False, userName=userName)
                    elif k == "2no_spec":
                        if gs[2] == "บน":
                            bc = BuyCommand(no=gs[0], up=int(gs[1] or "0"), spec=gs[2], leaf=False, userName=userName)
                        if gs[2] == "ล่าง":
                            bc = BuyCommand(no=gs[0], under=int(gs[1] or "0"),  spec=gs[2], leaf=False, userName=userName)
                    elif k == "2no_spec_multi":
                        n1, n2 = gs[0].split(',')
                        if gs[2] == "บน":
                            bc = BuyCommand(no=n1, up=int(gs[1] or "0"), spec=gs[2], leaf=False, userName=userName)
                            bc2 = BuyCommand(no=n2, up=int(gs[1] or "0"), spec=gs[2], leaf=False, userName=userName)
                        if gs[2] == "ล่าง":
                            bc = BuyCommand(no=n1, under=int(gs[1] or "0"),  spec=gs[2], leaf=False, userName=userName)
                            bc2 = BuyCommand(no=n2, under=int(gs[1] or "0"),  spec=gs[2], leaf=False, userName=userName)

                    elif k == "2no":
                        bc = BuyCommand(no=gs[0], up=int(gs[1] or "0"),  under=int(gs[1] or "0"),  leaf=False, userName=userName)

                    elif k == "2no_multi":
                        n1, n2 = gs[0].split(',')
                        bc = BuyCommand(no=n1, up=int(gs[1] or "0"),  under=int(gs[1] or "0"),  leaf=False, userName=userName)
                        bc2 = BuyCommand(no=n2, up=int(gs[1] or "0"),  under=int(gs[1] or "0"),  leaf=False, userName=userName)

                    elif k == "2no_spec_leaf":
                        if gs[2] == "บน":
                            bc = BuyCommand(no=gs[0], up=int(gs[1] or "0"), spec=gs[2], leaf=True, userName=userName)
                        if gs[2] == "ล่าง":
                            bc = BuyCommand(no=gs[0], under=int(gs[1] or "0"),  spec=gs[2], leaf=True, userName=userName)

                    elif k == "2no_leaf":
                        bc = BuyCommand(no=gs[0], up=int(gs[1] or "0"),  under=int(gs[1] or "0"),  leaf=True, userName=userName)

                    elif k == "2no_spec_leaf_multi":
                        n1, n2 = gs[0].split(',')
                        if gs[2] == "บน":
                            bc = BuyCommand(no=n1, up=int(gs[1] or "0"), spec=gs[2], leaf=True, userName=userName)
                            bc2 = BuyCommand(no=n2, up=int(gs[1] or "0"), spec=gs[2], leaf=True, userName=userName)
                        if gs[2] == "ล่าง":
                            bc = BuyCommand(no=n1, under=int(gs[1] or "0"),  spec=gs[2], leaf=True, userName=userName)
                            bc1 = BuyCommand(no=n2, under=int(gs[1] or "0"),  spec=gs[2], leaf=True, userName=userName)

                    elif k == "2no_leaf_multi":
                        n1, n2 = gs[0].split(',')
                        bc = BuyCommand(no=n1, up=int(gs[1] or "0"),  under=int(gs[1] or "0"),  leaf=True, userName=userName)
                        bc2 = BuyCommand(no=n2, up=int(gs[1] or "0"),  under=int(gs[1] or "0"),  leaf=True, userName=userName)



                    if bc or bc2:
                        if bc:
                            commandList.append(bc)
                        if bc2:
                            commandList.append(bc2)

                        break
            else:
                #print("else match", file=sys.stderr)
                c = c.replace(",@", "@")
                #print(c, file=sys.stderr)
                pl = r'(?<!\*)(\d+)(?=,|=)'
                #pr = r'(?<==)(\d+)\*?(\d+|บน|ล่าง|โต๊ด)?'
                pr = r'=(\d+)\*?(\d+|บน|ล่าง|โต๊ด)?'
                pr2 = r'=(\(\d+\))\*?(\(\d+\)|บน|ล่าง|โต๊ด)?'
                namePattern = r'@(\S+)'

                nums = re.findall(pl, c)

                temp = re.findall(pr,c)
                temp2 = re.findall(pr2,c)
                #print("xxxxxxxxxxxxxxxxxxxxxxxx==========", file=sys.stderr)
                print(temp, temp2,  file=sys.stderr)
                isLeaf = False
                if temp:
                    print("temp1", file=sys.stderr)
                    orders = temp[0]
                if temp2:
                    isLeaf = True
                    print("temp2", file=sys.stderr)
                    orders = temp2[0]

                names = re.findall(namePattern,c)
                #print("xxxxxxxxxxxxxxxxxxxxxxxx", file=sys.stderr)
                #print(nums, orders, names, file=sys.stderr)
                #print("xxxxxxxxxxxxxxxxxxxxxxxx", file=sys.stderr)
                for n in nums:
                    #print(n)
                    #print(orders)
                    bc = BuyCommand(no=n)
                    if isLeaf == True:
                        bc.leaf = True
                        orders = list(orders)
                        for i,v in enumerate(orders):
                            orders[i] = orders[i].replace("(", "").replace(")", "")
                        print(orders, file=sys.stderr)

                    no1 = no2 = comSpec = None

                    if orders[0].isnumeric():
                        no1 = int(orders[0])

                    #print(len(orders), file=sys.stderr)
                    #print(orders, file=sys.stderr)
                    if len(orders) ==  2:
                        if orders[1].isnumeric():
                            no2 = int(orders[1])
                        else:
                            comSpec = orders[1]
                        #print(len(n), file=sys.stderr)
                        if len(n) == 2:
                            if no2 is not None:
                                bc.up = no1
                                bc.under = no2
                            if comSpec is not None:
                                if comSpec == "บน":
                                    bc.up = no1
                                if comSpec == "ล่าง":
                                    bc.under = no1
                                bc.setSpec(comSpec)


                        if len(n) == 3:

                            if no2 is not None:
                                #print("no2 is not None", file=sys.stderr)
                                bc.up = no1
                                bc.swap = no2
                            else:
                                #print("comspec", file=sys.stderr)
                                #print(comSpec, file=sys.stderr)
                                #print(comSpec, file=sys.stderr)
                                if comSpec == "บน":
                                    bc.up = no1
                                if comSpec == "โต๊ด":
                                    bc.swap = no1
                                bc.setSpec(comSpec)

                        #print("Names = ", file=sys.stderr)
                        #print(names, file=sys.stderr)
                        if len(names) == 1:
                            bc.userName = names[0]
                        else:
                            bc.userName = userName

                        print("Leaf ", bc.leaf, file=sys.stderr)
                        commandList.append(bc)



        print([ vars(x) for x in commandList], file=sys.stderr)
        print("==============================")
        return commandList

class BuyCommand:
    def __init__(self, no="", up=0, under=0, spec="", swap=0,  leaf=None, userName=""):
        self.no = no
        self.up = up
        self.under = under
        self.swap = swap
        self.normalizeSpec(spec)
        #self.spec = self.normalizeSpec(spec)
        self.leaf = leaf
        self.userName = userName

    def setSpec(self,spec):
        self.normalizeSpec(spec)

    def normalizeSpec(self, spec):
        if spec is None:
            self.spec = "n/a"
            return

        if "บน" in spec:
            self.spec = "hi"
        elif "ล่าง" in spec:
            self.spec = "lo"
        elif "โต๊ด" in spec:
            self.spec = "swap"
        elif "วิ่ง" in spec:
            self.spec = "run"
        else:
            self.spec = "n/a"



    def __str__(self):
        return f"no = {self.no} , up = {self.up}, under = {self.under}, spec = {self.spec}, leaf = {self.leaf}"

if __name__ == "__main__":
    command = [
        "123 = 100 บน",
        "123,231 = 100 บน",
        "133 = 100 โต๊ด",
        "22 = 100*30",
        "11 = 100 บน",
        "23 = 100 * 200\n199 = 200 * 150",
        "22 = (100)*(30)",
        "11 = (100) บน",
        """
        12
        32
        11
        99
        20
        12= 100 * 200
        """,
        """
        12
        32
        11
        99
        20
        12= (100) * (200)
        """,
        """
        12
        32
        11
        99
        20
        12= 100 ล่าง
        ** TumHello **
        """
    ]
    print("xxxxxxxxxxxxxxxxxxxxxxxxxx")
    for c in command:
        print(c)
        BuyCommandManger.genBuyCommand(c, "tum")
