from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import blockchainSetup
import datetime
from blockchainSetup import  web3
from pymongo.errors import ConnectionFailure
from bson.json_util import dumps

app = Flask(__name__)
title = "TransACT Server"
CORS(app)

client = MongoClient('localhost', 27017)
db = client['transact']

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/test", methods=['GET'])
def testGet():
    dic = {"value": 1}
    return jsonify(dic)


@app.route("/makeDonation", methods=['POST'])
def donate():
    # try:
    amount = request.form.get("amount")
    print(amount)
    pid = request.form.get("project_id")
    print(pid)
    donor = request.form.get("donor_id")
    print(donor)
    result = db.donors.find_one({"_id": ObjectId(donor)})
    print(result['eth_address'])
    result1 = db.projects.find_one({"_id": ObjectId(pid)})


    txn = blockchainSetup.make_donation(int(amount), int(result1['project_solidity_id']), result['eth_address'])
    print(txn)
    new_donation = {
        "amount": amount,
        "project_id": pid,
        "donor_id": donor,
        "donation_time": str(datetime.now()),
        "donation_hash": txn,
        "confirmed_hash": ''
    }


    donation_id = db.donations.insert_one(new_donation)
    print(str(donation_id))
    
    # except Exception as ex:
    #     print(ex)
    #     print(type(ex))
    #     return jsonify(
    #         {"error": str(ex)}
    #     )

    print(donation_id)
    return jsonify(200)


@app.route("/registerInspector", methods=['POST'])
def registerInspector():
    # address = request.form.get("inspectorAddress")
    # print(address)
    address = request.args.get("inspectorAddress")
    # print(address)
    txn = blockchainSetup.registerInspector(address)
    dic = {"txn": txn}
    return jsonify(dic)


@app.route("/registerDonor", methods=['POST'])
def registerDonor():
    donor_id = ''
    try:
        address = request.form.get("eth_address")
        #TODO: check address exists or not before add new record
        txn = blockchainSetup.registerDonor(address, request.form.get("full_name"))
        new_donor = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "email": request.form.get("email"),
            "eth_address": request.form.get("eth_address"),
            "bank_account": request.form.get("bank_account"),
            "physical_address": request.form.get("physical_address"),
            "full_name": request.form.get("full_name"),
            "contact_number": request.form.get("contact_number"),
            "financial_info": request.form.get("financial_info"),
            "registration_hash": txn,
            "approval_hash": ''
        }
        donor_id = db.donors.insert_one(new_donor)

    except Exception as ex:
        print(ex)
        print(type(ex))
        return jsonify(
            {
                "code":400,
                "message": str(ex)
            }
            # {"error": str(ex.args[0]['message'])}
        )

    print(donor_id)
    # dic = {"donor_id": str(donor_id.inserted_id)}
    # return jsonify(dic)
    return jsonify({"code":200})

@app.route("/updateDonor", methods=['POST'])
def updateDonor():

    donors = db.donors

    donor = request.form.get("eth_address")

    try:
        txn = blockchainSetup.updateDonor(donor, request.form.get("full_name"))

        result = donors.find_one_and_update(
            {"eth_address": donor},
            {"$set":{
                "username": request.form.get("username"),
                "password": request.form.get("password"),
                "email": request.form.get("email"),
                "bank_account": request.form.get("bank_account"),
                "physical_address": request.form.get("physical_address"),
                "full_name": request.form.get("full_name"),
                "contact_number": request.form.get("contact_number"),
            }
            }
        )
        dic = {"code": 200}
        return jsonify(dic)
    except Exception as ex:
        return jsonify({"error":str(ex)})



@app.route("/approveDonor", methods=['POST'])
def approveDonor():
    donors = db.donors

    donor = request.form.get("donorAddress")
    inspector = request.form.get("inspectorAddress")

    try:
        txn = blockchainSetup.approveDonor(donor, inspector)

        result = donors.find_one_and_update(
            {"eth_address": donor},
            {"$set":{
                "approval_hash":txn
            }
            }
        )
        # dic = {"txn": txn}
        return jsonify({
                "code":200,
                "message": "Approve Donor"
            })
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })

@app.route("/rejectDonor", methods=['POST'])
def rejectDonor():
    donors = db.donors

    donor = request.form.get("donorAddress")
    inspector = request.form.get("inspectorAddress")

    try:
        txn = blockchainSetup.rejectDonor(donor, inspector)

        result = donors.find_one_and_update(
            {"eth_address": donor},
            {"$set":{
                "approval_hash":txn
            }
            }
        )
        return jsonify({
                "code":200,
                "message": "Reject Donor"
            })
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })

