from bitsound import blockchain
from flask import Flask, jsonify, request, render_template, url_for, flash, redirect, Response
import json
block = blockchain

block.register_node("http://192.168.1.243:8080")
block.resolveConflicts()
#
# newwallet = block.newWallet()
# block.resolveConflicts()
# newwallet1 = block.newWallet()
# block.resolveConflicts()
# newwallet2 = block.newWallet()
# block.resolveConflicts()
# nodewallet = block.wallet.wallet
# block.resolveConflicts()
# block.minePendingTransaction(nodewallet,newwallet1.wallet)
# block.resolveConflicts()
# block.minePendingTransaction(newwallet.wallet,newwallet1.wallet)
# block.resolveConflicts()
# block.minePendingTransaction(newwallet1.wallet,newwallet1.wallet)
# block.resolveConflicts()
# block.minePendingTransaction(newwallet2.wallet,newwallet1.wallet)
# block.resolveConflicts()
# block.makeTransaction(nodewallet,newwallet.wallet,20)
# block.resolveConflicts()
# block.makeTransaction(newwallet1.wallet,newwallet.wallet,10)
# block.resolveConflicts()
# block.makeTransaction(newwallet.wallet,newwallet2.wallet,20)
# block.resolveConflicts()
# block.makeTransaction(newwallet2.wallet,newwallet.wallet,30)
# block.resolveConflicts()
# print(block.getBalance(nodewallet),block.getBalance(newwallet.wallet),block.getBalance(newwallet1.wallet),block.getBalance(newwallet2.wallet))
# #print(nodewallet,newwallet.wallet,newwallet1.wallet,newwallet2.wallet)
# user1 = block.newUser()
# block.resolveConflicts()







app = Flask(__name__)
@app.route('/chain')
def sendEncoded():
    result = block.chainJsonEncode()
    with open("file.json","w") as jsonreader:
        json.dump(result,jsonreader, indent=4)
    return result, 200

@app.route('/transaction', methods=["GET"])
def newTransaction():
    block.resolveConflicts()
    #block.makeTransaction(newwallet.wallet,newwallet2.wallet,10)
    result = block.chainJsonEncode()
    #print(result)
    with open("file.json","w") as jsonreader:
        json.dump(result,jsonreader, indent=4)
    #block.resolveConflicts()
    print(block.nodes)
    return render_template('wallets.html',blockchain=block),200

@app.route('/wallet', methods=["GET"])
def createnew():
    block.resolveConflicts()
    newWallet = block.newWallet()
    return render_template('new.html',wallet=newWallet),200

@app.route('/add/node',methods=["POST"])
def addnode():
    block.resolveConflicts()
    address = request.form.get('address')
    print(address)
    block.register_node(address)
    return "si",200

@app.route('/mine',methods=["GET"])
def mine():
    block.resolveConflicts()
    block.minePendingTransaction(block.wallets[-1].wallet,block.wallets[-2].wallet)
    return render_template('wallets.html',blockchain=block),200

@app.route('/add/user',methods=["GET"])
def adduser():
    block.resolveConflicts()
    user = block.newUser(True)
    data = {"user":user,"hash":"","keyphrase":""}
    for wallet in block.wallets:
        if wallet.wallet == user.wallet:
            data["hash"] = wallet.hash
            data["keyphrase"] = user.wallet_compl.keyphrase
    return render_template('new_user.html',newuser=data),200

@app.route('/access/wallet',methods=["GET","POST"])
def access():
    if request.method == "POST":
        wallet = request.form.get('wallet')
        keyphrase = request.form.get('keyphrase')
        if block.authUserWallet(wallet,keyphrase):
            print("SIIIIIII")
            return render_template('access_wallet.html',check=True),200
        else:
            print("NOOOOOO")
            return render_template('access_wallet.html',check=False)
    if request.method == "GET":
        return render_template('access_wallet.html',check=True),200


@app.route('/address/<wallet>',methods=["GET"])
def view_transactions(wallet):
    #wallet = request.args.get("wallet")
    block.resolveConflicts()
    transactions = block.returnTransaction(wallet)
    transaction = {"wallet":wallet,"transactions":transactions}
    return render_template('transactions.html',transaction=transaction),200


# # @app.route('/')
# # def streamwav():
# #     def generate():
# #         with open("wow.wav", "rb") as fwav:
# #             data = fwav.read(1024)
# #             while data:
# #                 yield data
# #                 data = fwav.read(1024)
# #     return Response(generate(), mimetype="audio/wav")
# #
# #
# #
app.run(host='192.168.1.197', port=8080)
