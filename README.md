# vaccine-check-telegram-bot
A telegram bot that gives you available vaccine centers in the given district and pincode. In case pincode is not known, user can search with only district. It also gives feature of automatic notifications on subscribing.

In this bot users will be asked questions and based on the answers ( works as filters ) , they will be provided with the availibality centers .

#PREREQUISITS:

  - Put your bot token from botfather in config.py
  - Install all the imported libraries used in api_final and main_final.
 
#RUN:

        python3 main_final.py

#PROCESS:

  - To start , user has to type /start or start. Then choose from one of the below two options.
    
        Please type choosen option number from below two options.
        1. Search by district and pincode.
        2. Search only by district
        
  - Based on the chosen option ,  below questions will be asked one by one

        1. Enter District name.
        2. Enter pincode  
        3. Enter date range (Any number between 1 to 14)
        4. Provide age group (Type 18 or 45)
        5. Enter Payment type (Type Free or Paid or Both)
        
    NOTE: Pincode will be asked only if option 1 is chosen.
 
    Answers Validations:
    
      Question 1 -  Valid district name.\
      Question 2 -  Only 6 digits numbers.\
      Question 3 -  Can only be numbers and must be between 1 and 14 ( inclusive 14 )\
      Question 4 -  either 18 or 45 as answers.\
      Question 5 -  can only have free or paid or both as answers.          
      

  - Once all answers are given , user will get the response.
    
       AVAILABLE Response format
         
          [PINCODE]
          Age group: AGE_GROUP_ANSWER
          Hospital Name: HOSPITAL_NAME
          Address: HOSPITAL_ADDRESS
          Date: AVAILABILITY_DATE
          Available Capacity: TOTAL_CAPACITY
          Dose 1 Available Capacity: DOSE1_CAPACITY
          Dose 2 Available Capacity: DOSE2_CAPACITY
          Vaccine: VACCINE_TYPE
          Fee type: PAYEMENT_TYPE ( FREE or PAID)
          AMOUNT: In case of PAID Fee Type

     NOT AVAILABLE Reponse
       
          Vaccines are not available in any center.

  - After above response , user will be given few other choices as below
      
          Wish to change any of the filter and search again ? Please press /continue. 
          To subscribe with the current filters, press /subscribe. You will get automatic notifications as soon as there will be an update.
          Press /repeat to repeat search with current filters. 
          Press /start for a fresh search. 
          Press /check to check filters 
          For any help or suggestion. Press /help.
          Press /exit to quit searching.
          
      <b>/continue</b> is to give answer to any one of the filter. Rest will remain same.\
      <b>/subscribe</b> - User can also subscribe and they will get automatic notifications as soon as there will be a change from the previous response.\
              We are hitting the api on every 2 mins and comparing the current response with the previous one.\
              If the current and previous responses are same there will be no message.\
      <b>/start</b> will begin questions again.\
      <b>/check</b> will give you current chosen filters.
      <b>/help</b> is for messaging the developer in order to provide suggesion or feed back.\
      <b>/exit</b> will end the conversion and given answers will be lost.
     
  - If /continue is pressed , you will get below options to change the filter

        Please reply with the selected option number.
        1. Enter pincode 
        2. Enter date range (Any number between 1 to 14)
        3. Provide age group (Type 18 or 45)
        4. Enter Payment type (Type Free or Paid or Both) 
        5. Choose Vaccine Type. 
        6. Looking for specific dose availability ?
        7. Go to Previous options. 
        8. Exit

    User has to type the selected option number.
  
    <b>NOTE:</b> User can quit any time by one of the given option , it could be quit or done or exit.

#TO RUN 24*7
  
   - Deploy it in any aws cloud service. I used AWS EC2 instance. Chose Ubuntu 18.04 AMI, installed python over there and ran the below command.
   
         nohop python3 main_final.py &
   
     this will run the script in background.
   
   - Now if you want to stop the above running process , you have to find first find the pid of the background running script and then kill it .
     Run below command to find the pid
   
         ps -fA | grep python  
     
     then kill it with below command  
     
         sudo kill -9 <PID>
   
   - In case you EC2 instance is showing UTC time zone. please follow below steps to modify the timezone.
     Check your current time zone by

          $ date
     To change it, run

          $ sudo dpkg-reconfigure tzdata
     This will show list of geographical areas. Select to narrow down available time zones. Next select city/timezone. And you have changed system to new timezone.
    