@app.route("/getDonorDetails", methods=['GET'])
def getDonorDetails():
    donor = request.args.get("donorAddress")
    print(donor)

    try: 
        # txn = blockchainSetup.getDonorDetails(donor)
        db_result = db.donors.find_one({"eth_address":donor})
        db_result['_id'] = str(db_result['_id'])
        dic = {"code": 200, "message":db_result}
        return jsonify(db_result)
        
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })

@app.route("/getAllDonors", methods=['GET'])
def getAllDonors():
    try: 
        db_result = db.donors.find()
        result_list = []
        for result in db_result:
            result['_id'] = str(result['_id'])
            print(result)
            result_list.append(result)

        return jsonify(
            {"code": 200,
            "items": result_list}
        )
        
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })

@app.route("/getAllPendingDonors", methods=['GET'])
def getAllPendingDonors():
    try:
        db_result = db.donors
        result_list = []
        all_result = db_result.find(
            {"approval_hash": ''}
        )
        for result in all_result:
            result['_id'] = str(result['_id'])
            result_list.append(result)

        return jsonify(
            {"code": 200,
            "items": result_list}
        )
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })
            
@app.route("/getDonorsByProject", methods=['GET'])
def getDonorsByProject():
    projectId = request.args.get("projectId")
    print(projectId)
    try: 
        db_result = db.donations.find({"project_id":projectId})
        dic = {"code":200}
        i = 0
        for result in db_result:
            donor = result['donor_address']
            donor_details = db.donors.find_one({"eth_address":donor})
            donor_details['_id'] = str(donor_details['_id'])
            print(donor_details)
            dic[str(i)]=donor_details
            i+=1
        dic["message"]=i
        return jsonify(dic)
        
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })

@app.route("/getProjectsByOrganization", methods=['GET'])
def getProjectsByOrganization():
    charity = request.args.get("charityAddress")
    print(charity)
    try: 
        db_result = db.projects.find({"charity_address":charity})
        result_list = []
        for result in db_result:
            result['_id'] = str(result['_id'])
            print(result)
            result_list.append(result)
        dic = {"code":200, "items":result_list}    
        return jsonify(dic)
        
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })     

@app.route("/getProjectsByDonor", methods=['GET'])
def getProjectsByDonor():
    donor = request.args.get("donorAddress")
    print(donor)
    try: 
        db1_result = db.donations.find({"donor_address":donor})
        # project_id = str(db1_result['project_id'])
        db_result = db.projects.find({"project_id":"0"})
        result_list = []
        for result in db_result:
            result['_id'] = str(result['_id'])
            print(result)
            result_list.append(result)  
        dic = {"code":200, "items":result_list}    
        return jsonify(dic)
        
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })                         


@app.route("/registerOrganization", methods=['POST'])
def registerOrganization():

    charity = request.form.get("eth_address")
    try:

        txn = blockchainSetup.registerOrganization(charity, request.form.get("full_name"))
        new_charity = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "email": request.form.get("email"),
            "eth_address": request.form.get("eth_address"),
            "bank_account": request.form.get("bank_account"),
            "physical_address": request.form.get("physical_address"),
            "name": request.form.get("full_name"),
            "contact_number": request.form.get("contact_number"),
            "financial_info": request.form.get("financial_info"),
            "description": request.form.get("description"),
            "registration_hash": txn,
            "approval_hash":''
        }
        charity_id = db.charities.insert_one(new_charity)
    except Exception as ex:
        print(ex)
        print(type(ex))
        return jsonify(
            {"code": 400,
            "error": str(ex)}
            # {"error": str(ex.args[0]['message'])}
        )

    # dic = {"charity_id": str(charity_id.inserted_id)}
    # return jsonify(dic)
    return jsonify({"code":200})


@app.route("/approveOrganization", methods=['POST'])
def approveOrganization():

    charities = db.charities

    charity = request.form.get("charityAddress")
    inspector = request.form.get("inspectorAddress")

    try:
        txn = blockchainSetup.approveOrganization(charity, inspector)

        result = charities.find_one_and_update(
            {"eth_address": charity},
            {"$set":{
                "approval_hash":txn
            }
            }
        )
        # dic = {"txn": txn}
        return jsonify({
                "code": 200,
                "message": "Approve organization"
                })
    except Exception as ex:
        return jsonify({
                "code": 400,
                "message": str(ex)
                })


