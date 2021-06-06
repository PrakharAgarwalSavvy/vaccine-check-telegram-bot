import datetime
import json
import numpy as np
import requests
import pandas as pd
import config as cfg
import utils
from copy import deepcopy
from typing import Dict
    
def get_availability(answers: Dict[str, str],update):
   utils.do_logging('get_availability',update.update_id,update.message.message_id,update.message.chat_id, answers)
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
               if final_df is None:
                  final_df = pd.DataFrame()
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
                      if ("vaccine_fees" in df):
                          df['fee_amount'] = df.apply(lambda x: utils.get_vaccine_amount(x['vaccine_fees'],x['vaccine']), axis=1)
                      else:
                          raise Exception('Vaccine Fees column is not present.')
                   except Exception as e:
                      df['fee_amount'] = np.where(df.fee_type == 'Free',
                              dict({"fee": '0'}),
                              dict({"fee": 'unknown'}))
                      df['fee_amount'] = df.fee_amount.apply(lambda x: x.get('fee'))
                      utils.do_logging('get_availability',update.update_id,update.message.message_id,update.message.chat_id, 'No vaccine_fees column in dataframe')
                   df = df[["date", "available_capacity", "vaccine", "min_age_limit", "pincode", "name", "address","state_name", "district_name", "block_name", "fee_type","fee_amount","available_capacity_dose1","available_capacity_dose2"]]
                   if not final_df.empty:
                       final_df = pd.concat([final_df, df])
                   else:
                       final_df = deepcopy(df)                        
   if final_df is None:
      utils.do_logging('get_availability ',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'final_df is none'}))
      reset_df = utils.create_error_message_df(cfg.TECHNICAL_ERROR_MESSAGE,'')
   elif(final_df.empty):    
      utils.do_logging('get_availability ',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'final_df is empty'}))
      reset_df = utils.create_error_message_df(cfg.NO_CENTER_MESSAGE,'')
   else:       
      utils.do_logging('get_availability ',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'final_df send to filter'}))
      reset_df = filter(final_df,answers,date_str,update)
   return reset_df

def filter(final_df,answers,date_str,update):
    message=''
    if (not final_df.empty) and (len(final_df)):
    
        final_df.drop_duplicates(inplace=True)
            
        final_df.sort_values(by = ['date','pincode','name','address','available_capacity'], axis=0, ascending=[True,True,True,True,False], inplace=True,
                na_position='first', ignore_index=True)
            
        final_df.drop_duplicates(
            subset = ['date', 'vaccine','min_age_limit','pincode','name','address','state_name','district_name','block_name','fee_type','fee_amount'],
            keep = 'first',inplace=True)

        final_df.rename(columns=cfg.RENAME_MAPPING, inplace=True)
        new_df= None
        
        utils.do_logging('filter',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'availability filter start'}))
        final_df = utils.filter_capacity(final_df, "Available Capacity", 0)
        isEmpty = utils.check_empty_df(final_df)
        if bool(isEmpty):
            return utils.create_error_message_df(cfg.NO_VACCINE_MESSAGE,'')

        utils.do_logging('filter',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'date filter start'}))
        date_range_str = answers.get('date_range')
        for date_inp in date_str: 
            date_df = utils.filter_column(final_df, "Date", date_inp)
            new_df = pd.concat([new_df, date_df])
        final_df = deepcopy(new_df) 
        isEmpty = utils.check_empty_df(final_df) 
        if bool(isEmpty):
            message = f'No Vaccination centers are available for booking in next {date_range_str} day/days'
            return utils.create_error_message_df(message,'')
        
        utils.do_logging('filter',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'pincode filter start'}))
        valid_pincodes = list(np.unique(final_df["Pincode"].values))
        pincode_inp_str=answers.get('pincode')
        pincode_inp= int(pincode_inp_str)
        if (pincode_inp in valid_pincodes):
            final_df = utils.filter_column(final_df, 'Pincode', pincode_inp)
            isEmpty = utils.check_empty_df(final_df)
            if bool(isEmpty):
                return utils.create_error_message_df(cfg.NO_VACCINE_PINCODE_MESSAGE,pincode_inp_str)
        elif(pincode_inp == 000000 ):
            utils.do_logging('filter',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'only district choosen'}))
        else:
            return utils.create_error_message_df(cfg.NO_VACCINE_PINCODE_MESSAGE,pincode_inp_str)
        utils.do_logging('filter',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'min age filter start'}))
        age_inp = int(answers.get('age_limit'))
        final_df = utils.filter_column(final_df, "Minimum Age Limit", age_inp)
        isEmpty = utils.check_empty_df(final_df)
        if bool(isEmpty):
           if(pincode_inp == 000000):
              message = 'No slots are available for '+str(age_inp) +'+ age group.'
           else:
              message = 'No slots are available for '+str(age_inp) + '+ age group in pincode ' + str(pincode_inp)
           return utils.create_error_message_df(message,'')  
        
        utils.do_logging('filter',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'payment filter start'}))        
        pay_inp= answers.get('payment')
        if pay_inp != "Both":
            final_df = utils.filter_column(final_df, "Fees", pay_inp)
            isEmpty = utils.check_empty_df(final_df)
            if bool(isEmpty):
                message = pay_inp + ' vaccines are not available for '+str(age_inp) + '+ age group' + ' in ' + str(pincode_inp)
                return utils.create_error_message_df(message,'')
        
        distinct_vaccine = final_df.Vaccine.unique().tolist()
        utils.do_logging('filter',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'vaccine type filter start'}))        
        vaccine_type= answers.get('vaccine_type')
        if (vaccine_type): 
            if (vaccine_type in distinct_vaccine):
                final_df = utils.filter_column(final_df, "Vaccine", vaccine_type)
                isEmpty = utils.check_empty_df(final_df)
                if bool(isEmpty):
                    message = vaccine_type + 'vaccine are not available for chosen filters.'
                    return utils.create_error_message_df(message,'')
            else:
                message = vaccine_type + ' vaccines are not available in any center for chosen filters.'
                return utils.create_error_message_df(message,'')
        
        utils.do_logging('filter',update.update_id,update.message.message_id,update.message.chat_id, dict({"message":'specific dose filter start'}))
        dose_avail= answers.get('dose_avail')
        if(dose_avail):
            if(dose_avail == '1'):
                final_df = utils.filter_capacity(final_df, "Dose 1 Available Capacity", 0)
            else:
                final_df = utils.filter_capacity(final_df, "Dose 2 Available Capacity", 0)
            isEmpty = utils.check_empty_df(final_df)
            if bool(isEmpty):
                return utils.create_error_message_df('Dose ' + dose_avail + ' vaccines are not availabile','')
                  

        reset_df = deepcopy(final_df)
        reset_df.reset_index(inplace=True, drop=True)
        
    else:
        reset_df = pd.DataFrame([[cfg.TECHNICAL_ERROR_MESSAGE]], columns = ['message'])
    return reset_df;
