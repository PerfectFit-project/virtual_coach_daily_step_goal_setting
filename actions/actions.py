# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from datetime import datetime
from definitions import (DATABASE_HOST, DATABASE_PASSWORD, 
                         DATABASE_PORT, DATABASE_USER)
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction, SlotSet, ConversationPaused
from typing import Any, Dict, List, Optional, Text

import logging
import mysql.connector


class ActionEndDialog(Action):
    """Action to cleanly terminate the dialog."""
    # ATM this action just calls the default restart action
    # but this can be used to perform actions that might be needed
    # at the end of each dialog
    def name(self):
        return "action_end_dialog"

    async def run(self, dispatcher, tracker, domain):

        return [ConversationPaused()]


class ActionDefaultFallbackEndDialog(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback_end_dialog"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_default")
        dispatcher.utter_message(template="utter_default_close_session")

        # End the dialog, which leads to a restart.
        return [FollowupAction('action_end_dialog')]


def get_latest_bot_utterance(events) -> Optional[Any]:
    """
       Get the latest utterance sent by the VC.
        Args:
            events: the events list, obtained from tracker.events
        Returns:
            The name of the latest utterance
    """
    events_bot = []

    for event in events:
        if event['event'] == 'bot':
            events_bot.append(event)

    if (len(events_bot) != 0
            and 'metadata' in events_bot[-1]
            and 'utter_action' in events_bot[-1]['metadata']):
        last_utterance = events_bot[-1]['metadata']['utter_action']
    else:
        last_utterance = None

    return last_utterance


def check_session_not_done_before(cur, prolific_id, session_num):

    query = ("SELECT * FROM sessiondata WHERE prolific_id = %s and session_num = %s")
    cur.execute(query, [prolific_id, session_num])
    done_before_result = cur.fetchone()

    not_done_before = True

    # user has done the session before
    if done_before_result is not None:
        not_done_before = False

    return not_done_before


class ActionLoadSessionFirst(Action):
    
    def name(self) -> Text:
        return "action_load_session_first"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        prolific_id = tracker.current_state()['sender_id']
        session_loaded = False

        try:
            conn = mysql.connector.connect(
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database='db'
            )
            cur = conn.cursor(buffered=True)
            
            session_loaded = check_session_not_done_before(cur, prolific_id, 1)
        
        except mysql.connector.Error as error:
            logging.info("Error in loading first session: " + str(error))

        finally:
            if conn.is_connected():
                cur.close()
                conn.close()

        return [SlotSet("session_loaded", session_loaded)]


class ActionLoadSessionNotFirst(Action):

    def name(self) -> Text:
        return "action_load_session_not_first"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        prolific_id = tracker.current_state()['sender_id']
        session_num = tracker.get_slot("session_num")

        session_loaded = True
        prev_goal = ""
        previous_activity = ""

        try:
            conn = mysql.connector.connect(
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database='db'
            )
            cur = conn.cursor(buffered=True)

            # check if user has not done this session before
            session_loaded = check_session_not_done_before(cur, prolific_id, 
                                                            session_num)

            if session_loaded:
                # Get goal from previous session
                query = ("SELECT response_value FROM sessiondata WHERE prolific_id = %s and session_num = %s and response_type = %s")
                cur.execute(query, [prolific_id, str(int(session_num) - 1), "goal"])
                res = cur.fetchone()
                
                # Check if the user has completed the previous session
                if res is None:
                    session_loaded = False
                else:
                    prev_goal = res[0]
                    query = ("SELECT response_value FROM sessiondata WHERE prolific_id = %s and session_num = %s and response_type = %s")
                    cur.execute(query, [prolific_id, str(int(session_num) - 1), "prev_activity"])
                    res = cur.fetchone()
                    previous_activity = res[0]

        except mysql.connector.Error as error:
            session_loaded = False
            prev_goal = "0"
            previous_activity = "0"
            logging.info("Error in loading session not first: " + str(error))

        finally:
            if conn.is_connected():
                cur.close()
                conn.close()    

        return [SlotSet("goal_prev_session", prev_goal),
                SlotSet("session_loaded", session_loaded),
                SlotSet("previous_activity_from_db", previous_activity)]


