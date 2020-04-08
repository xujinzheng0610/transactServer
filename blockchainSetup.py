from web3 import Web3
import json
from eth_typing import (
    Address,
    BlockNumber,
    ChecksumAddress,
    HexStr,
)


web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
accounts = web3.eth.accounts

inspectorAddress = "0x34d5A773cbb46DfFd9766A95d22Be6d72FC47420"

with open("./blockchain/build/contracts/Project.json") as project:
    info_json = json.load(project)
abi = info_json["abi"]

projectContractAddress = '0x34d5A773cbb46DfFd9766A95d22Be6d72FC47420'
projectContract = web3.eth.contract(abi=abi, address=projectContractAddress)

with open("./blockchain/build/contracts/Registration.json") as regist:
    info_json = json.load(regist)
abi = info_json["abi"]

registrationContractAddress = '0x34d5A773cbb46DfFd9766A95d22Be6d72FC47420'
registrationContract = web3.eth.contract(abi=abi, address=registrationContractAddress)


with open("./blockchain/build/contracts/Donation.json") as donation:
    info_json = json.load(donation)
abi = info_json["abi"]

donationContractAddress = '0x674665f533b13eC9b0CAD7c5B372Aa1E93C56670'
donationContract = web3.eth.contract(abi=abi, address=donationContractAddress)

def make_donation(amount, pid, donor):
    txn = donationContract.functions.makeDonation(amount, pid)
    txn = txn.transact({'from': donor})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    print(receipt)
    return receipt.transactionHash.hex()


def registerInspector(address):
    print(address)
    # print(type(address))
    # print(accounts[0])
    # print(type(accounts[0]))
    txn = registrationContract.functions.registerInspector(address, "inspector").transact({'from': accounts[0]})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    # print("111")
    # print(txn)
    # print(type(txn))
    # print("222")
    # print(receipt)
    print(receipt.transactionHash)
    print(type(receipt.transactionHash))
    # print(receipt['from'])
    # print(receipt['to'])

    return receipt.transactionHash.hex()


def registerDonor(address, name):
    txn = registrationContract.functions.registerDonor(address,name).transact({'from':address})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    print(receipt)
    return receipt.transactionHash.hex()


def approveDonor(donor,inspector):
    txn = registrationContract.functions.approveDonor(donor).transact({'from':inspector})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    print(receipt)
    return receipt.transactionHash.hex()

def rejectDonor(donor, inspector): 
    txn = registrationContract.functions.rejectDonor(donor).transact({'from': inspector})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    print(receipt)
    return receipt.transactionHash.hex()
    
def updateDonor(donor, name):
    txn = registrationContract.functions.updateDonor(donor, name).transact({'from': donor})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    print(receipt)
    return receipt.transactionHash.hex() 


def getDonorDetails(donor):
    txn = registrationContract.functions.getOrganizationName(donor).call({'from': donor})
    return txn


def registerOrganization(charity, name):
    txn = registrationContract.functions.registerOrganization(charity, name).transact({'from': charity})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    print(receipt)
    return receipt.transactionHash.hex()


def approveOrganization(charity, inspector):
    txn = registrationContract.functions.approveOrganization(charity).transact({'from': inspector})
    receipt = web3.eth.waitForTransactionReceipt(txn) 
    return receipt.transactionHash.hex()


def rejectOrganization(charity, inspector):
    txn = registrationContract.functions.rejectOrganization(charity).transact({'from': inspector})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    return receipt.transactionHash.hex()


def updateOrganization(charity, name):
    txn = registrationContract.functions.updateOrganization(charity, name).transact({'from': charity})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    return receipt.transactionHash.hex()


def deleteOrganization(charity):
    txn = registrationContract.functions.deleteOrganization(charity).transact({'from': charity})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    return receipt.transactionHash.hex()


def approvedOrganization(charity):
    txn = registrationContract.functions.approvedOrganization(charity).call({'from': charity})
    return txn


def getOrganizationName(charity):
    txn = registrationContract.functions.getOrganizationName(charity).call({'from': charity})
    return txn


def confirmReceiveMoney(donation, charity):
    txn = donationContract.functions.confirmReceiveMoney(donation).transact({'from': charity})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    return receipt.transactionHash.hex()


def registerProject(charity, beneficiaryGainedRatio):
    numProjects = registrationContract.functions.numProjects().call()
    txn = registrationContract.functions.registerProject(beneficiaryGainedRatio).transact({'from': charity})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    return receipt.transactionHash.hex(), numProjects


def approveProject(inspector, projectId):
    int_id = int(projectId)
    txn = registrationContract.functions.approveProject(int_id).transact({'from': inspector})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    return receipt.transactionHash.hex()


def rejectProject(inspector, projectId):
    int_id = int(projectId)
    txn = registrationContract.functions.rejectProject(int_id).transact({'from': inspector})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    return receipt.transactionHash.hex()

def stopProject(inspector, projectId):
    int_id = int(projectId)
    txn = registrationContract.functions.stopProject(int_id).transact({'from': inspector})
    receipt = web3.eth.waitForTransactionReceipt(txn)
    return receipt.transactionHash.hex()

# def checkDonorApproval(txn_hash):
#     try:
#         receipt = web3.eth.getTransactionReceipt(txn_hash)
#         logs = registrationContract.events.DonorApproval().processReceipt(receipt)
#         return True
#     except Exception as ex:
#         print(ex)
#         return False

def checkDonorApproval(txn_hash,donor):
    try:
        receipt = web3.eth.getTransactionReceipt(txn_hash)
        logs = registrationContract.events.DonorApproval().processReceipt(receipt)
        print(logs)
        if(logs[0]['args']['donor']==donor):
            print(logs[0]['args']['donor'])
            return True
        return False
    except Exception as ex:
        print(ex)
        return False
        
def checkCharityApproval(txn_hash):
    try:
        receipt = web3.eth.getTransactionReceipt(txn_hash)
        logs = registrationContract.events.OrganizationApproval().processReceipt(receipt)
        return True
    except Exception as ex:
        print(ex)
        return False

def checkProjectApproval(txn_hash):
    try:
        receipt = web3.eth.getTransactionReceipt(txn_hash)
        logs = registrationContract.events.ApprovalProject().processReceipt(receipt)
        if(logs != null):
            return True
        else:
            return False 
    except Exception as ex:
        print(ex)
        return False

