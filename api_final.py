import logging
import datetime
import json
import numpy as np
import requests
import pandas as pd
import config as cfg
import utils
from copy import deepcopy
from typing import Dict


logging.basicConfig(filename='logs/api_logger.txt',
                            filemode='w',
                            format='%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
logger = logging.getLogger("API_FINAL")
    
def get_availability(answers: Dict[str, str]):
   logger.debug(f'{answers} -> user_input.')
   DIST_ID = answers.get('dist_id')
   base = datetime.datetime.today()
   date_list = [base + datetime.timedelta(days=x) for x in range(int(answers.get('date_range')))]
   date_str = [x.strftime("%d-%m-%Y") for x in date_list]
   final_df = None
   for INP_DATE in date_str:
       URL = cfg.URL.format(DIST_ID, INP_DATE)
       headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
       response = requests.get(URL,headers=headers)
       if (response.ok) and ('centers' in json.loads(response.text)):
           resp_json = json.loads(response.text)['centers']
           if resp_json is not None: 
               df = pd.DataFrame(resp_json)
               if len(df):
                   df = df.explode("sessions")
                   df['min_age_limit'] = df.sessions.apply(lambda x: x['min_age_limit'])
                   df['vaccine'] = df.sessions.apply(lambda x: x['vaccine'])
                   df['available_capacity'] = df.sessions.apply(lambda x: x['available_capacity'])
                   df['available_capacity_dose1'] = df.sessions.apply(lambda x: x['available_capacity_dose1'])
                   df['available_capacity_dose2'] = df.sessions.apply(lambda x: x['available_capacity_dose2'])
                   df['date'] = df.sessions.apply(lambda x: x['date'])
                   try:
                      df = df.explode("vaccine_fees") 
                      df['vaccine_fees'] = np.where((df.vaccine_fees.isnull()) & (df.fee_type == 'Free'),
                              dict({"fee": '0'}),
                              df.vaccine_fees)  
                      df['fee_amount'] = df.vaccine_fees.apply(lambda x: x.get('fee'))
                   except:
                      df['fee_amount'] = 'Unknown'
                      logger.debug('No vaccine_fees column in dataframe')
                   df = df[["date", "available_capacity", "vaccine", "min_age_limit", "pincode", "name", "state_name", "district_name", "block_name", "fee_type","fee_amount","available_capacity_dose1","available_capacity_dose2"]]
                   if final_df is not None:
                       final_df = pd.concat([final_df, df])
                   else:
                       final_df = deepcopy(df)                  
               else:
                   return utils.create_error_message_df(cfg.NO_CENTER_MESSAGE,'',final_df)

   reset_df = filter(final_df,answers,date_str)
   return reset_df

def filter(final_df,answers,date_str):
    message=''
    if (final_df is not None) and (len(final_df)):
        final_df.drop_duplicates(inplace=True)
        final_df.rename(columns=cfg.RENAME_MAPPING, inplace=True)
        new_df= None
        logger.debug('date filter start')
        date_range_str = answers.get('date_range')
        for date_inp in date_str: 
            date_df = utils.filter_column(final_df, "Date", date_inp)
            new_df = pd.concat([new_df, date_df])
        final_df = deepcopy(new_df) 
        isEmpty = utils.check_empty_df(final_df) 
        if bool(isEmpty):
            message = f'No Vaccination centers are available for booking in next {date_range_str} day/days'
            return utils.create_error_message_df(message,'',final_df)
        logger.debug('pincode filter start')
        valid_pincodes = list(np.unique(final_df["Pincode"].values))
        pincode_inp_str=answers.get('pincode')
        pincode_inp= int(pincode_inp_str)
        if (pincode_inp in valid_pincodes):
            final_df = utils.filter_column(final_df, 'Pincode', pincode_inp)
            isEmpty = utils.check_empty_df(final_df)
            if bool(isEmpty):
                return utils.create_error_message_df(cfg.NO_VACCINE_PINCODE_MESSAGE,pincode_inp_str,final_df)
        else:
            return utils.create_error_message_df(cfg.NO_VACCINE_PINCODE_MESSAGE,pincode_inp_str,final_df)
        logger.debug('min age filter start')
        age_inp = int(answers.get('age_limit'))
        final_df = utils.filter_column(final_df, "Minimum Age Limit", age_inp)
        isEmpty = utils.check_empty_df(final_df)
        if bool(isEmpty):
           message = 'No slots open for Age above '+str(age_inp) + ' ' + ' in pincode ' + str(pincode_inp)
           return utils.create_error_message_df(message,'',final_df)
        logger.debug('payment filter start')    
        pay_inp= answers.get('payment')
        if pay_inp != "Both":
            final_df = utils.filter_column(final_df, "Fees", pay_inp)
            isEmpty = utils.check_empty_df(final_df)
            if bool(isEmpty):
                message = pay_inp + ' vaccines are not available for '+str(age_inp) + '+ age group' + ' in ' + str(pincode_inp)
                return utils.create_error_message_df(message,'',final_df)
        logger.debug('availability filter start') 
        final_df = utils.filter_capacity(final_df, "Available Capacity", 0)
        isEmpty = utils.check_empty_df(final_df)
        if bool(isEmpty):
            logging.debug(cfg.DATAFRAME_EMPTY_MESSAGE)
            return utils.create_error_message_df(cfg.NO_VACCINE_MESSAGE,'',final_df)

        reset_df = deepcopy(final_df)
        reset_df.reset_index(inplace=True, drop=True)
        
    else:
        reset_df = pd.DataFrame([[cfg.TECHNICAL_ERROR_MESSAGE]], columns = ['message'])
    return reset_df;
       
        