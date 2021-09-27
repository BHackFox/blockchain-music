import random
import string
import hashlib
import json
from datetime import datetime

class Wallet(object):
    def __init__(self,index,time):
        self.index = index
        self.time = time
        self.keyphrase = self.generateKeyphrase()
        self.prev = ""
        self.address = self.generateAddress()
        self.wallet = self.generateWallet()

    def generateAddress(self):
        hashString = str(self.index) + self.time + self.prev
        hashEncoded = json.dumps(hashString,sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def generateKeyphrase(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(256))

    def generateWallet(self):
        hashString = self.address + self.keyphrase
        hashEncoded = json.dumps(hashString,sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def isValidWallet(self):
        if self.address != self.generateAddress():
            return False
