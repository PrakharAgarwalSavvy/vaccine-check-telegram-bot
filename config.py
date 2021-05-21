CHAT_TIMEOUT=120

URL="https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}"

CONT_MESSAGE = ("Please reply with the selected option number." 
             "\n1. Enter pincode "
             "\n2. Enter date range (Any number between 1 to 14)" 
             "\n3. Provide age group (Type 18 or 45)"
             "\n4. Enter Payment type (Type Free or Paid or Both) " 
             "\n5. For any kind of help or suggestion "
             "\n6. Exit")
             
INVALID_CONT_MESSAGE = "Selected option is not valid."

EXIT_COMMANDS = "^(Done|Exit|Quit|done|exit|quit)$"
CHOOSING_NUMS_REGEX = "^(1|2|3|4|5|6|[0-9]+)$"

TELEGRAM_PROFILE_LINK='telegram.me/AgarwalPrakhar'

BOT_TOKEN='YOUR_BOT_TOKEN_HERE'

RESP_END_MESSAGE= ("Wish to change any of the filter and search again ? Please press /continue. "
                    "\nTo subscribe with the current filters, press /subscribe. You will get automatic notifications as soon as there will be an update."           
                    "\npress /start for a fresh search. "
                    "\nFor any help or suggestion. Press /help."
                    "\nPress /exit to quit searching.")
                    
UNSUBSCRIBE_MESSAGE = ("To unsubscribe or to change filters, press /unsubscribe.")

DISTRICT_NAME_MESSAGE= "Lets get started. \nPlease enter the district name."
INVALID_DISTRICT_NAME_MESSAGE = "Provided district name is not correct.Please try again."             

DATE_RANGE_MESSAGE = "Provide date range (Type any number between 1 to 14) Example: If answerd 5 then slots will be checked for next 5 days from today."
INVALID_DATE_RANGE_MESSAGE = "Provided date range is not valid.Date range must be a number between 1 to 14. Please try again."

AGE_GROUP_MESSAGE =  "Provide age group (Type 18 for 18+ age group or 45 for 45+ age group.)"
INVALID_AGE_GROUP_MESSAGE =  "Provided age group is not valid. Type 18 for 18+ age group or 45 for 45+ age group.Please try again."

PINCODE_MESSAGE="Please enter pincode"  
INVALID_PINCODE_MESSAGE =  "Provided pin code is not valid. Please try again."
           
PAYMENT_MESSAGE =  "Choose Vaccination Payment (Type Free or Paid or Both)"
INVALID_PAYMENT_MESSAGE =  'Provided payment type is not valid.  Type Free or Paid or Both. Plese try again.'

TECHNICAL_ERROR_MESSAGE =  'Unable to fetch due to some technical error. Please type /start to check again after some time.'
        
HELP_MESSAGE = 'Would love to hear you back. Click on the below button to text me your query/suggestion. Thanks.'

EXIT_MESSAGE= "Thanks. Wear Mask & Stay safe. Press /start to begin the search again."

SUBSCRIBE_MESSAGE = 'Thanks for subscribing. You will get automatic notifications as soon as there will be an update on the given filters. To stop getting automatic notification, please type /unsubscribe.'

INACTIVITY_MESSAGE = 'Sorry Chat is ended due to the inactivity. Press /start to try again. '

DEVELOPER_MESSAGE='Message the developer'

RENAME_MAPPING = {
    'date': 'Date',
    'min_age_limit': 'Minimum Age Limit',
    'available_capacity': 'Available Capacity',
    'vaccine': 'Vaccine',
    'pincode': 'Pincode',
    'name': 'Hospital Name',
    'state_name' : 'State',
    'district_name' : 'District',
    'block_name': 'Block Name',
    'fee_type' : 'Fees',
    'fee_amount': 'Amount',
    'available_capacity_dose1': 'Dose 1 Available Capacity',
    'available_capacity_dose2': 'Dose 2 Available Capacity',
    }

NO_CENTER_MESSAGE="No centers available for booking"    
NO_VACCINE_MESSAGE = "Vaccines are not available in any center."
NO_VACCINE_PINCODE_MESSAGE = 'No Vaccination centers are available for booking in Pincode '
DATAFRAME_EMPTY_MESSAGE = 'Dataframe is empty'