@app.route("/rejectOrganization", methods=['POST'])
def rejectOrganization():

    charities = db.charities

    charity = request.form.get("charityAddress")
    inspector = request.form.get("inspectorAddress")

    try:
        txn = blockchainSetup.rejectOrganization(charity, inspector)

        result = charities.find_one_and_update(
            {"eth_address": charity},
            {"$set":{
                "approval_hash":txn
            }
            }
        )
        # dic = {"txn": txn}
        return jsonify({
                "code": 200,
                "message": "Reject organization"
                })
    except Exception as ex:
        return jsonify({
                "code": 400,
                "message": str(ex)
                })


@app.route("/updateOrganization", methods=['POST'])
def updateOrganization():

    charities = db.charities

    charity = request.form.get("eth_address")

    try:
        txn = blockchainSetup.updateOrganization(charity, request.form.get("full_name"))

        result = charities.find_one_and_update(
            {"eth_address": charity},
            {"$set":{
                "username": request.form.get("username"),
                "password": request.form.get("password"),
                "email": request.form.get("email"),
                "bank_account": request.form.get("bank_account"),
                "physical_address": request.form.get("physical_address"),
                "name": request.form.get("full_name"),
                "contact_number": request.form.get("contact_number"),
                "financial_info": request.form.get("financial_info"),
                "description": request.form.get("description"),
            }
            }
        )
        dic = {"code": 200}
        return jsonify(dic)
    except Exception as ex:
        return jsonify({"error":str(ex)})


@app.route("/deleteOrganization", methods=['DELETE'])
def deleteOrganization():

    charities = db.charities

    charity = request.args.get("charityAddress")
    
    try:
        txn = blockchainSetup.deleteOrganization(charity)

        result = charities.delete_one(
            {"eth_address": charity}
        )

        return jsonify(200)
    except Exception as ex:
        return jsonify({"error":str(ex)})

@app.route("/getAllPendingOrganizations", methods=['GET'])
def getAllPendingOrganizations():
    try:
        db_result = db.charities
        result_list = []
        all_result = db_result.find(
            {"approval_hash": ''}
        )
        for result in all_result:
            result['_id'] = str(result['_id'])
            result_list.append(result)

        return jsonify(
            {"code": 200,
            "items": result_list}
        )
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })


@app.route("/approvedOrganization", methods=['GET'])
def approvedOrganization():
    charity = request.args.get("charityAddress")
    print(charity)
    txn = blockchainSetup.approvedOrganization(charity)
    dic = {"txn": txn}
    return jsonify(dic)


@app.route("/getOrganizationName", methods=['GET'])
def getOrganizationName():
    charity = request.args.get("charityAddress")
    print(charity)
    txn = blockchainSetup.getOrganizationName(charity)
    dic = {"txn": txn}
    return jsonify(dic)

@app.route("/getCharityDetails", methods=['GET'])
def getCharityDetails():
    charity = request.args.get("charityAddress")
    print(charity)

    try: 
        # txn = blockchainSetup.getDonorDetails(donor)
        db_result = db.charities.find_one({"eth_address":charity})
        db_result['_id'] = str(db_result['_id'])
        dic = {"code": 200, "message":db_result}
        return jsonify(db_result)
        
    except Exception as ex:
        return jsonify({
                "code":400,
                "message": str(ex)
            })    


@app.route("/confirmReceiveMoney", methods=['POST'])
def confirmReceiveMoney():
    donations = db.donations
    donation = request.args.get("donationId")
    inspector = request.args.get("inspectorAddress")
    try:
        txn = blockchainSetup.confirmReceiveMoney(donation, inspector)
        result = donations.find_one_and_update(
            {"_id": ObjectId(request.form.get("id"))},
            {"$set":{
                "comfirmed_hash": txn
            }
            }
        )
        return jsonify(200)
    except Exception as ex:
        return jsonify({"error":str(ex)})



@app.route("/retrieveProjectDetails",methods=['GET'])
def retrieveProjectDetails():

    try:
        result = db.projects.find_one({"_id":ObjectId(request.args.get("id"))})
        result['_id'] = str(result['_id'])
        result['charity_id'] = str(result['charity_id'])
        charity = db.charities.find_one({"_id":ObjectId(result['charity_id'])})
        result['charity_name'] = charity['name']

        # approval = blockchainSetup.checkProjectApproval(result['approval_hash'])
        # if(approval):
        #     return jsonify(result)
        # else:
        #     return jsonify({"code": 400, "error": "This Project is still waiting for approval!"})
        result['charity_description'] = charity['description']
        result['charity_number'] = charity['contact_number']
        result['charity_email'] = charity['email']
        result['charity_address'] = charity['physical_address']
        donations = list(db.donations.find({"project_id": ObjectId(result['_id'])}))
        num = 0
        for d in donations:
            num += d['amount']
        print(num)
        result['actual_amount'] = num
        return jsonify({'code': 200, "result": result})


    except Exception as ex:
        return jsonify({"code": 400, "message":str(ex)})

