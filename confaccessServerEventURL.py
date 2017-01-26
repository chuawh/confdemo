from flask import Flask,render_template,request, Response
import requests
import json
from jose import jwt

app = Flask(__name__)

dict={}
retries = 0

@app.route('/confaccess',methods=['GET', 'POST'])
def Conf_NCCO():
    global retries
    print ("number of retry: " + str(retries))
    webhookContent=request.json
    print("In Conf_NCCO: " + str(webhookContent))
    #extract access code from call event (INPUT) send from VAPI server
    # {
    #     "conversation_uuid": "63f61863-4a51-4f6b-86e1-46edebcf9929",
    #     "timed_out": true,
    #     "dtmf": "3109"
    # }
    max_retries = 2
    if 'dtmf' in webhookContent and retries < max_retries:
        access_code = webhookContent['dtmf']
        conv_uuid = webhookContent['conversation_uuid']
        if access_code == "1234" and retries < max_retries:
            print("You are moderator")
            #NCCO for moderator
            ncco=[
                    {
                      "action": "talk",
                      "text": "You have entered the conference",
                      "voiceName": "Amy"
                    },
                    {
                      "action": "conversation",
                      "name": "nexmo-conference-moderated",
                      "endOnExit": "true",
                      "record": "true",
                      "eventUrl":["http://533a94ee.ngrok.io/confaccess"]
                 }]
            retries = 0
        elif access_code == "0000" and retries < max_retries:
            #NCCO for atttendee
            print("You are attendee")
            ncco= [{
                    	"action": "talk",
                    	"text": "Welcome to a Wei Hong moderated conference",
                    	"voiceName": "Amy"
                	  },
                	  {
                    	"action": "conversation",
                    	"name": "nexmo-conference-moderated",
                    	"startOnEnter": "false",
                    	"musicOnHoldUrl": ["https://nexmo-community.github.io/ncco-examples/assets/voice_api_audio_streaming.mp3"],
                    	"eventUrl":["http://533a94ee.ngrok.io/confaccess"]
                	 }]
            retries = 0
        elif (access_code != "0000" or access_code !="1234") and retries < max_retries:
            print(retries)
            print("Wrong access code, Retry NCCO")
            ncco=[{
                        "action": "talk",
                        "text": "You have entered the wrong access code, please try again",
                        "bargeIn": "true",
                        "voiceName": "Amy"
                      },
                      {
                        "action": "input",
                        "submitOnHash": "true",
                        "timeout": 10,
                        "eventUrl": ["http://533a94ee.ngrok.io/confaccess"]
                     }]
            retries += 1
        else:
            print("Retry exceeded")
            ncco= [{
                     "action": "talk",
                     "text": "You have exceeded number of try, Good Bye",
                     "bargeIn": "true",
                     "voiceName": "Amy"
                 }]
            retries = 0

    #Response NCCO to VAPI
        js=json.dumps(ncco)
        print(js)
        resp=Response(js, status=200, mimetype='application/json')
        print(resp)
        return resp
    else:
        return "ok"

if __name__=='__main__':
    app.run()
