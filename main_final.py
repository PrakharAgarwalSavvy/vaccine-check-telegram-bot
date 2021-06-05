import pandas as pd
import api_final as api
import utils
import time
import schedule
import config as cfg
from typing import Dict
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove, InlineKeyboardMarkup,InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from threading import Thread
from time import sleep
import re

CHOOSING, DATE_RANGE, PINCODE, MIN_AGE_LIMIT, PAYMENT, RESULT, CHANGE_FILTER,UNSUBSCRIBE, CONT_CHOOSING, START_CHOOSING, SKIP_PINCODE = range(11)

mapping_df = utils.load_mapping()

mapping_dict = pd.Series(mapping_df["district id"].to_list(),
                         map(lambda x:x.lower(),mapping_df["district name"].to_list())).to_dict()
                         
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(cfg.START_MESSAGE)
    return START_CHOOSING    
              

def continueChoosing(update: Update, context: CallbackContext) -> int:           
    utils.send_reply_text(update,cfg.CONT_MESSAGE,None)
    return CONT_CHOOSING
    
def need_help(update: Update, context: CallbackContext):
    user_data = context.user_data   
    reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text=cfg.DEVELOPER_MESSAGE, url=cfg.TELEGRAM_PROFILE_LINK)]
    ]) 
    utils.send_reply_text(update,cfg.HELP_MESSAGE,reply_markup)
    return CONT_CHOOSING
    
