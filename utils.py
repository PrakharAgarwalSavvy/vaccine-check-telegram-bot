import pandas as pd
from copy import deepcopy

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

def set_user_data(context,filter_name,text_input):
    context.user_data[filter_name]=text_input
    
def set_message_reply(update,context,message,new_filter):
    update.message.reply_text(
                message
            )
    set_user_data(context,new_filter,1)

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
        
def create_error_message_df(message,value,final_df):
    # initialize list of lists
    message = message + value
    data = [[message]]
  
    # Create the pandas DataFrame
    final_df = pd.DataFrame(data, columns = ['message'])
    return final_df
    