class ActionSaveStateToDB(Action):

    def name(self) -> Text:
        return "action_save_state_to_db"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = mysql.connector.connect(
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database='db'
            )
            cur = conn.cursor(prepared=True)

            prolific_id = tracker.current_state()['sender_id']
            session_num = tracker.get_slot("session_num")

            slots_to_save = ["mood", "rest", "available_time", "self_motivation", "self_efficacy"]
            for slot in slots_to_save:
                save_sessiondata_entry(cur, conn, prolific_id, session_num,
                                       slot, tracker.get_slot(slot),
                                       formatted_date)

        except mysql.connector.Error as error:
            logging.info("Error in saving name to db: " + str(error))

        finally:
            if conn.is_connected():
                cur.close()
                conn.close()

        return []


class ActionSaveGoalToDB(Action):

    def name(self) -> Text:
        return "action_save_goal_to_db"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = mysql.connector.connect(
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database='db'
            )
            cur = conn.cursor(prepared=True)

            prolific_id = tracker.current_state()['sender_id']
            session_num = tracker.get_slot("session_num")

            save_sessiondata_entry(cur, conn, prolific_id, session_num,
                                       "goal", tracker.get_slot("preferred_step_goal_slot"),
                                       formatted_date)

        except mysql.connector.Error as error:
            logging.info("Error in saving name to db: " + str(error))

        finally:
            if conn.is_connected():
                cur.close()
                conn.close()

        return []


class ActionSaveGoalAchievabilityToDB(Action):

    def name(self) -> Text:
        return "action_save_goal_achievability_to_db"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = mysql.connector.connect(
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database='db'
            )
            cur = conn.cursor(prepared=True)

            prolific_id = tracker.current_state()['sender_id']
            session_num = tracker.get_slot("session_num")

            save_sessiondata_entry(cur, conn, prolific_id, session_num,
                                       "goal_achievability", tracker.get_slot("goal_achievability"),
                                       formatted_date)

        except mysql.connector.Error as error:
            logging.info("Error in saving name to db: " + str(error))

        finally:
            if conn.is_connected():
                cur.close()
                conn.close()

        return []


class ActionSavePreviousActivitySession1ToDB(Action):

    def name(self) -> Text:
        return "action_save_previous_activity_session1_to_db"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = mysql.connector.connect(
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database='db'
            )
            cur = conn.cursor(prepared=True)

            prolific_id = tracker.current_state()['sender_id']
            session_num = tracker.get_slot("session_num")

            previous_activity = tracker.get_slot("previous_activity_slot").split(',')
            if len(previous_activity) < 9:
                sum_of_elements = 0
                for steps in previous_activity:
                    sum_of_elements += int(steps)
                mean = sum_of_elements/len(previous_activity)
                for i in range(9 - len(previous_activity)):
                    previous_activity.append(str(mean))
            save_sessiondata_entry(cur, conn, prolific_id, session_num, "prev_activity", previous_activity, formatted_date)

        except mysql.connector.Error as error:
            logging.info("Error in saving name to db: " + str(error))

        finally:
            if conn.is_connected():
                cur.close()
                conn.close()

        return []


