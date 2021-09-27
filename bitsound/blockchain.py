import hashlib
import json
from datetime import datetime
from urllib.parse import urlparse
import requests
import random
import string
from urllib.parse import urlparse
from bitsound.database import Database


class Blockchain (object):
    def __init__(self,node=False):
        self.nodes = set()
        if node:
            self.register_node(node)
            self.resolveConflicts()
        self.chain = []
        self.wallets = []
        self.users = []
        self.songs = []
        self.wallet = self.newWallet()
        self.blockSize = 10
        self.rewards = 10
        self.hostrewards = 5
        self.validatorrewards = 1
        self.db = Database()

    def newWallet(self):
        self.resolveConflicts()
        if len(self.wallets) == 0:
            genwallet = self.addGenesisWallet()
            self.wallets.append(genwallet)
            return genwallet
        else:
            wallet = Wallet(len(self.wallets),datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),self.getLastWallet().hash)
            self.wallets.append(wallet)
            return wallet

    def addGenesisWallet(self):
        wallet = Wallet(0,datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),"None")
        return wallet


    def minePendingTransaction(self,walletArtist,walletValidator):
        if len(self.chain) == 0:
            genblock = self.addGenesisBlock()
            self.chain.append(genblock)
        newBlock = Block(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),len(self.chain),self.getLastBlock().hash)
        self.chain.append(newBlock)
        self.artistPendingTransaction(newBlock,walletArtist)
        self.hostPendingTransaction(newBlock)
        self.validatorPendingTransaction(newBlock,walletValidator)

    def artistPendingTransaction(self,block,walletArtist):
        payArtist = Transaction("rewards",walletArtist,self.rewards)
        block.transactions.append(payArtist)

    def hostPendingTransaction(self,block):
        payHost = Transaction("hostRewards",self.wallet.wallet,self.hostrewards)
        block.transactions.append(payHost)


    def validatorPendingTransaction(self,block,walletValidator):

        payValidator = Transaction("validatorRewards",walletValidator,self.validatorrewards)
        block.transactions.append(payValidator)


    def addGenesisBlock(self):
        tArr = []
        genesis = Block(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),0,"None")
        return genesis

    def register_node(self,address):
        parseUrl = urlparse(address)
        self.nodes.add(parseUrl.netloc)

    def resolveConflicts(self):
        neighbors = self.nodes
        newChain = None
        maxLength = len(self.nodes)
        new_nodes = []
        for node in neighbors:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    #print(response.json())
                    self.chainJsonDecode(response.json())
                    new_nodes = response.json()["nodes"]
            except:
                pass
        for node in new_nodes:
            self.nodes.add(node)


    def getLastBlock(self):
        self.resolveConflicts()
        i = 0
        blo = self.chain[0]
        for block in self.chain:
            if block.index > i:
                i = block.index
                bloc = block
        return bloc

    def getLastWallet(self):
        self.resolveConflicts()
        i = 0
        wall = self.wallets[0]
        for wallet in self.wallets:
            if wallet.index > i:
                i = wallet.index
                wall = wallet
        return wall

    def getLastSong(self):
        self.resolveConflicts()
        i = 0
        s = self.songs[0]
        for song in self.songs:
            if song.index > i:
                i = song.index
                s = song
        return s

    def isValidChain(self):
        for i in range(1,len(self.chain)):
            b1 = self.chain[i-1]
            b2 = self.chain[i]

            if not b2.hasValidTransactions():
                return False
            if b2.hash != b2.calculateHash():
                return False
            if b2.prev != b1.hash:
                return False
        return True

    def chainJsonDecode(self,chainJson):
        for blockJ in chainJson["blocks"]:
            block = Block(blockJ['time'],blockJ['index'],blockJ['prev'])
            tArr = []
            for tJson in blockJ['transactions']:
                transaction = Transaction(tJson['sender'], tJson['reciever'], tJson['amt'])
                transaction.time = tJson['time']
                transaction.hash = tJson['hash']
                tArr.append(transaction)
            block.transactions = (tArr)
            self.chain.append(block)
        for walletJ in chainJson["wallets"]:
            wallet = Wallet(walletJ["index"],walletJ["time"],walletJ["prev"])
            wallet.keyphrase = ""
            wallet.prev = walletJ["prev"]
            wallet.wallet = walletJ["wallet"]
            self.wallets.append(wallet)
        for userJ in chainJson["users"]:
            user = User(userJ["hashBlock"],userJ["time"])
            user.hash = userJ["hash"]
            user.wallet = userJ["wallet"]
            self.users.append(user)

        # for nodeJ in chainJson["nodes"]:
        #     self.nodes.add(nodeJ)
        # print(self.nodes)

        self.resolveCopyConflict()


    def chainJsonEncode(self):
        chain_json = {}
        blockArrJson = []
        for i in range(len(self.chain)):
            block = self.chain[i]
            blockJ = {}
            blockJ['hash'] = block.hash
            blockJ['index'] = block.index
            blockJ['prev'] = block.prev
            blockJ['time'] = block.time
            blockJ['musical'] = block.musical


            transactionJ = []
            for j in range(len(block.transactions)):
                tJson = {}
                transaction = block.transactions[j]
                tJson['time'] = transaction.time
                tJson['sender'] = transaction.sender
                tJson['reciever'] = transaction.reciever
                tJson['amt'] = transaction.amt
                tJson['hash'] = transaction.hash
                transactionJ.append(tJson)
            blockJ['transactions'] = transactionJ
            blockArrJson.append(blockJ)

        walletArrJson = []
        for wallet in self.wallets:
            wjson = {}
            wjson["wallet"] = wallet.wallet
            wjson["prev"] = wallet.prev
            wjson["hash"] = wallet.hash
            wjson["time"] = wallet.time
            wjson["index"] = wallet.index
            wjson["address"] = wallet.address
            walletArrJson.append(wjson)

        usersArrJson = []
        for user in self.users:
            ujson = {}
            ujson["hash"] = user.hash
            ujson["time"] = user.time
            ujson["hashBlock"] = user.hashBlock
            ujson["wallet"] = user.wallet
            usersArrJson.append(ujson)

        nodesArrJson = []
        for node in self.nodes:
            nodesArrJson.append(node)

        chain_json["blocks"] = blockArrJson
        chain_json["wallets"] = walletArrJson
        chain_json["users"] = usersArrJson
        chain_json["nodes"] = nodesArrJson
        self.db.insert(chain_json)
        result =  self.db.find()
        return result

    def getBalance(self,wallet):
        balance = 0
        for i in range(0,len(self.chain)):
            block = self.chain[i]
            #print(block.prev)
            try:
                for j in range(len(block.transactions)):
                    transaction = block.transactions[j]
                    if transaction.sender == wallet:
                        balance -=transaction.amt
                    if transaction.reciever == wallet:
                        balance += transaction.amt
            except AttributeError:
                print("No transaction")
        return balance

    def makeTransaction(self,sender,reciever,amt):
        if self.getBalance(sender) - amt >= 0:
            transaction = Transaction(sender,reciever,amt)
            lastBlock = self.getLastBlock()
            lastBlock.transactions.append(transaction)
            return True
        return False

    #def doHostJob(self,request):

    #def doValidatorJob(self,nodeaddress,request,response):

    def newUser(self,hasWallet=False):
        if hasWallet:
            wallet = self.newWallet()
            print(wallet.keyphrase)
            user = User(self.getLastBlock().hash,datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),wallet)
            self.users.append(user)
        else:
            user = User(self.getLastBlock().hash,datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
            self.users.append(user)
        return user

    def resolveCopyConflict(self):
        sum = []
        for i in range(len(self.chain)):
            block = self.chain[i]
            for k in range(i+1,len(self.chain)):
                blocks = self.chain[k]
                if block.hash == blocks.hash:
                    if len(block.transactions) == len(blocks.transactions):
                        sum.append(block)
                    if len(block.transactions) < len(blocks.transactions):
                        block.transactions = blocks.transactions
                        sum.append(blocks)
                    if len(block.transactions) > len(blocks.transactions):
                        blocks.transactions = block.transactions
                        sum.append(block)
                    # if blocks.transactions == block.transactions:
                    #     # for k in range(len(block.transactions)):
                    #     #     if block.transactions[k].hash == blocks.transactions[k].hash:
                    #     if len(block.transactions) < len(blocks.transactions):
                    #         block.transactions = blocks.transactions
        for i in sum:
            self.chain.remove(i)
        sum = []
        for i in range(len(self.wallets)):
            wallet = self.wallets[i]
            for k in range(i+1,len(self.wallets)):
                wallets = self.wallets[k]
                if wallet.wallet == wallets.wallet and wallet.address == wallets.address:
                    sum.append(wallet)
        for i in sum:
            self.wallets.remove(i)
        sum = []
        for i in range(len(self.users)):
            user = self.users[i]
            for k in range(i+1,len(self.users)):
                users = self.users[k]
                if user.hash == users.hash:
                    sum.append(user)
        for i in sum:
            self.users.remove(i)
        sum = []

    def enterBlockChain(self,address,myAddress):
        try:
            data = {"address":myAddress}
            send = requests.post(address+"/add/node",data=data)
            if send.status_code == 200:
                self.register_node(address)
                self.resolveConflicts()
        except Exception as e:
            raise

    def authUserWallet(self,userWallet,keyphrase):
        for wallet in self.wallets:
            print(wallet.wallet)
            if wallet.wallet == userWallet:
                print(wallet.wallet)
                wallet.keyphrase = keyphrase
                print(wallet.keyphrase)
                if wallet.generateWallet() == userWallet:
                    return True
                else:
                    return False
        return False


    def returnTransaction(self,wallet):
        transactionArr = []
        for block in self.chain:
            for transaction in block.transactions:
                transactionJson = {}
                if transaction.sender == wallet:
                    transactionJson["sender"] = wallet
                    transactionJson["reciever"] = transaction.reciever
                    transactionJson["amt"] = transaction.amt
                    transactionJson["block"] = block.hash
                    transactionArr.append(transactionJson)
                elif transaction.reciever == wallet:
                    transactionJson["reciever"] = wallet
                    transactionJson["sender"] = transaction.sender
                    transactionJson["amt"] = transaction.amt
                    transactionJson["block"] = block.hash
                    transactionArr.append(transactionJson)
        return transactionArr


    def addSong(self,title,user):
        prev = self.getLastSong()
        if user.wallet != "None":
            music = Music(title,prev.index,datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),prev.hash,user.hash)
            self.songs.append(music)


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


