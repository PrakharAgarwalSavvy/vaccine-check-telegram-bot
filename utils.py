import pandas as pd
from copy import deepcopy
import logging
import datetime
import logging.handlers as handlers

logger = logging.getLogger('MAIN_FINAL')
logger.setLevel(logging.INFO)

logHandler = handlers.TimedRotatingFileHandler('logs/main_logger.log', when='m', interval=1)
logHandler.setLevel(logging.INFO)
fileformatter = logging.Formatter('%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s')
logHandler.setFormatter(fileformatter)
logger.addHandler(logHandler)

def load_mapping():
    df = pd.read_csv("district_mapping.csv")
    return df

def date_range_validation(text):
    if (int(text) in range(1,15)):
        return True
    else:
        return False

def pincode_validation(text):
    if ( len(text) == 6 ):
        return True
    else:
        return False

def age_group_validation(text):
     valid_age = [18, 45]
     if (int(text) in valid_age):
        return True
     else:
        return False

def payment_validation(text):
     valid_payments = ["Free", "Paid", "Both"]
     if text != "":
        text = text[0].upper() + text[1:]
        if (text in valid_payments):
            return True
        else:
            return False  

def set_user_data(context,key_name,value):
    context.user_data[key_name]=value
    
def set_message_reply(update,context,message,key_name):
    update.message.reply_text(
                message
            )
    set_user_data(context,key_name,1)

def send_reply_text(update,message,arg):
    if(arg == 'HTML'):
        update.message.reply_text(
            message,parse_mode='HTML'
        )
    elif(arg == None):
        update.message.reply_text(
            message
        )
    else:
        update.message.reply_text(
            message,reply_markup=arg
        )
#api_final method
def filter_column(df, col, value):
    df_temp = deepcopy(df.loc[df[col] == value, :])
    return df_temp

def filter_capacity(df, col, value):
    df_temp = deepcopy(df.loc[df[col] > value, :])
    return df_temp
    
def check_empty_df(final_df):
    if final_df.empty:
        return True
    else:
        return False
        
def create_error_message_df(message,value):
    # initialize list of lists
    message = message + value
    data = [[message]]
  
    # Create the pandas DataFrame
    final_df = pd.DataFrame(data, columns = ['message'])
    return final_df
    
def do_logging(method_name, update_id,message_id,chat_id, e):
    if e == None:
        msg = "method name = {} :: update_id = {} :: message_id = {} :: chat_id = {}"
        logger.debug(msg.format(method_name,update_id,message_id,chat_id))
    elif(isinstance(e, dict)):
        msg = "method name = {} :: update_id = {} :: message_id = {} :: chat_id = {} :: UserData :: {}"
        logger.debug(msg.format(method_name,update_id,message_id,chat_id, e))
    else:
        msg = "method name = {} :: update_id = {} :: message_id = {} :: chat_id = {} :: Exception :: {}"
        logger.error(msg.format(method_name,update_id,message_id,chat_id, e))
        
def isSubscribed(userdata):
    isSubscribe= userdata.get('subscribe')
    if(isSubscribe == None or isSubscribe != 'yes'):
        return False
    else:
        return True
        
def print_filters(update,context):
    msg="";
    for key, value in context.user_data.items():
            if(key == 'dist_name'):
                msg = msg + '\n<b>Distict Name : </b>' + value 
            if(key == 'date_range'):
                if(value == '1'):
                    msg = msg + '\n<b>Date Range </b>: ' + value + ' (Today)'
                else:
                    msg = msg + '\n<b>Date Range </b>: ' + value + ' days from today.'
            if(key == 'pincode' and value != '000000'):
                msg = msg + '\n<b>Pincode </b>: ' + value 
            if(key == 'age_limit'):
                msg = msg + '\n<b>Age Group </b>: ' + value +'+'
            if(key == 'payment'):
                if (value == 'Both'):
                    msg = msg +  '\n<b>Payment Type </b>: ' + value +' ( Free and paid )'
                else:
                    msg = msg +  '\n<b>Payment Type </b>: ' + value
            if(key == 'vaccine_type'):
                msg = msg +  '\n<b>Vaccine </b>: ' + value 
            if(key == 'dose_avail'):
                msg = msg +  '\n<b>Dose Availability </b>: Dose ' + value  
    send_reply_text(update,msg,'HTML') 