class ActionSavePreviousActivityToDB(Action):

    def name(self) -> Text:
        return "action_save_previous_activity_to_db"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = mysql.connector.connect(
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database='db'
            )
            cur = conn.cursor(prepared=True)

            prolific_id = tracker.current_state()['sender_id']
            session_num = tracker.get_slot("session_num")

            previous_activity = tracker.get_slot("previous_activity_from_db").split(',')
            prev_day_activity = tracker.get_slot("previous_activity_not_session1_slot")
            previous_activity.pop(8)
            previous_activity.insert(0, prev_day_activity)
            prev_activity = ""
            for activity in previous_activity:
                prev_activity += activity
            save_sessiondata_entry(cur, conn, prolific_id, session_num, "prev_activity", prev_activity, formatted_date)

        except mysql.connector.Error as error:
            logging.info("Error in saving name to db: " + str(error))

        finally:
            if conn.is_connected():
                cur.close()
                conn.close()

        return []

    
def save_sessiondata_entry(cur, conn, prolific_id, session_num, response_type,
                           response_value, time):
    query = "INSERT INTO sessiondata(prolific_id, session_num, response_type, response_value, time) VALUES(%s, %s, %s, %s, %s)"
    cur.execute(query, [prolific_id, session_num, response_type,
                        response_value, time])
    conn.commit()


class ActionCreateStepGoalOptions(Action):

    def name(self) -> Text:
        return "action_create_step_goal_options"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        step_goal_1 = "4000"
        step_goal_2 = "6000"
        step_goal_3 = "8000"

        return [SlotSet("step_goal_option_1_slot", step_goal_1),
                SlotSet("step_goal_option_2_slot", step_goal_2),
                SlotSet("step_goal_option_3_slot", step_goal_3)]


class ActionIncreaseGoal(Action):

    def name(self) -> Text:
        return "action_increase_goal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        number_of_rejected_proposals = int(tracker.get_slot("number_of_rejected_proposals"))
        option_1 = int(tracker.get_slot("step_goal_option_1_slot"))
        option_2 = int(tracker.get_slot("step_goal_option_2_slot"))
        option_3 = int(tracker.get_slot("step_goal_option_3_slot"))

        if number_of_rejected_proposals < 4:
            option_1 += 200
            option_2 += 200
            option_3 += 200
            number_of_rejected_proposals += 1
            dispatcher.utter_message("But since you said you wanted something higher, I'll increase the step goals a bit!")
            return [SlotSet("step_goal_option_1_slot", str(option_1)),
                    SlotSet("step_goal_option_2_slot", str(option_2)),
                    SlotSet("step_goal_option_3_slot", str(option_3)),
                    SlotSet("number_of_rejected_proposals", str(number_of_rejected_proposals))]
        else:
            dispatcher.utter_message("Unfortunately I cannot change the goals any further. So, you will have to pick one which then becomes your step goal for today.")
            return [SlotSet("final_choice", True)]


class ActionDecreaseGoal(Action):

    def name(self) -> Text:
        return "action_decrease_goal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        number_of_rejected_proposals = int(tracker.get_slot("number_of_rejected_proposals"))
        option_1 = int(tracker.get_slot("step_goal_option_1_slot"))
        option_2 = int(tracker.get_slot("step_goal_option_2_slot"))
        option_3 = int(tracker.get_slot("step_goal_option_3_slot"))

        if number_of_rejected_proposals < 4:
            option_1 -= 200
            option_2 -= 200
            option_3 -= 200
            number_of_rejected_proposals += 1
            dispatcher.utter_message("But since you said you wanted something lower, I'll decrease the step goals a bit!")
            return [SlotSet("step_goal_option_1_slot", str(option_1)),
                    SlotSet("step_goal_option_2_slot", str(option_2)),
                    SlotSet("step_goal_option_3_slot", str(option_3)),
                    SlotSet("number_of_rejected_proposals", str(number_of_rejected_proposals))]
        else:
            dispatcher.utter_message("Unfortunately I cannot change the goals any further. So, you will have to pick one which then becomes your step goal for today.")
            return [SlotSet("final_choice", True)]


