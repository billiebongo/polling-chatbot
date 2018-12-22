
import telepot
from updated
import telepot.helper
import gspread
from telepot.delegate import (
    per_chat_id, per_inline_from_id, per_callback_query_origin, create_open, pave_event_space, include_callback_query_chat_id)
from pollbot_utils import *

from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from oauth2client.service_account import ServiceAccountCredentials

errorMsg="""Hi, something went wrong and i'm stuck! Reboot me with /start. Do remember to put a / at the start of your commands. """  
global errorMsg

jsonfile=input("Input the location of your JSON file: eg '/Users/Yourself/Desktop/JSON Authentication Keyfile' Please do not include'' ") 
TOKEN=input("Input your Bot's Token. Please do not include semicolons") 
channel=int(input("Input the ID of your channel. eg -1001065895481")) 
botname=input("Input your bots name.")

#2BD: work on asynchro, use inconsistent variable names, address more dumb user edge cases, huge functions that might die lel


credentials = ServiceAccountCredentials.from_json_keyfile_name( jsonfile, 'https://spreadsheets.google.com/feeds')
gc = gspread.authorize(credentials)
wks = gc.open("Yay or Nay datasheet").sheet1

global credentials
global gc
global wks
#note that query and quiz are used interchangeably coz legacy issues lel


class YayOrNay(telepot.helper.ChatHandler):

    def __init__(self, *args, **kwargs):
        super(YayOrNay, self).__init__(*args, **kwargs)
        self.quizzes_done = []   #one list is created per user. It's much faster.


    def on_chat_message(self, msg):

        content_type, chat_type, chat_id = telepot.glance(msg)
        onchat_object=updated_gspread() ##create the object that references from the updated_gspread() class
        print('User: ', msg['chat']['first_name'], chat_id)
        print(content_type) ## print what type of input it is
        if content_type=='text': # if the input is text
            command = msg['text'].lower() ## assign the input of user to the variable, command
        else:
            command='zzz' #command is a photo
        quiz_id = ''

        if command == '/': ##edge case where user may misclick the '/'
            bot.sendMessage(chat_id, 'Please send me the command in proper format. Type /start for the list of instructions!') ##send error message

        if command=='/start': ##Gives instructions to users.
            bot.sendMessage(chat_id, 'Welcome to Yay or Nay! \n\nClick /createquery to create a new query \nClick /viewresponses to view the query results \nClick /start to refresh bot') #sends the instructions to the user
            quiz_str = '' ## empty the string of quiz
            current_quiz_list=(onchat_object.return_list_of_quizzes()) ## retrieves list of all quizzes in gspread
            bot.sendMessage(chat_id, 'Here are the 10 recent queries.') ## sends the user a list of recent queries
            for quiz in current_quiz_list:
                if quiz != 'qns_id' and quiz != '': ## '' and 'qns_id' are in the gspread column, omit the first 2 value of the column which are the headers
                    quiz_str=quiz_str+"/query"+quiz+"\n"
            bot.sendMessage(chat_id, quiz_str)
        if command=='/viewresponses':
            bot.sendMessage(chat_id, "Please wait while I retrieve your queries.")
            createdquizzes=onchat_object.retrieve_quizzes_i_created(chat_id)
            #print(createdquizzes)
            quiz_str='Click to view responses'
            for quiz in createdquizzes:
                quiz_str=quiz_str+"\n"+" /responses"+quiz
            bot.sendMessage(chat_id, quiz_str)

        if command== '/createquery':  #gives instructions to user
            bot.sendMessage(chat_id, "Key in your question in this format q: <your question>")

        if command[:2]=='q:':
            qns=command[2:]
            if qns == ' ':
                bot.sendMessage(chat_id, 'Error. Please send me the query in this format, q: <your query>')
            else:
                bot.sendMessage(chat_id, 'Creating new query, please wait...')
                new_quiz_id=onchat_object.add_new_quiz(qns, chat_id)
                print("New query created: ", new_quiz_id)
                bot.sendMessage(chat_id, "Your query has been created! To view responses, click /responses"+new_quiz_id+" or type /response<your quiz id>"+ "If you would like to add a photo to your query, click /addphoto"+ new_quiz_id)
                bot.sendMessage(channel, "NEW QUERY: /query"+new_quiz_id+ '\n\nThe new query created is: ' +qns+" .Click @"+botname )
