import os
import pymongo
import json
import random
import hashlib
import time

import requests
import uuid



from hashlib import sha256



def hashthis(st):


    hash_object = hashlib.md5(st.encode())
    h = str(hash_object.hexdigest())
    return h



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def initdb():

    mongostr = os.environ.get('MONGOSTR')
    client = pymongo.MongoClient(mongostr)
    db = client["surveydonkey"]

    return client, db





def login_user(email, password, db):
    k = db.employees.find_one({"email":email})

    if k != None:
        # x = bcrypt.hashpw(password.encode('utf-8'), k["password"])

        x = password
        
        
        if x == k["password"]:
            return {"status":"success", "userid" : k['uid']}
        else:
            return {"status":"failed", "userid" : "-1"}

    else:
        return {"status":"failed", "userid" : "-1"}



def get_user_info(email, db):
    k = db.employees.find_one({"email":email})
    k["_id"] = str(k["_id"])
    # k["password"] = str(k["password"])
    k["password"] = "encrypted"
    return k

def update_user(db, uid, field, value):
    
    db.users.update_one({"id":uid}, {"$set": {field:value}})


def getpointmultipliers (sid, gender, age, ethnic, db):
    mul = 1
    col = db.surveyanswers


    return mul





def dummy(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    if request.method == 'OPTIONS':
        # Allows GET requests from origin https://mydomain.com with
        # Authorization header
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Max-Age': '3600',
            'Access-Control-Allow-Credentials': 'true'
        }
        return ('', 204, headers)

    # Set CORS headers for main requests
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Credentials': 'true'
    }

    request_json = request.get_json()



    receiver_public_key = os.environ.get('ownpublic')

    # mongostr = os.environ.get('MONGOSTR')
    # client = pymongo.MongoClient(mongostr)
    # db = client["neurolyzer"]

    client, db = initdb()


    retjson = {}

    action = request_json['action']

    if action == "gettranscriptionstatus":

        headers = {
        "authorization": "ASSSEMBLY AI API KEY",
        "content-type": "application/json"
        }
        id = request_json['id']
        transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

        polling_response = requests.get(transcript_endpoint+"/"+id, headers=headers)

        if polling_response.json()['status'] == "completed":
            retjson['status'] = 1
            retjson['text'] = polling_response.json()['text']
        if polling_response.json()['status'] == "queued":
            retjson['status'] = 0
        if polling_response.json()['status'] == "error":
            retjson['status'] = -1
        return json.dumps(retjson)

    

    if action == "getallsurveys":
        surveys = []
        col = db.surveys

        for x in col.find():
            s = {}
            s['name'] = x['name']
            s['id'] = x['id']
            surveys.append(s)

        # retjson['status'] = status
        retjson['surveys'] = surveys

        return json.dumps(retjson)


    if action == "getallsurveysbyuser":
        surveys = []
        col = db.surveys

        for x in col.find():
            if x['creatorid'] != request_json['creatorid']:
                continue
            s = {}
            s['name'] = x['name']
            s['id'] = x['id']
            surveys.append(s)

        # retjson['status'] = status
        retjson['surveys'] = surveys

        return json.dumps(retjson)



    if action == "getallsurveyanswers":

        col = db.surveys

        for x in col.find():
            if x['id'] != request_json['surveyid']:
                continue
            else:
                retjson['name'] = x['name']
                break

        answers = []
        col = db.questions

        for x in col.find():
            if x['surveyid'] == request_json['surveyid']:
                a = {}
                a['question'] = x['text']
                a['type'] = x['type']
                ans = []
                qid = x['id']
                col2 = db.answers

                for y in col2.find():
                    if y['questionid'] == qid:
                        ans.append(y['answer'])
                a['qid'] = qid
                a['answers'] = ans

                answers.append(a)
        

        retjson['answers'] = answers

        return json.dumps(retjson)
        

        for x in col.find():
            if x['creatorid'] != request_json['creatorid']:
                continue
            s = {}
            s['name'] = x['name']
            s['id'] = x['id']
            surveys.append(s)

        # retjson['status'] = status
        retjson['surveys'] = surveys

        return json.dumps(retjson)


    if action == "getbalancedsurveyanswers":

        col = db.surveys

        for x in col.find():
            if x['id'] != request_json['surveyid']:
                continue
            else:
                retjson['name'] = x['name']
                break

        answers = []
        col = db.questions

        for x in col.find():
            if x['surveyid'] == request_json['surveyid']:
                a = {}
                a['question'] = x['text']
                a['type'] = x['type']
                ans = []
                qid = x['id']
                col2 = db.answers

                for y in col2.find():
                    if y['questionid'] == qid:
                        ans.append(y['answer'])
                a['qid'] = qid
                a['answers'] = ans

                answers.append(a)
        

        if request_json['balanceby'] == 'gender':
            answers2 = [] 
            mcount = 0
            fcount = 0
            ncount = 0
            for a in answers:
                if 'gender' not in a['question']:
                    continue 
                for an in a['answers']:
                    an = an.lower()
                    if an == 'male':
                        mcount +=1
                    if an == 'female':
                        fcount +=1                     
                    if an == 'non-binary':
                        ncount +=1
            
            maxcount = 0
            apos = 0



            if (mcount <= fcount) and (mcount <= ncount):
                maxcount = mcount
  
            elif (fcount <= mcount) and (fcount <= ncount):
                maxcount = fcount
            else:
                maxcount = ncount

            mcount = 0
            fcount = 0
            ncount = 0
            
            flag = 0
            targets = []
            for a in answers:
                if 'gender' not in a['question']:
                    # apos +=1
                    continue
                apos =0
                for an in a['answers']:
                    an = an.lower()
                    if an == 'male':
                        mcount +=1
                        if mcount > maxcount:
                            targets.append(apos)
                            apos+=1
                            mcount -=1
                            continue
                    if an == 'female':
                        fcount +=1
                        if fcount > maxcount:
                            targets.append(apos)
                            apos+=1
                            
                            fcount -=1
                            continue                     
                    if an == 'non-binary':
                        ncount +=1
                        if ncount > maxcount:
                            targets.append(apos)
                            apos+=1
                            
                            ncount -=1
                            continue
                    apos +=1

            
            for a in answers:
                mov = 0
                for t in targets:
                    
                    a['answers'].pop(t-mov)
                    mov += 1

                
                answers2.append(a)


        retjson['answers'] = answers2

        return json.dumps(retjson)


    
    
    

    if action == "getuseridfromphone" :
        col = db.users
        user = {}
        status = "not found"
        for x in col.find():
            if x['phone'] == request_json['phone']:
                status = "found"
                user['id'] = x['id']
                user['name'] = x['name']
                user['phone'] = x['phone']
                user['email'] = x['email']
                user['school'] = x['school']
                user['points'] = x['points']
                
        retjson['status'] = status
        retjson['user'] = user

        return json.dumps(retjson)


    if action == "keygen":
        
        pair = Keypair.random()
        # print(f"Secret: {pair.secret}")
        # Secret: SCMDRX7A7OVRPAGXLUVRNIYTWBLCS54OV7UH2TF5URSG4B4JQMUADCYU
        # print(f"Public Key: {pair.public_key}")
        retjson['status'] = "generated"                
        retjson['secret'] = pair.secret
        retjson['public'] = pair.public_key
        

        return json.dumps(retjson)



    if action == "getuserdata":
        col = db.users
        for x in col.find():
            if int(x['id']) == int(request_json['userid']):
                name = x['name']
                weight = x['weight']
                height = x['height']
                age = x['age']
                gender = x['gender']


                retjson = {}

                # retjson['dish'] = userid
                retjson['status'] = "success"
                retjson['name'] = name
                retjson['height'] = height
                retjson['weight'] =  weight                
                retjson['age'] = age
                retjson['gender'] = gender
                

                return json.dumps(retjson)
        retjson = {}

        # retjson['dish'] = userid
        retjson['status'] = "fail"
        retjson['id'] = "-1"

        return json.dumps(retjson)


    if action == "updateuserdata":
        col = db.users
        for x in col.find():
            if int(x['id']) == int(request_json['id']):
                if 'name' in request_json:
                    col.update_one({"id": x['id']}, {"$set":{"name":request_json['name']}})
                if 'gender' in request_json:
                    col.update_one({"id": x['id']}, {"$set":{"gender":request_json['gender']}})
                if 'height' in request_json:
                    col.update_one({"id": x['id']}, {"$set":{"height":request_json['height']}})
                if 'weight' in request_json:
                    col.update_one({"id": x['id']}, {"$set":{"weight":request_json['weight']}})
                if 'age' in request_json:
                    col.update_one({"id": x['id']}, {"$set":{"age":request_json['age']}})
                    
                        
                # status = x['status']
                # diet = x['diet']
                # allergy = x['allergy']

                retjson = {}

                # retjson['dish'] = userid
                retjson['responsestatus'] = "success"
                # retjson['status'] = status
                # retjson['diet'] = diet
                # retjson['allergy'] = allergy
                

                return json.dumps(retjson)
        retjson = {}

        # retjson['dish'] = userid
        retjson['status'] = "fail"
        retjson['id'] = "-1"

        return json.dumps(retjson)



    if action == "register" :
        maxid = 1
        col = db.users
        for x in col.find():
            id = x["id"]
            maxid +=1
        id = str(maxid+1)

        payload = {}

        uid = id 
        payload["id"] = id
        # payload["uid"] = request_json['uid']
        # payload["name"] = request_json['name']
        payload["name"] = request_json['name']
        payload["email"] = request_json['email']
        payload["password"] = request_json['password']

        payload["phone"] = request_json['phone']

        payload["school"] = request_json['school']

        payload["points"] = 0
        
        
        result=col.insert_one(payload)

        retjson = {}

        # retjson['dish'] = userid
        retjson['status'] = "successfully added"
        retjson['userid'] = id

        return json.dumps(retjson)


    if action == "login":
        col = db.users
        for x in col.find():
            
            if x['email'] == request_json['email'] and x['password'] == request_json['password']:
                userid = x['id']
                name = x['name']
                points = x['points']
                retjson = {}

                # retjson['dish'] = userid
                retjson['status'] = "success"
                retjson['name'] = name
                retjson['userid'] = userid
                retjson['points'] = points

                return json.dumps(retjson)
        retjson = {}

        # retjson['dish'] = userid
        retjson['status'] = "fail"
        retjson['userid'] = "-1"

        return json.dumps(retjson)


    if action == "createsurvey" :
        maxid = 1
        col = db.surveys
        for x in col.find():
            id = x["id"]
            maxid +=1
        id = str(maxid+1)

        payload = {}

        uid = id 
        payload["id"] = id
        # payload["uid"] = request_json['uid']
        # payload["name"] = request_json['name']
        payload["creatorid"] = request_json['creatorid']
        payload["name"] = request_json['name']

        result=col.insert_one(payload)

        sid = id

        col = db.questions
        maxid = 1
        for x in col.find():
            id = x["id"]
            maxid +=1
        id = str(maxid+1)

        questions = request_json['questions']

        for q in questions:
            payload = {}
            payload["id"] = str(maxid+1)
            payload["surveyid"] = sid
            payload["text"] =  q['text']
            payload["type"] = q['type']
            if 'options' in q:
                payload["options"] = q['options']

            # payload["points"] = 0
            
            
            result=col.insert_one(payload)
            maxid +=1

        retjson = {}

        # retjson['dish'] = userid
        retjson['status'] = "successfully added"
        retjson['surveyid'] = sid

        return json.dumps(retjson)


    if action == "answersurvey" :
        maxid = 1
        col = db.surveyanswers
        for x in col.find():
            if x['userid'] == request_json['userid'] and x['surveyid'] == request_json['surveyid']:
                retjson = {}
                retjson['status'] = "error. already filled"
                retjson['points'] = 0
                return json.dumps(retjson)

            id = x["id"]
            maxid +=1
        id = str(maxid+1)

        payload = {}

        uid = id 
        payload["id"] = id
        # payload["uid"] = request_json['uid']
        # payload["name"] = request_json['name']
        payload["userid"] = request_json['userid']
        payload["surveyid"] = request_json['surveyid']

        result=col.insert_one(payload)

        said = id

        col = db.answers
        maxid = 1
        for x in col.find():
            id = x["id"]
            maxid +=1
        id = str(maxid+1)

        answers = request_json['answers']
        points = 0
        for q in answers:
            payload = {}
            payload["id"] = str(maxid+1)
            payload["surveyanswerid"] = said
            payload["questionid"] =  q['questionid']
            payload["answer"] = q['answer']
            points +=1

            # payload["points"] = 0
            
            
            result=col.insert_one(payload)
            maxid +=1
        
        col =  db.users


        col.update_one({"id": request_json['userid']}, {"$inc":{"points":points}})

        retjson = {}

        # retjson['dish'] = userid
        retjson['status'] = "successfully added response"
        retjson['points'] = points

        return json.dumps(retjson)



    if action == "getsurveybyid":
        questions = []
        col = db.questions
        for x in col.find():
            if int(x['surveyid']) == int(request_json['surveyid']):
                q = {}
                q['id'] = x['id']
                q['text'] = x['text']
                q['type'] = x['type']
                options = []
                if 'options' in x:
                    for o in x['options']:
                        options.append(o)
                    q['options'] = options
                
                questions.append(q)
            
        retjson = {}

        # retjson['dish'] = userid
        retjson['surveyid'] = request_json['surveyid']
        retjson['questions'] = questions

        return json.dumps(retjson)

    retstr = "action not done"

    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return retstr
