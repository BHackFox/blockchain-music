import hashlib
import json
from datetime import datetime

class Block(object):
    def __init__(self,transactions,time,index):
        self.index = index
        self.transactions = transactions
        self.time = time
        self.prev = ''
        self.musical = self.calculateMusical()
        self.hash = self.calculateHash()

    def calculateMusical(self):
        return "52 hr"

    def calculateHash(self):
        hashTransactions = ""
        for transaction in self.transactions:
            hashTransactions += transaction.hash
        hashString = str(self.time)+hashTransactions+self.musical+self.prev
        hashEncoded = json.dumps(hashString,sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def hasValidTransactions(self):
        for i in range(len(self.transactions)):
            transaction = self.transactions[i]
            if not transaction.isValidTransaction():
                return False
        return True

    def jsonEncode(self):
        return jsonpickle.encode(self)

    #qua ci dovrebber essere mineBlock ma per adesso lo lascio cosi
    def mineBlock(self):
        choosen = 32
        while choosen != self.index:
            choosen = int(input(""))
        return True