class Wallet(object):
    def __init__(self,index,time,prev):
        self.index = index
        self.time = time
        self.prev = prev
        self.keyphrase = self.generateKeyphrase()
        self.address = self.generateAddress()
        self.wallet = self.generateWallet()
        self.hash = self.calculateHash()

    def generateAddress(self):
        hashString = str(self.index) + self.time + self.prev
        hashEncoded = json.dumps(hashString,sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def generateKeyphrase(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(256))

    def generateWallet(self):
        hashString = self.address + self.keyphrase
        hashEncoded = json.dumps(hashString,sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def calculateHash(self):
        hashString = self.prev
        hashEncoded = json.dumps(hashString,sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def isValidWallet(self):
        if self.address != self.generateAddress():
            return False
        if self.wallet != self.generateWallet():
            return False
        return True


class Block(object):
    def __init__(self,time,index,prev):
        self.index = index
        self.transactions = []
        self.time = time
        self.prev = prev
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
        return True


class User(object):
    def __init__(self,hashBlock,time,wallet="None"):
        self.hashBlock = hashBlock
        self.time = time
        self.hash = self.generateHash()
        if wallet!= "None":
            self.wallet = wallet.wallet
            self.wallet_compl = wallet
        else:
            self.wallet = wallet

    def generateHash(self):
        hashString = self.hashBlock + self.time + ''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(256))
        hashEncoded = json.dumps(hashString,sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()


class Music(object):
    def __init__(self, title,index,time,prev,user):
        self.title = title
        self.index = index
        self.time = time,
        self.prev = prev
        self.user = user
        self.hash = self.generateHash()
        self.tags = []
        self.users = []
        self.isVerified = None

    def generateHash(self):
        hashString = self.title + str(self.index) + self.time + self.prev + self.user
        hashEncoded = json.dumps(hashString,sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()


    def addTags(self,tags):
        for i in tags:
            self.tags.append(tags)

    def addUserToList(self,time,user,block):
        struct = {"user":user,"time":time,"block":block}
        self.users.append(struct)
