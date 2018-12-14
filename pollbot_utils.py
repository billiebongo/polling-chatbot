
from updated
import gspread
from random import randint
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



class updated_gspread():
    def return_list_of_quizzes(self): ###Returns a list of recent 10 quizzes when message is /start
        all_quizzes = wks.col_values(1)
        all_quizzes[:] = (value for value in all_quizzes if value != "")
        if len(all_quizzes)>10:
            all_quizzes=all_quizzes[-10:] #last 10 items
        return all_quizzes

    def add_new_quiz(self, qns, chat_id):
        all_quizzes = wks.col_values(1) #list of quiz_id are retrieved to ensure quiz with same number is used.
        while True:
            new_quiz_id=randint(100, 999)
            new_quiz_id=str(new_quiz_id)
            if new_quiz_id not in all_quizzes:
                break

        for updatingCell in wks.range('A2:A100'): #Look for next empty cell in quiz_id column
            if updatingCell.value == "": #empty cell will have value ""
                wks.update_cell(updatingCell.row, updatingCell.col, new_quiz_id)
                wks.update_cell(updatingCell.row, 3, qns) #question in the 3rd column
                wks.update_cell(updatingCell.row, 4, 0)
                wks.update_cell(updatingCell.row, 6, 0)
                wks.update_cell(updatingCell.row, 8, 0)
                wks.update_cell(updatingCell.row, 2, int(chat_id)) #Stores the chat_id of the creator
                break
        return new_quiz_id #returns the quiz_id to the command that called this function.

    def add_count(self,quiz_id,data):
        for cell in wks.range('A2:A100'):
            if cell.value == quiz_id:
                thatQnsCell=cell
        if data=='yay':
            noOfYay = int(wks.cell(thatQnsCell.row, int(thatQnsCell.col) + 3).value)
            noOfYay += 1
            wks.update_cell(thatQnsCell.row, int(thatQnsCell.col) + 3, noOfYay)

        if data=='nay':
            noOfNay = int(wks.cell(thatQnsCell.row, int(thatQnsCell.col) + 5).value)
            noOfNay += 1
            wks.update_cell(thatQnsCell.row, int(thatQnsCell.col) + 5, noOfNay)

        totalResponses = int(wks.cell(thatQnsCell.row, 8).value)
        totalResponses += 1
        print("Total number of responses - " + str(totalResponses))
        wks.update_cell(thatQnsCell.row, 8, totalResponses)

    def add_elab(self,quiz_id,add_elab):
        for updatingCell in wks.range('A2:A100'):
            if updatingCell.value == quiz_id:
                print(add_elab)
                elabb=wks.cell(updatingCell.row, 9).value
                elabb=elabb+"***"+add_elab
                wks.update_cell(updatingCell.row, 9, elabb)

    def retrieve_quiz_qns(self, quiz_id): #Returns Qns for quiz_id given
        for updatingCell in wks.range('A2:A100'):
            if updatingCell.value == quiz_id:
                qns=wks.cell(updatingCell.row, int(updatingCell.col) + 2).value
                break
        return qns

    def retrieve_quiz_responses(self, quiz_id, chat_id):
        """Returns results (% Yay, % Nay, Total Responses and all elaboration) as a list """
        signal=0
        for updatingCell in wks.range('A2:A99'): ## Retrieves the column of queries created
            if updatingCell.value == quiz_id:
                creator_id = int(wks.cell(updatingCell.row,2).value)
                signal=1 ## flag thaT there is such quiz_id in the column
                if int(chat_id)==int(creator_id): ## check if the user is the creator of query
                    try:
                        print("creator of /query"+quiz_id+" has requested to view responses.")
                        responses=[]
                        totalResponses=int(wks.cell(updatingCell.row, 8).value)
                        responses.append(totalResponses)
                        PercYay=float(wks.cell(updatingCell.row,5).value)
                        responses.append(PercYay)
                        PercNay=float(wks.cell(updatingCell.row,7).value)
                        responses.append(PercNay)
                        elab=wks.cell(updatingCell.row,9).value
                        elab_list=elab.split("***") ##delimiter ***
                        responses=responses+elab_list
                    except ValueError:
                        bot.sendMessage(chat_id, "There is no response from the users yet. Try again later.")
                    except IndexError:
                        return None
                    return responses ##return the list of responses
                    break
                else:
                    bot.sendMessage(chat_id, "You are not the creator.")  ##tell the user that you are not the creator of the query
                    return False
        if signal==0:   ##there is no such quiz_id in the gspread
                bot.sendMessage(chat_id, "Query does not exist") ##send error message to the user
                return False


    def retrieve_quizzes_i_created(self,chat_id):
        """Retrieves the list of quizzes created by the creator. Verifies if the
        quiz is created by the creator through his/her chat_id """
        createdquizzes=[]
        for updatingCell in wks.range('B2:B99'):
            if updatingCell.value==str(chat_id):
                createdquizzes.append(str(wks.cell(updatingCell.row, 1).value))
        return createdquizzes