@app.route("/registerProject", methods=['POST'])
def registerProject():
    charity = request.args.get("charityAddress")
    beneficiary_list_id = request.args.get('beneficiaryListId')
    documentation_id = request.args.get('documentationId')
    beneficiaryGainedRatio = request.args.get('beneficiaryGainedRatio')
    try:
        

        new_beneficiary_list = {
            "project_name": request.form.get('project_name'),
            "beneficiaryList": request.form.getlist('beneficiaryList')
        }
        beneficiary_list_id = db.beneficiaryList.insert_one(new_beneficiary_list)

        new_documentation = {
            "project_name": request.form.get('project_name'),
            'documentation': request.form.get('documentation')
        }
        documentation_id = db.documentation.insert_one(new_documentation)

        txn = blockchainSetup.registerProject(charity, int(beneficiary_list_id), int(documentation_id), int(beneficiaryGainedRatio))

        # need to get project id from blockchain
        numProjects = blockchainSetup.projectContract.methods.numProjects().call()
        print(numProjects)
        new_project = {
            "project_name": request.form.get('project_name'),
            "charity_address": request.form.get('charityAddress'),
            "beneficiaryListId": beneficiary_list_id,
            "documentation": documentation_id,
            "expire_date": request.form.get('expire_date'), 
            "target_amount": request.form.get('target_amount'),
            "description": request.form.get("description"),
            "charity_id":numProjects,
            # "registration_hash": txn,
            "approval_hash": '',
            "reject_hash": ''
        }
        project_id = db.projects.insert_one(new_project)

        return jsonify({
                "code": 200,
                "message": "username or password not correct"
                })

        
    except Exception as ex:
        print(ex)
        print(type(ex))
        return jsonify(
            {"error": str(ex)}
            # {"error": str(ex.args[0]['message'])}
        )

    return jsonify(200)

@app.route("/approveProject", methods=['POST'])
def approveProject():
    projects = db.projects 

    project = request.args.get('projectId')
    inspector = request.args.get('inspectorAddress')
    project_name = request.args.get('project_name')
    try:
        txn = blockchainSetup.approveProject(inspector, int(project))
        result = projects.find_one_and_update(
            {"project_name": project_name},
            {"$set":{
                "approval_hash":txn
            }
            }
        )
        dic = {"txn": txn}
        return jsonify(200)
    except Exception as ex:
        return jsonify({"error":str(ex)})

@app.route("/rejectProject", methods=['POST'])
def rejectProject():
    projects = db.projects

    project = request.args.get('projectId')
    inspector = request.args.get('inspectorAddress')
    project_name = request.args.get('project_name')
    try:
        txn = blockchainSetup.rejectProject(inspector, project)
        result = projects.find_one_and_update(
            {"project_name": project_name},
            {"$set":{
                "reject_hash":txn
            }
            }
        )
        return jsonify(200)
    except Exception as ex:
        return jsonify({"error":str(ex)})

@app.route("/retrieveAllProjects", methods=['GET'])
def retrieveAllProjects():

    projects = db.projects

    try:
        result = list(projects.find({"approval_hash": { "$ne": ""}}))
        print(result)
        print(type(result))
        for i in result:
            i['_id'] = str(i['_id'])
            i['charity_id'] = str(i['charity_id'])
            num = 0
            donations = list(db.donations.find({"project_id": ObjectId(i['_id'])}))
            for d in donations:
                num += d['amount']
            i['actual_amount'] = num
            print(i)

        return jsonify({"code":200, "result": result})
    except Exception as ex:
        return jsonify({"code":400, "message":str(ex)})

@app.route("/retrieveDonorsByProject", methods=['GET'])
def retrieveDonorsByProject():
    try:
        project = db.projects.find_one({"_id":ObjectId(request.args.get("id"))})
        project['_id'] = str(project['_id'])
        donations = list(db.donations.find({"project_id": ObjectId(project['_id'])}))
        for i in donations:
            donor = db.donors.find_one({"eth_address": i['donor_address']})
            i['_id'] = str(i['_id'])
            i['project_id'] = str(i['project_id'])
            i['donor'] = donor['username']

        latestDonors = list(reversed(list(donations)))[0:10]

        return jsonify({"code":200, "latestDonors": latestDonors})
    except Exception as ex:
        return jsonify({"code":400, "message":str(ex)})