def search_again(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    utils.set_user_data(context,'previous_response',pd.DataFrame())
    if utils.isSubscribed(context.user_data):
        utils.set_user_data(context,'subs_cont','1')
    else:
        utils.set_user_data(context,'subs_cont','0')
    for key in list(context.user_data.keys()):
        if(key.startswith('new_')):
           del context.user_data[key]
    try:
        int(text)
        if(int(text) in range(1,9)):
            if (text == '1'):
                utils.set_message_reply(update,context,cfg.PINCODE_MESSAGE,'new_pincode')
                return CHANGE_FILTER
            if (text == '2'):
                utils.set_message_reply(update,context,cfg.DATE_RANGE_MESSAGE,'new_date_range')
                return CHANGE_FILTER
            if (text == '3'):
                utils.set_message_reply(update,context,cfg.AGE_GROUP_MESSAGE,'new_age_limit')
                return CHANGE_FILTER
            if (text == '4'):
                utils.set_message_reply(update,context,cfg.PAYMENT_MESSAGE,'new_payment')
                return CHANGE_FILTER
            if (text == '5'):
                utils.set_message_reply(update,context,cfg.VACCINE_TYPE_MESSAGE,'new_vaccine_type')
                return CHANGE_FILTER
            if (text == '6'):
                utils.set_message_reply(update,context,cfg.DOSE_AVAILABILITY_MESSAGE,'new_dose_avail')
                return CHANGE_FILTER
            if (text == '7'):
                utils.send_reply_text(update,cfg.RESP_END_MESSAGE,None)
                return CHOOSING
            if (text == '8'):
                return done(update,context)
        else:                  
            utils.send_reply_text(update,cfg.INVALID_CONT_MESSAGE,None)        
            utils.send_reply_text(update,cfg.CONT_MESSAGE,None)
    except:  
        utils.send_reply_text(update,cfg.INVALID_CONT_MESSAGE,None)        
        utils.send_reply_text(update,cfg.CONT_MESSAGE,None)
        
    return CONT_CHOOSING
    
def change_filter(update: Update, context: CallbackContext) -> int:
    user_data=context.user_data
    text = update.message.text
    for key, value in user_data.items():
        updated_filter_key=''
        if ((key.startswith("new_")) and (value == 1)):
            updated_filter_key = key
            updated_filter_value = value
    new_filter_name = updated_filter_key.replace('new_','')
    if(new_filter_name == 'date_range'):
        try:
            if (utils.date_range_validation(text)):
                utils.set_user_data(context,new_filter_name,text)
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING
            else:
                raise Exception(cfg.INVALID_DATE_RANGE_MESSAGE)
        except Exception as e :
            utils.do_logging('change_filter date_range',update.update_id,update.message.message_id,update.message.chat_id, e)
            utils.send_reply_text(update,cfg.INVALID_DATE_RANGE_MESSAGE,None)
            return CHANGE_FILTER
    if(new_filter_name == 'pincode'):
        try:
            if (utils.pincode_validation(text)):
                utils.set_user_data(context,new_filter_name,text)
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING
            else:
                raise Exception(cfg.INVALID_PINCODE_MESSAGE)
        except Exception as e:
            utils.do_logging('change_filter pincode',update.update_id,update.message.message_id,update.message.chat_id, e)
            utils.send_reply_text(update,cfg.INVALID_PINCODE_MESSAGE,None)            
            return CHANGE_FILTER
            
    if(new_filter_name == 'age_limit'):
        try:
            if (utils.age_group_validation(text)):
                utils.set_user_data(context,new_filter_name,text)
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING
            else:
                raise Exception(cfg.INVALID_AGE_GROUP_MESSAGE)
        except Exception as e:
            utils.do_logging('change_filter age_limit',update.update_id,update.message.message_id,update.message.chat_id, e)
            utils.send_reply_text(update,cfg.INVALID_AGE_GROUP_MESSAGE,None)
            
            return CHANGE_FILTER
            
    if(new_filter_name == 'payment'):
        try:
            if (utils.payment_validation(text)):
                text = text[0].upper() + text[1:]
                utils.set_user_data(context,new_filter_name,text)
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING
            else:
                raise Exception(cfg.INVALID_PAYMENT_MESSAGE)
        except Exception as e:
            utils.do_logging('change_filter payment',update.update_id,update.message.message_id,update.message.chat_id, e)
            utils.send_reply_text(update,cfg.INVALID_PAYMENT_MESSAGE,None)           
            return CHANGE_FILTER
            
    if(new_filter_name == 'vaccine_type'):
        try:
            int(text)
            if(text == '1'):
                text='COVAXIN'
                utils.set_user_data(context,new_filter_name,text)
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING
            elif(text == '2'):
                text='COVISHIELD'
                utils.set_user_data(context,new_filter_name,text)
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING
            elif(text == '3'):
                text='SPUTNIK V'
                utils.set_user_data(context,new_filter_name,text)
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING
            elif(text == '4'):
                del context.user_data[new_filter_name]
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING   
            else:
                raise Exception(cfg.INVALID_VACCINE_TYPE_MESSAGE)
        except Exception as e:
            utils.do_logging('change_filter vaccine type',update.update_id,update.message.message_id,update.message.chat_id, e)
            utils.send_reply_text(update,cfg.INVALID_VACCINE_TYPE_MESSAGE,None)           
            return CHANGE_FILTER
            
    if(new_filter_name == 'dose_avail'):
        try:
            int(text)
            if(text == '1' or text == '2'):
                utils.set_user_data(context,new_filter_name,text)
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING
            elif(text == '3'):
                del context.user_data[new_filter_name]
                if not utils.isSubscribed(context.user_data):
                    # if changing filter when subscribed then no immediate api call. 
                    call_api(update,context)
                else:
                    utils.send_reply_text(update,'Filter changed successfully. Now updates will be on below filters :',None) 
                    utils.print_filters(update,context)
                    utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)
                return CHOOSING
            else:
                raise Exception(cfg.INVALID_DOSE_AVAILABILITY_MESSAGE)
        except Exception as e:
            utils.do_logging('change_filter dose avail',update.update_id,update.message.message_id,update.message.chat_id, e)
            utils.send_reply_text(update,cfg.INVALID_DOSE_AVAILABILITY_MESSAGE,None)           
            return CHANGE_FILTER        
            

