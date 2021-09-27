import hashlib
import json
from datetime import datetime

class Transaction(object):
    def __init__(self,sender,reciever,amt):
        self.sender = sender
        self.reciever = reciever
        self.amt = amt
        self.time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.hash = self.calculateHash()

    def calculateHash(self):
        hashString = self.sender+self.reciever+str(self.amt)+str(self.time)
        hashEncoded = json.dumps(hashString, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def isValidTransaction(self):
        if self.hash != self.calculateHash():
            return False
        if self.sender == self.reciever:
            return False
        if self.sender == "rewards":
            return True
        # if not self.signature or len(self.signature) == 0:
        #     return False
        return True

    def signTransaction(self,key,senderKey):
        if self.hash != self.calculateHash():
            return False