class ActionRespondGoalAchievement(Action):

    def name(self) -> Text:
        return "action_respond_goal_achievement"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        previous_step_goal = int(tracker.get_slot("goal_prev_session"))
        previous_activity = int(tracker.get_slot("previous_activity_not_session1_slot"))

        if previous_step_goal <= previous_activity:
            dispatcher.utter_message("That means that you achieved yesterday's goal, congrats! Keep it up!")
        else:
            dispatcher.utter_message("This means that you unfortunately did not achieve the goal we set yesterday. But do not be discouraged, I'm sure you will make it today!")

        return []


class ValidatePreviousActivityForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_previous_activity_form'

    def validate_previous_activity_slot(
            self, value: Text, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        # pylint: disable=unused-argument
        """Validate previous_activity_slot input."""
        last_utterance = get_latest_bot_utterance(tracker.events)

        if last_utterance != 'utter_ask_previous_activity_slot':
            return {"previous_activity_slot": None}

        previous_activity = value.split(",")
        valid_previous_activity = True
        previous_activity_slot = ""
        # Check if there are at least 5 values
        if len(previous_activity) < 5:
            valid_previous_activity = False
        # Check if the values are numbers
        else:
            for i in range (0, min(9, len(previous_activity))):
                if not previous_activity[i].isnumeric():
                    valid_previous_activity = False
                elif i == 0:
                    previous_activity_slot += previous_activity[i]
                else:
                    previous_activity_slot += "," + previous_activity[i]
        
        if not valid_previous_activity:
            dispatcher.utter_message("You didn't provide at least 5 numbers, maybe you forgot one, or your answer isn't formatted correctly, it should be numbers seperated by commas.")
            dispatcher.utter_message(response="utter_example_input_previous_activity")
            return {"previous_activity_slot": None}

        # Use only the first 9 days of previous activity
        return {"previous_activity_slot": previous_activity_slot}


class ValidateProposeStepGoalOptionsForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_propose_step_goal_options_form'

    def validate_preferred_step_goal_slot(
            self, value: Text, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        # pylint: disable=unused-argument
        """Validate preferred_step_goal_slot input."""
        last_utterance = get_latest_bot_utterance(tracker.events)

        if last_utterance != 'utter_ask_preferred_step_goal_slot':
            return {"preferred_step_goal_slot": None}

        valid_preferred_step_goal_option = True
        option_1 = tracker.get_slot("step_goal_option_1_slot")
        option_2 = tracker.get_slot("step_goal_option_2_slot")
        option_3 = tracker.get_slot("step_goal_option_3_slot")
        # Check if the value is one of the proposed step goal options
        if not (value == option_1 or value == option_2 or value == option_3):
            valid_preferred_step_goal_option = False
        
        if not valid_preferred_step_goal_option:
            if tracker.get_slot("final_choice"):
                dispatcher.utter_message("Hmm, that doesn't seem to be one of the choices I gave you. Just pick one of the options by typing it.")
            else:
                dispatcher.utter_message("Hmm, that doesn't seem to be one of the choices I gave you.")
                dispatcher.utter_message("Remember that this doesn't have to be your final goal and that you can change it later! So, just pick one of the options by typing it.")
            return {"preferred_step_goal_slot": None}

        return {"preferred_step_goal_slot": value}


class ValidatePreviousActivityNotSession1Form(FormValidationAction):
    def name(self) -> Text:
        return 'validate_previous_activity_not_session1_form'

    def validate_previous_activity_not_session1_slot(
            self, value: Text, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        # pylint: disable=unused-argument
        """Validate previous_activity_not_session1_slot input."""
        last_utterance = get_latest_bot_utterance(tracker.events)

        if last_utterance != 'utter_ask_previous_activity_not_session1_slot':
            return {"previous_activity_not_session1_slot": None}

        # Check if the response is a number
        if value.isnumeric():
            return {"previous_activity_not_session1_slot": value}
        else:
            dispatcher.utter_message("Your input is not formatted correctly. Please only respond with the number of steps you took yesterday")
            return {"previous_activity_not_session1_slot": None}
