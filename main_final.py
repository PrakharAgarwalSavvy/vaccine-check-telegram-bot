import logging
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


# Enable logging
logging.basicConfig(filename='logs/main_logger.txt',
                            filemode='w',
                            format='%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logger = logging.getLogger(__name__)


CHOOSING, DATE_RANGE, PINCODE, MIN_AGE_LIMIT, PAYMENT, RESULT, CHANGE_FILTER,UNSUBSCRIBE, CONT_CHOOSING = range(9)

mapping_df = utils.load_mapping()

mapping_dict = pd.Series(mapping_df["district id"].to_list(),
                         map(lambda x:x.lower(),mapping_df["district name"].to_list())).to_dict()

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
    context.user_data['previous_response'] = pd.DataFrame()
    if(int(text) in range(1,7)):
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
            return need_help(update,context)
        if (text == '6'):
            return done(update,context)
    else:
        
        message = cfg.INVALID_CONT_MESSAGE + cfg.CONT_MESSAGE                  
        utils.send_reply_text(update,message,None)
    return CHOOSING
    
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
                if( call_api(update,context.user_data)):
                    del user_data[updated_filter_key]
                    return CHOOSING 
                else:
                    del user_data[updated_filter_key]
                    return ConversationHandler.END
            else:
                raise Exception(cfg.invalid_date_range_message)
        except Exception as e :
            logger.error("change_filter date_range -> ", e)
            utils.send_reply_text(update,cfg.invalid_date_range_message,None)
            return CHANGE_FILTER
    if(new_filter_name == 'pincode'):
        try:
            if (utils.pincode_validation(text)):
                utils.set_user_data(context,new_filter_name,text)
                if( call_api(update,context.user_data)):
                    del user_data[updated_filter_key]
                    return CHOOSING 
                else:
                    del user_data[updated_filter_key]
                    return ConversationHandler.END
            else:
                raise Exception(cfg.INVALID_PINCODE_MESSAGE)
        except Exception as e:
            logger.error("change_filter pincode -> ", e)
            utils.send_reply_text(update,cfg.INVALID_PINCODE_MESSAGE,None)            
            return CHANGE_FILTER
            
    if(new_filter_name == 'age_limit'):
        try:
            if (utils.age_group_validation(text)):
                utils.set_user_data(context,new_filter_name,text)
                if( call_api(update,context.user_data)):
                    del user_data[updated_filter_key]
                    return CHOOSING 
                else:
                    del user_data[updated_filter_key]
                    return ConversationHandler.END
            else:
                raise Exception(cfg.INVALID_AGE_GROUP_MESSAGE)
        except Exception as e:
            logger.error("change_filter age_limit -> ", e)
            utils.send_reply_text(update,cfg.INVALID_AGE_GROUP_MESSAGE,None)
            
            return CHANGE_FILTER
            
    if(new_filter_name == 'payment'):
        try:
            if (utils.payment_validation(text)):
                text = text[0].upper() + text[1:]
                utils.set_user_data(context,new_filter_name,text)
                if( call_api(update,context.user_data)):
                    del user_data[updated_filter_key]
                    return CHOOSING 
                else:
                    del user_data[updated_filter_key]
                    return ConversationHandler.END
            else:
                raise Exception(cfg.INVALID_PAYMENT_MESSAGE)
        except Exception as e:
            logger.error("change_filter payment -> ", e)
            utils.send_reply_text(update,cfg.INVALID_PAYMENT_MESSAGE,None)           
            return CHANGE_FILTER

def get_dist_name(update: Update, context: CallbackContext) -> int:
    utils.send_reply_text(update,cfg.DISTRICT_NAME_MESSAGE,None)
    context.user_data['previous_response'] = pd.DataFrame()
    return DATE_RANGE

def get_date_range(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        DIST_ID = mapping_dict[text.lower()]
        utils.set_user_data(context,'dist_id',DIST_ID)
        utils.send_reply_text(update,cfg.DATE_RANGE_MESSAGE,None)
        return PINCODE
    except Exception as e:
        logger.error("get_date_range -> ", e)
        utils.send_reply_text(update,cfg.INVALID_DISTRICT_NAME_MESSAGE,None)
        return DATE_RANGE
         
def get_pincode(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        if (utils.date_range_validation(text)):
            utils.set_user_data(context,'date_range',text)
            utils.send_reply_text(update,cfg.PINCODE_MESSAGE,None)
            return MIN_AGE_LIMIT
        else:
            raise Exception(cfg.INVALID_DATE_RANGE_MESSAGE)
    except Exception as e:
        logger.error("get_pincode -> ", e)
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
        logger.error("get_min_age_limit -> ", e)
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
        logger.error("get_payment_type -> ", e)
        utils.send_reply_text(update,cfg.INVALID_AGE_GROUP_MESSAGE,None)
        return PAYMENT

def get_result(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if (utils.payment_validation(text)):
        text = text[0].upper() + text[1:]
        utils.set_user_data(context,'payment',text)
        if( call_api(update,context.user_data)):
            return CHOOSING
        else:     
            return ConversationHandler.END
    else:
        utils.send_reply_text(update,cfg.INVALID_PAYMENT_MESSAGE,None)
        return RESULT
        
def call_api(update: Update, user_data) -> int:
    logger.debug('call_api -> user_data for chat_id {} {}'.format(update.message.chat_id,user_data))
    try:
        final_df=api.get_availability(user_data)
        final_df_previous_response = user_data['previous_response']
        if(final_df_previous_response.empty):
            logger.debug("First Response call for chat_id  {}".format(update.message.chat_id))
            serialize_ex(final_df,update)
            return print_after_serialize_ex(update,user_data,final_df)
        else:
            compared_df = final_df.compare(final_df_previous_response)
            if not compared_df.empty:
               logger.debug("second onwards Response call for chat_id  {}".format(update.message.chat_id))
               # there is change show the response
               serialize_ex(final_df,update)
               return print_after_serialize_ex(update,user_data,final_df)
    except ValueError as ve:
        #this is a change show the response
        logger.error("call_api -> ", ve)
        serialize_ex(final_df,update)
        return print_after_serialize_ex(update,user_data,final_df)
    except Exception as e:
        utils.send_reply_text(update,cfg.TECHNICAL_ERROR_MESSAGE,'HTML')
        logger.error("call_api -> ", e)
        return False

def print_after_serialize_ex(update,user_data,final_df):
        isSubscribe= user_data.get('subscribe')
        if(isSubscribe == None or isSubscribe != 'yes'):
            utils.send_reply_text(update,cfg.RESP_END_MESSAGE,None)
        else:
            utils.send_reply_text(update,cfg.UNSUBSCRIBE_MESSAGE,None)        
        user_data['previous_response'] = final_df  
        return True
    
def serialize_ex(df,update):
    for index, row in df.iterrows():
        if ('message' in df.columns):
            result = '<b>' + str(row["message"])+ '</b>\n\n'
            utils.send_reply_text(update,result,'HTML')  
        else:
            if(row["Fees"] == 'Free'):
                result = '<b>[' +str(row["Pincode"])+ ']</b>'+ '\n <b>Age group: </b>' + str(row["Minimum Age Limit"]) +'\n <b>Hospital Name: </b>' + str(row["Hospital Name"]) + '\n <b>Date: </b>' + str(row["Date"])+ '\n <b>Available Capacity: </b>' + str(row["Available Capacity"]) + '\n <b>Dose 1 Available Capacity: </b>' + str(row["Dose 1 Available Capacity"]) + '\n <b>Dose 2 Available Capacity: </b>' + str(row["Dose 2 Available Capacity"]) + '\n <b>Vaccine: </b>' + str(row["Vaccine"]) + '\n <b>Fee type: </b>' + str(row["Fees"])
            else:
                result = '<b>[' +str(row["Pincode"])+ ']</b>'+ '\n <b>Age group: </b>' + str(row["Minimum Age Limit"]) +'\n <b>Hospital Name: </b>' + str(row["Hospital Name"]) + '\n <b>Date: </b>' + str(row["Date"])+ '\n <b>Available Capacity: </b>' + str(row["Available Capacity"]) + '\n <b>Dose 1 Available Capacity: </b>' + str(row["Dose 1 Available Capacity"]) + '\n <b>Dose 2 Available Capacity: </b>' + str(row["Dose 2 Available Capacity"]) + '\n <b>Vaccine: </b>' + str(row["Vaccine"]) + '\n <b>Fee type: </b>' + str(row["Fees"]) + '\n<b> Amount: </b>'+ str(row["Amount"]) 
            utils.send_reply_text(update,result,'HTML')
   
def do_subscribe(update: Update, context: CallbackContext):
    utils.send_reply_text(update,cfg.SUBSCRIBE_MESSAGE,None)
    context.user_data['subscribe'] = 'yes'
    schedule.every(15).minutes.do(call_api,update=update,user_data=context.user_data)
    return CHOOSING
    
def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)
        
def do_unsubscribe(update: Update, context: CallbackContext):
    utils.send_reply_text(update,cfg.RESP_END_MESSAGE,None)
    context.user_data['subscribe'] = 'no'
    schedule.clear()
    
def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    reply_markup=ReplyKeyboardRemove()
    utils.send_reply_text(update,cfg.EXIT_MESSAGE,None)
    user_data.clear()
    schedule.clear()
    context.user_data['previous_response'] = pd.DataFrame()
    return ConversationHandler.END

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(cfg.BOT_TOKEN)
    j = updater.job_queue
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', get_dist_name),MessageHandler(
                    Filters.regex('^start$'), get_dist_name
                ),CommandHandler('help', need_help)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex(cfg.EXIT_COMMANDS), done
                ),
                CommandHandler('start', get_dist_name
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
                )
            ],
            CONT_CHOOSING: [
                MessageHandler(
                    Filters.regex(cfg.CHOOSING_NUMS_REGEX) & ~(Filters.command | Filters.regex(cfg.EXIT_COMMANDS)),
                    search_again,
                )
            ],
            DATE_RANGE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex(cfg.EXIT_COMMANDS)),
                    get_date_range,
                )
            ],
            PINCODE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex(cfg.EXIT_COMMANDS)),
                    get_pincode,
                )
            ],
            MIN_AGE_LIMIT: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex(cfg.EXIT_COMMANDS)),
                    get_min_age_limit,
                )
            ],
            PAYMENT: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex(cfg.EXIT_COMMANDS)),
                    get_payment_type,
                )
            ],
            RESULT: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex(cfg.EXIT_COMMANDS)),
                    get_result,
                )
            ],
            CHANGE_FILTER: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex(cfg.EXIT_COMMANDS)),
                    change_filter,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex(cfg.EXIT_COMMANDS), done)],
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
