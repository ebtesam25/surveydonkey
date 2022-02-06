from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
# import tns
# import dataloader

import requests
import json





incomingstate = 0
incomingnum = ""
doctorname = "Dr Victor Von Doom"
patientname = "Reed Richards"
aptdate = "02/01/2022"
apttime = "16:20"

survey =[]
answers = []
qid = "-1"
userid = "-1"
surveyid = "-1"





def answersurvey(answers):
    url = "https://us-central1-aiot-fit-xlab.cloudfunctions.net/surveydonkey"
    
    global userid, surveyid
    payload = {}
    
    payload['action'] = "answersurvey"
    payload['userid'] = userid
    payload['surveyid'] = surveyid
    
    payload['answers'] = answers
    
    pl = json.dumps(payload)
    
    
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=pl)

    print(response.text)

    js = json.loads(response.text)
    
    return js['points']







def getsurvey(id):
    url = "https://us-central1-aiot-fit-xlab.cloudfunctions.net/surveydonkey"

    payload = json.dumps({
    "action": "getsurveybyid",
    "surveyid": id
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    
    js = json.loads(response.text)
    
    return js['questions']


def getuserfromphone(phone):
    
    global userid

    url = "https://us-central1-aiot-fit-xlab.cloudfunctions.net/surveydonkey"

    payload = json.dumps({
    "action": "getuseridfromphone",
    "phone": phone
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    
    js = json.loads(response.text)
    
    if js['status'] == "found":
        name = js['user']['name']
        points = js['user']['points']
        userid = js['user']['id']
        
        return name, points

    
    userid = "-1"
    
    return "unknown", -1





app = Flask(__name__)


def setcreds(nc):
    global cred
    cred = nc

    return "success"



# def syncappdata():
#     global doctorname, patientname, aptdate, apttime
    
#     doctorname, patientname, aptdate, apttime = dataloader.getRRXdata()

@app.route("/smsbase", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""

    global incomingstate, incomingnum, survey, answers, qid, surveyid, userid
    global cred
    # global doctorname, patientname, aptdate, apttime
    
    print(request.values['From'])
    
    incomingnum = request.values['From']
    
    incomingnum = incomingnum.replace('+', '')
    
    print (incomingnum)
    
    n, p = getuserfromphone(incomingnum)
    
    

    incoming = request.values['Body']
    
    incoming = incoming.lower()

    print("incoming text is " + incoming)


    # Start our TwiML response
    resp = MessagingResponse()

    flag = 0
    outstring = "Unfortunately surveydonkey did not understand the following message ..." + incoming

    if incomingstate == 0:
        if 'hello' in incoming:
            if p > -1:
                outstring= "Hello " + n + "! Welcome to SurveyDonkey! You have " + str(p) + " points. Please put respond with survey followed by survey number  to start taking a survey. For example, survey 7" 
                flag = 1
                incomingstate = 1
                resp.message(outstring)

                return str(resp)
            
            outstring= "Hello! Welcome to SurveyDonkey!  Please register on the surveydonkey platform with you phone number to proceed" 
            flag = 1
            incomingstate = 0
            resp.message(outstring)

            return str(resp)
        
            
        
    if incomingstate == 1:
        if 'survey' in incoming or 'start' in incoming:
            
            incoming = incoming.replace('survey ','')
            incoming = incoming.replace('survey','')
            incoming = incoming.replace('sstart ','')
            incoming = incoming.replace('start ','')
            
            
            survey = getsurvey(incoming)
            
            if len(survey) == 0:
                outstring= "Hi "+ n + ", the survey ID  "+ incoming + " is incorrect. Please try again... Thank you for using SurveyDonkey" 
                flag = 1
                incomingstate = 1
                resp.message(outstring)

                return str(resp)
            
            surveyid = incoming
            question = survey.pop(0)
            qid = question['id']
            text = question['text']
            
            outstring= "Hi "+ n + ", you are now taking survey " + incoming + " from SurveyDonkey. question:  "+ text 
            if question['type'] == "mcq":
                options = str(question['options'])
                outstring = outstring +  ". Please respond one of the following options:  " + options
            else:
                outstring = outstring + " Please respond with a short sentence."
            flag = 1
            incomingstate = 2
            resp.message(outstring)

            return str(resp)
    
    
    if incomingstate == 2:
        
        answer = {}
        answer['questionid'] = qid
        answer['answer'] = incomingstate
        answers.append(answer)
        
        
        if len(survey) == 0:
            
            p = str(answersurvey(answers))
            
            outstring= "Hi "+ n + ", Thank you for completing the survey!. You now added " +p + " points to your profile! Thanks again for using SurveyDonkey!" 
            flag = 1
            incomingstate = 0
            survey =[]
            answers = []
            qid = "-1"
            userid = "-1"
            surveyid = "-1"
            resp.message(outstring)
            
            
        else:
            question = survey.pop(0)
            qid = question['id']
            text = question['text']
            
            outstring= "Hi "+ n + ", you are now taking  a survey from SurveyDonkey. Next question:  "+ text 
            if question['type'] == "mcq":
                options = str(question['options'])
                outstring = outstring +  ". Please respond one of the following options:  " + options
            else:
                outstring = outstring + " Please respond with a short sentence."
            flag = 1
            incomingstate = 2
            resp.message(outstring)

            return str(resp)


    # Add a message
    if flag ==0:
        outstring = "Unfortunately surveydonkey did not understand the following message ..." + incoming
    
    resp.message(outstring)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host = 'localhost', port = 8004)
    # app.run(debug=True, host = '45.79.199.42', port = 8004)