def get_dist_name(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
     int(text)
     if(text == '1' or text == '2'):
        utils.set_user_data(context,'choice',text)
        utils.send_reply_text(update,cfg.DISTRICT_NAME_MESSAGE,None)
        utils.set_user_data(context,'previous_response',pd.DataFrame())
        return DATE_RANGE
     else:
        utils.send_reply_text(update,cfg.INVALID_START_MESSAGE,None)
        return START_CHOOSING
    except Exception as e:
        utils.do_logging('get_dist_name',update.update_id,update.message.message_id,update.message.chat_id, e)
        utils.send_reply_text(update,cfg.INVALID_START_MESSAGE,None)
        return START_CHOOSING
    

def get_date_range(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    choice_taken = context.user_data['choice']
    try:
        DIST_ID = mapping_dict[text.lower()]
        utils.set_user_data(context,'dist_id',DIST_ID)
        utils.set_user_data(context,'dist_name',text.lower())
        utils.send_reply_text(update,cfg.DATE_RANGE_MESSAGE,None)
        if(choice_taken == '1'):
            return PINCODE 
        else:
            return SKIP_PINCODE
    except Exception as e:
        utils.do_logging('get_date_range',update.update_id,update.message.message_id,update.message.chat_id, e)
        utils.send_reply_text(update,cfg.INVALID_DISTRICT_NAME_MESSAGE,None)
        return DATE_RANGE

def skip_pincode(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    utils.do_logging('skip_pincode',update.update_id,update.message.message_id,update.message.chat_id, None)
    try:
        if (utils.date_range_validation(text)):
            utils.set_user_data(context,'date_range',text)
            utils.set_user_data(context,'pincode','000000')
            utils.send_reply_text(update,cfg.AGE_GROUP_MESSAGE,None)
            return PAYMENT
        else:
            raise Exception(cfg.INVALID_DATE_RANGE_MESSAGE)
    except Exception as e:
        utils.do_logging('skip_pincode',update.update_id,update.message.message_id,update.message.chat_id, e)
        utils.send_reply_text(update,cfg.INVALID_DATE_RANGE_MESSAGE,None)
        return SKIP_PINCODE
    
         
def get_pincode(update: Update, context: CallbackContext) -> int:
    utils.do_logging('get_pincode',update.update_id,update.message.message_id,update.message.chat_id, None)
    text = update.message.text
    choice_taken = context.user_data['choice']
    try:
        if (utils.date_range_validation(text)):
            utils.set_user_data(context,'date_range',text)
            utils.send_reply_text(update,cfg.PINCODE_MESSAGE,None)
            return MIN_AGE_LIMIT
        else:
            raise Exception(cfg.INVALID_DATE_RANGE_MESSAGE)
    except Exception as e:
        utils.do_logging('get_pincode',update.update_id,update.message.message_id,update.message.chat_id, e)
        utils.send_reply_text(update,cfg.INVALID_DATE_RANGE_MESSAGE,None)
        return PINCODE
    
def get_min_age_limit(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        int(text)
        utils.set_user_data(context,'pincode',text)
        if ( utils.pincode_validation(text) ):
            utils.send_reply_text(update,cfg.AGE_GROUP_MESSAGE,None)
            return PAYMENT
        else:
            raise Exception(cfg.INVALID_PINCODE_MESSAGE)
    except Exception as e:
        utils.do_logging('get_min_age_limit',update.update_id,update.message.message_id,update.message.chat_id, e)
        utils.send_reply_text(update,cfg.INVALID_PINCODE_MESSAGE,None)
        return MIN_AGE_LIMIT
      
    
def get_payment_type(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        if (utils.age_group_validation(text)):
            utils.set_user_data(context,'age_limit',text)
            utils.send_reply_text(update,cfg.PAYMENT_MESSAGE,None)
            return RESULT
        else:
            raise Exception(cfg.INVALID_AGE_GROUP_MESSAGE)
    except Exception as e:
        utils.do_logging('get_payment_type',update.update_id,update.message.message_id,update.message.chat_id, e)
        utils.send_reply_text(update,cfg.INVALID_AGE_GROUP_MESSAGE,None)
        return PAYMENT

def get_result(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if (utils.payment_validation(text)):
        text = text[0].upper() + text[1:]
        utils.set_user_data(context,'payment',text)
        call_api(update,context)
        return CHOOSING
    else:
        utils.send_reply_text(update,cfg.INVALID_PAYMENT_MESSAGE,None)
        return RESULT
        
def do_repeat(update: Update, context: CallbackContext) -> int:
    utils.set_user_data(context,'previous_response',pd.DataFrame())
    call_api(update,context)
    return CHOOSING
        
def call_api(update: Update, context) -> int:  
    user_data = context.user_data
    utils.do_logging('call_api',update.update_id,update.message.message_id,update.message.chat_id, dict(user_data))
    try:
        final_df=api.get_availability(user_data,update)
        final_df_previous_response = user_data['previous_response']
        if(final_df_previous_response.empty):
            utils.do_logging('First Response call for call_api',update.update_id,update.message.message_id,update.message.chat_id, None)
            return print_after_serialize_ex(update,context,final_df)
        else:
            compared_df = final_df.compare(final_df_previous_response)
            if not compared_df.empty:
               utils.do_logging('second onwards Response call for call_api with change',update.update_id,update.message.message_id,update.message.chat_id, dict({"compared_df":compared_df}))
               return print_after_serialize_ex(update,context,final_df)
            else:
                utils.do_logging('second onwards Response call for call_api with no change',update.update_id,update.message.message_id,update.message.chat_id, dict({"compared_df":compared_df}))
    except ValueError as ve:
        #this is a change show the response
        utils.do_logging('call_api value error exception block',update.update_id,update.message.message_id,update.message.chat_id, ve)
        return print_after_serialize_ex(update,context,final_df)
    except Exception as e:  
        utils.do_logging('call_api all exception block',update.update_id,update.message.message_id,update.message.chat_id, e)
        final_df_previous_response = user_data['previous_response']        
        if(final_df_previous_response.empty):
            return print_exception(update,context)
        else:
            try:
                message = final_df_previous_response['message'].tolist()
            except:
                return print_exception(update,context)

def print_exception(update,context):
        user_data = context.user_data
        final_df = utils.create_error_message_df(cfg.TECHNICAL_ERROR_MESSAGE,'')
        serialize_ex(final_df,update)
        if not utils.isSubscribed(user_data):  
            utils.send_reply_text(update,cfg.MAIN_TECHNICAL_ERROR_MESSAGE_UNSUB,None)
            utils.send_reply_text(update,cfg.RESP_END_MESSAGE,None)
        else:
            utils.send_reply_text(update,cfg.MAIN_TECHNICAL_ERROR_MESSAGE_SUB,None)         
        utils.set_user_data(context,'previous_response',final_df)
        return True

            
def print_after_serialize_ex(update,context,final_df):
        user_data = context.user_data
        serialize_ex(final_df,update)
        if not utils.isSubscribed(user_data):
            utils.send_reply_text(update,cfg.RESP_END_MESSAGE,None)
        else:
            utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)    
        utils.set_user_data(context,'previous_response',final_df)
        return True
    
def serialize_ex(df,update):
    for index, row in df.iterrows():
        if ('message' in df.columns):
            utils.send_reply_text(update,str(row["message"]),None)  
        else:
            if(row["Fees"] == 'Free'):
                result = '<b>[' +str(row["Pincode"])+ ']</b>'+ '\n <b>Age group: </b>' + str(row["Minimum Age Limit"]) +'\n <b>Hospital Name: </b>' + str(row["Hospital Name"]) + '\n <b>Address: </b>' + str(row["Address"]) + '\n <b>Date: </b>' + str(row["Date"])+ '\n <b>Available Capacity: </b>' + str(row["Available Capacity"]) + '\n <b>Dose 1 Available Capacity: </b>' + str(row["Dose 1 Available Capacity"]) + '\n <b>Dose 2 Available Capacity: </b>' + str(row["Dose 2 Available Capacity"]) + '\n <b>Vaccine: </b>' + str(row["Vaccine"]) + '\n <b>Fee type: </b>' + str(row["Fees"])
            else:
                result = '<b>[' +str(row["Pincode"])+ ']</b>'+ '\n <b>Age group: </b>' + str(row["Minimum Age Limit"]) +'\n <b>Hospital Name: </b>' + str(row["Hospital Name"]) + '\n <b>Address: </b>' + str(row["Address"]) +'\n <b>Date: </b>' + str(row["Date"])+ '\n <b>Available Capacity: </b>' + str(row["Available Capacity"]) + '\n <b>Dose 1 Available Capacity: </b>' + str(row["Dose 1 Available Capacity"]) + '\n <b>Dose 2 Available Capacity: </b>' + str(row["Dose 2 Available Capacity"]) + '\n <b>Vaccine: </b>' + str(row["Vaccine"]) + '\n <b>Fee type: </b>' + str(row["Fees"]) + '\n<b> Amount: </b>'+ str(row["Amount"]) 
            utils.send_reply_text(update,result,'HTML')
   
def do_subscribe(update: Update, context: CallbackContext):
    msg = ''
    if not utils.isSubscribed(context.user_data):
        utils.send_reply_text(update,cfg.SUBSCRIBE_MESSAGE,None)
        utils.print_filters(update,context)
        utils.send_reply_text(update,cfg.SUBSCRIBE_MESSAGE_END,None)
        utils.set_user_data(context,'subscribe','yes')
        schedule.every(59).seconds.do(call_api,update=update,context=context)
    else:
        utils.send_reply_text(update,cfg.ALREADY_SUBSCRIBED,None)
    return CHOOSING
    
def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)
        
def do_unsubscribe(update: Update, context: CallbackContext):
    utils.send_reply_text(update,cfg.SUCCESS_UNSUBSCRIBE_MESSAGE,None)
    utils.send_reply_text(update,cfg.RESP_END_MESSAGE,None)
    utils.set_user_data(context,'subscribe','no')
    schedule.clear()

def print_filters(update: Update, context: CallbackContext):
    utils.send_reply_text(update,'Current filters are :',None) 
    utils.print_filters(update,context)
    utils.send_reply_text(update,cfg.RESP_END_MESSAGE,None)
    
def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    reply_markup=ReplyKeyboardRemove()
    utils.send_reply_text(update,cfg.EXIT_MESSAGE,None)
    user_data.clear()
    schedule.clear()
    utils.set_user_data(context,'previous_response',pd.DataFrame())
    return ConversationHandler.END
        
def invalid_start(update: Update, context: CallbackContext):
    utils.send_reply_text(update,cfg.INVALID_START,None)
    return ConversationHandler.END
        

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(cfg.BOT_TOKEN)
    j = updater.job_queue
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),MessageHandler(Filters.regex('^(start|Start)$'), start),
            MessageHandler(Filters.regex(cfg.EXIT_COMMANDS), done),MessageHandler(Filters.regex('^(?!start|Start).*'), invalid_start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex(cfg.EXIT_COMMANDS), done
                ),
                CommandHandler('start', start
                ),
                CommandHandler('continue', continueChoosing
                ),
                CommandHandler('exit', done
                ),
                CommandHandler('help', need_help
                ),
                CommandHandler('subscribe', do_subscribe
                ),
                CommandHandler('unsubscribe', do_unsubscribe
                ),
                CommandHandler('repeat', do_repeat
                ),
                CommandHandler('check', print_filters
                )
            ],
            START_CHOOSING:[
                MessageHandler(
                    ( Filters.text | Filters.command ) & ~(Filters.regex(cfg.EXIT_COMMANDS)),
                    get_dist_name,
                )
            ],
            CONT_CHOOSING: [
                MessageHandler(
                    ( Filters.text | Filters.command ) & ~(Filters.regex(cfg.EXIT_COMMANDS)),
                    search_again,
                )
            ],
            DATE_RANGE: [
                MessageHandler(
                    ( Filters.text | Filters.command ) & ~(Filters.regex(cfg.EXIT_COMMANDS)),
                    get_date_range,
                )
            ],
            SKIP_PINCODE: [
                MessageHandler(
                    ( Filters.text | Filters.command ) & ~(Filters.regex(cfg.EXIT_COMMANDS)),
                    skip_pincode,
                )
            ],
            PINCODE: [
                MessageHandler(
                    ( Filters.text | Filters.command ) & ~(Filters.regex(cfg.EXIT_COMMANDS)),
                    get_pincode,
                )
            ],
            MIN_AGE_LIMIT: [
                MessageHandler(
                    ( Filters.text | Filters.command ) & ~(Filters.regex(cfg.EXIT_COMMANDS)),
                    get_min_age_limit,
                )
            ],
            PAYMENT: [
                MessageHandler(
                    ( Filters.text | Filters.command ) & ~(Filters.regex(cfg.EXIT_COMMANDS)),
                    get_payment_type,
                )
            ],
            RESULT: [
                MessageHandler(
                    ( Filters.text | Filters.command ) & ~(Filters.regex(cfg.EXIT_COMMANDS)),
                    get_result,
                )
            ],
            CHANGE_FILTER: [
                MessageHandler(
                    ( Filters.text | Filters.command ) & ~(Filters.regex(cfg.EXIT_COMMANDS)),
                    change_filter,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.text, done)],
        per_user=True,
        per_chat=True
    )

    dispatcher.add_handler(conv_handler)
    
    # Spin up a thread to run the schedule check so it doesn't block your bot.
    # This will take the function schedule_checker which will check every second
    # to see if the scheduled job needs to be ran.
    Thread(target=schedule_checker).start() 
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