@app.route("/donor/login", methods=['GET'])
def loginDonor():
    donors = db.donors
    try:
        results = donors.find_one({"username": request.args.get("username")})
        print(results)
        # print(":::")
        if ( len(results) and results["password"] == request.args.get("password")):
            # print(results["approval_hash"])
            # print("::")
            approval = blockchainSetup.checkDonorApproval(results["approval_hash"],results['eth_address'])
            # print(approval)
            # print(":")

            if(approval):
                return jsonify(
                    {   
                        "code": 200,
                        "id": str(results["_id"]),
                        "username": results["username"],
                        "eth_address": results["eth_address"]
                     }
                )
            else:
                return jsonify({"code":400, "message": "Your account is still waiting for approval!"})

        else:
            return jsonify({"code":400, "message": "username or password not correct"})

    except Exception as ex:
        # print(ex)
        # print(type(ex))
        return jsonify(
            {"error": "username or password not correct"}
        )


@app.route("/charity/login", methods=['GET'])
def loginCharity():
    charities = db.charities
    try:
        print("username", request.args.get("username"))
        results = charities.find_one({"username": request.args.get("username")})
        #approval = blockchainSetup.checkDonorApproval(results["approval_hash"])
        
        print("results: ", results)
        if ( len(results) and results["password"] == request.args.get("password")):
            return jsonify(
                {
                    "code":200,
                    "id": str(results["_id"]),
                    "username": results["username"],
                    "eth_address": results["eth_address"]
                }
            )
        else:
            return jsonify({
                "code": 400,
                "message": "username or password not correct"
                })
        
    except Exception as ex:
        print(ex)
        print(type(ex))
        return jsonify(
            {   
                "code": 400,
                "message": "username or password not correct"
            }
        )

@app.route("/admin/login", methods=['GET'])
def loginAdmin():
    if request.args.get("password") == "admin" and request.args.get("username") == "admin":
        return jsonify({
            "code": 200,
            "eth_address": blockchainSetup.inspectorAddress
            })
    else:
        return jsonify({"code": 400, "message": "Username and Password are not matched!"})



@app.route("/adddummydata",methods=['GET'])
def dummyData():

    i = 0;
    for i in range(3):
        # txn = blockchainSetup.registerOrganization(charity, request.form.get("full_name"))
        new_charity = {
            "username": "charity"+str(i),
            "password": "password"+str(i),
            "email":  "email"+str(i),
            "eth_address": "testing",
            "bank_account": "testing",
            "physical_address": "testing",
            "name": "charity name"+str(i),
            "contact_number": "123456",
            "financial_info": "213123",
            "description": "good charity balahbalahbalah",
            "registration_hash": "yeah",
            "approval_hash": "oh"
        }
        p = 0;
        charity_id = db.charities.insert_one(new_charity)
        for p in range(3):
            new_project = {
                "charity_id": charity_id.inserted_id,
                "project_name": "project_name"+str(i)+str(p),
                "beneficiaryListId": "beneficiary_list_id"+str(i)+str(p),
                "documentation": "documentation"+str(i)+str(p),
                "expiry_date": "2020-05-20",
                "target_amount": 10000,
                "description": "A good charity Project balah balah balah balah balah balah balah balah",
                "registration_hash": "yeah",
                "approval_hash": 'yes',
                "reject_hash": 'oh',
                'project_solidity_id':p
            }
            project_id = db.projects.insert_one(new_project)

    project = db.projects.find_one({"project_name": "project_name00"})

    q = 0;
    for q in range(10):
        new_donor = {
            "username": "donor"+str(q),
            "password": "password"+str(q),
            "email": "email"+str(q),
            "eth_address": "testing"+str(q),
            "bank_account": "testing"+str(q),
            "physical_address": "testing"+str(q),
            "full_name": "name"+str(q),
            "contact_number": "123456",
            "financial_info": "321321",
            "registration_hash": "success",
            "approval_hash": "success"
        }
        donor_id = db.donors.insert_one(new_donor)

        new_donation = {
            "amount": 10,
            "project_id": project["_id"],
            "donor_address": "testing"+str(q),
            "donation_hash": "success",
            "confirmed_hash": ''
        }
        donation_id = db.donations.insert_one(new_donation)

    return jsonify({"code":200})


if __name__ == "__main__":
    app.run(debug=True)


