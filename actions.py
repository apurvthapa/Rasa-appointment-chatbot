import pandas as pd
import datetime
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionUpdateCSV(Action):
    def name(self) -> Text:
        return "action_update_csv"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        raw_date = tracker.get_slot('date')
        raw_name = tracker.get_slot('name')
        raw_time = tracker.get_slot('time')
        df = pd.read_csv(r'C:\Users\apurv\OneDrive\Desktop\appointment\data.csv')

        def time_format(t):
            formats = ['%H:%M', '%I:%M %p', '%I%p', '%I %p']
            for f in formats:
                try:
                    time_1 = datetime.datetime.strptime(t, f)
                    time_1 = time_1.strftime('%H:%M')
                    return time_1
                except ValueError:
                    pass
            dispatcher.utter_message("Invalid time format. Please enter time in hh:mm AM/PM format or hh AM/PM format.")
            return None
        
        format_codes = ['%d/%m/%y', '%d/%m/%Y', '%d %b %Y', '%d-%m-%y', '%d %B %Y', '%B %d, %Y', '%b %d, %Y', '%B %d %Y', '%d-%m-%Y']
        date_obj=None
        
        for code in format_codes:
            try:
                date_obj = datetime.datetime.strptime(raw_date, code)
                break
            except ValueError:
                continue
    
        if not date_obj:
            m1=f'Invalid date format: {raw_date}'
            dispatcher.utter_message(m1)
            return None
    
        if date_obj.date() < datetime.date.today():
            m2=f'Date {date_obj.strftime("%d-%m-%Y")} is in the past'
            dispatcher.utter_message(m2)
            return None
    
        day = date_obj.strftime('%A')
        formatted_date = date_obj.strftime('%d-%m-%Y')
        time=time_format(raw_time)
        name=(raw_name.lower()).title()
        
        if len(df[(df['date']==formatted_date) & (df['time']==time)]) == 0:
            message = f"An appointment for {name} on {formatted_date}({day}) at {time}hr has been scheduled."
            dispatcher.utter_message(message)
            new_row = {'name': name, 'date': pd.to_datetime(formatted_date, format='%d-%m-%Y'), 'time': time}
            df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
        else:
            message=(f"Data with Date: {formatted_date} and Time: {time}hrs already exists in the DataFrame.")
            dispatcher.utter_message(message)

        
        
        df = df.sort_values(['date', 'time'])
        df.to_csv(r'C:\Users\apurv\OneDrive\Desktop\appointment\data.csv', index=False)

        return []
