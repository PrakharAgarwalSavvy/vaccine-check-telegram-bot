# vaccine-check-telegram-bot
A telegram bot that gives you available vaccine centers in the given district and pincode. It also gives feature of automatic notifications on subscribing.

In this bot users will be asked questions and based on the answers ( works as filters ) , they will be provided with the availibality centers .

PREREQUISITS:
  -Put your bot token from botfather in config.py
  -Install all the imported libraries in api_final and main_final
 
RUN:
  -python3 main_final.py

PROCESS:
  - To start , user has to type /start or start.
  - Then below questions will be asked one by one

    1. Enter District name.
    2. Enter pincode
    3. Enter date range (Any number between 1 to 14)
    4. Provide age group (Type 18 or 45)
    5. Enter Payment type (Type Free or Paid or Both)
  Questions cannot be left blank .

  - Once all answers are given , user will get the response . 
    AVAILABLE Response format 
       [PINCODE]
       Age group: AGE_GROUP_ANSWER
       Hospital Name: HOSPITAL_NAME
       Date: AVAILABILITY_DATE
       Available Capacity: TOTAL_CAPACITY
       Dose 1 Available Capacity: DOSE1 CAPACITY
       Dose 2 Available Capacity: DOSE2 CAPACITY
       Vaccine: VACCINE_TYPE
       Fee type: PAYEMENT_TYPE ( FREE or PAID)
       AMOUNT: In case of PAID

     NOT AVAILABLE Reponse
       Vaccines are not available in any center.

  - Then user will be given few options 
      Wish to change any of the filter and search again ? Please press /continue.   
      To subscribe with the current filters, press /subscribe. You will get automatic notifications as soon as there will be an update.       
      Press /start for a fresh search.
      For any help or suggestion. Press /help.
      Press /exit to quit searching.
      
  - /continue is to give answer to any one of the filter. Rest will remain same.
  - /subscribe - User can also subscribe and they will get automatic notifications as soon as there will be a change/update from the previous response. 
        We are hitting the api on every 15 mins and comparing the current response with the previous one. 
        If the current and previous responses are same there will be no message. 
  - /start will begin questions again.
  - /help is for messaging the developer in order to provide suggesion or feed back.    
  - /exit will end the conversion and given answers will be lost.
  
NOTE: User can quit any time by one of the given option , it could be quit or done or exit.


RUN 24*7
  -To make it run 24*7. Deploy it in any aws cloud service. I used AWS EC2 instance. Chose Ubuntu 18.04 AMI, installed python over there and ran the below command.
            nohop python3 main_final.py & 
   this will run the script in background.