### this ensures there wont be 2 queries created wih same ID
        elif command[:10] == '/responses': #user requesting for query results
            quiz_id=command[10:13] #the quiz_id
            response=onchat_object.retrieve_quiz_responses(quiz_id, chat_id) 
            try:
                if response is not False:
                    print(response)
                    bot.sendMessage(chat_id, "Total Responses: "+ str(response[0]))
                    bot.sendMessage(chat_id, "Yays: "+ str(response[1])[:4] + "%")
                    bot.sendMessage(chat_id, "Nays: "+ str(response[2])[:4] + "%") 
                    for i in range(len(response)-3):
                        n=i+3
                        bot.sendMessage(chat_id, "Feedback: "+ response[n] ) ## prints every feedback by
                else:
                    bot.sendMessage(chat_id, "Access Denied") ## user is not the creator of query, ACCESS DENIED
            except ValueError:  ##when there are no response from users yet
                bot.sendMessage(chat_id, "There is no response from the users yet. Try again later.") ##error message
            except IndexError:
                bot.sendMessage(chat_id, "______") #2bd

        if command[:6]=='/query':
            quizno=command[6:]
            if quizno != '':
                myQns=onchat_object.retrieve_quiz_qns(quizno)
                cb_id_yay=quizno+'yay' 
                cb_id_nay=quizno+'nay' 
                markup = InlineKeyboardMarkup(inline_keyboard=[ ## describes the inline keyboard for users to indicate 'YAY' or 'NAY'
                                 [dict(text='YAY', callback_data=cb_id_yay)], ## INLINE KEYBOARD: YAY OR NAY
                                 [dict(text='NAY', callback_data=cb_id_nay)],
                             ])
                global markup ## declare the variable global so that it can be referenced later in the callback function
                global message_with_inline_keyboard ## declare the variable global so that it can be referenced later in the callback function
                if "__PHOTO__" in myQns: ##check if a photo is attached to the query
                    qns_with_photo=myQns.split("__PHOTO__")
                    myQns=qns_with_photo[0]
                    from_chat_id=qns_with_photo[1]
                    message_id=qns_with_photo[2]

                    bot.forwardMessage(chat_id, from_chat_id, message_id, disable_notification=None)

                message_with_inline_keyboard = bot.sendMessage(chat_id, myQns, reply_markup=markup)

            elif quizno is not onchat_object.return_list_of_quizzes():  ##in case user type in quiz id that doesnt exist in the spreadsheet
                bot.sendMessage(chat_id, "Hi, please specify the query id e.g /query231 ")
            else:
                bot.sendMessage(chat_id, "Hi, please specify the query id e.g /query231 ")
        if command[:9]=="/addphoto":
            tag=command[9:12]+"photo"
            self.quizzes_done.append(tag)
            #print(self.quizzes_done)
            bot.sendMessage(chat_id, "Please send only one photo.")
        if content_type=='photo':

            if self.quizzes_done[-1][-5:]=='photo':
                quizno=self.quizzes_done[-1][-8:]
                quizno=quizno[:3] #assigns quizno to the quiz id which will have photo attached
                for wcell in wks.range('A2:A100'):
                    if wcell.value==quizno:
                        row=wcell.row
                        qns=str(wks.cell(wcell.row, 3).value) #retrieves qns as string for that quiz_id
                        msg_id=msg['message_id']
                        qns=qns+"__PHOTO__"+str(chat_id)+"__PHOTO__"+str(msg_id) #attaching message id of forwarded photo to the question
                        #print(qns) #testing purposes /acheckpoint
                        break
                self.quizzes_done.append("added")
                wks.update_cell(row, 3, qns)
                bot.sendMessage(chat_id, "Your photo has been added to query"+quizno+" ! Click /start to respond to a query or create another one!")
            else:
                bot.sendMessage(chat_id, "Sorry! Only one photo per query!")

        if command[:4]=='elab':
            try:
                quizno=self.quizzes_done[-1] 
                print("User is elaborating for "+quizno)
                elab=command[4:]
                onchat_object.add_elab(quizno, elab)
                bot.sendMessage(chat_id,"Your feedback has been recorded! Thank you!")
            except IndexError:
                bot.sendMessage(chat_id, 'YAY or NAY? Make a choice before elaborating!')
        if command== '/start' or command=='/createquery' or command[:2]=='q:'or  command[:10] == '/responses' or command[:6]=='/query' or command[:9]=="/addphoto" or content_type=='photo' or command[:4]=='elab' or command=='/viewresponses':
            return None
        else:
            bot.sendMessage(chat_id, errorMsg)



    def on_callback_query(self, msg): ##query data
        """find out which quiz the person last did. per_chat_id stores the quizzes the person last did"""
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Response:', query_id, from_id, query_data)
        oncallbackobject=updated_gspread() 
        quizno=query_data[:3] ##assign the first 3 characters of query_data which represents the query id that the user did to variable quizno
        if quizno not in self.quizzes_done:
            data=query_data[-3:]
            oncallbackobject.add_count(quizno,data)
            bot.answerCallbackQuery(query_id, text='You chose ' + query_data[-3:].upper() + '!', show_alert=True)
            bot.sendMessage(from_id, "Thank you for your response! \n\nType 'elab <your feedback> 'to provide feedback. It's anonymous! Click /start to answer another query!")
            self.quizzes_done.append(quizno) ## adds this query id to the list of queries that is done by the user
        else:
            bot.sendMessage(from_id, "You have already done this query. Click /start to select another query") # checks if the user did this query before, prompt user to do another query



bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['private']), create_open, YayOrNay, timeout=999999999999),
])
print('Listening to responses...')

bot.message_loop(run_forever='Listening ...')