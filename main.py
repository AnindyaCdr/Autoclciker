#Importing Libaries
import multiprocessing
import tkinter
from sys import exit
import win32api
import pyautogui as ptg

#I don't know what it does but I got an error and the error told me to use this and I used it
ptg.FAILSAFE = False

#Creating The class
class loops:
    #Getting the required variables
    def __init__(self,que: multiprocessing.Queue, butQue: multiprocessing.Queue,startAgainQue:multiprocessing.Queue,stAgFix:multiprocessing.Queue):

        #que variable for running and stoping the autoclicker
        self.queue = que

        #butQue variable for getting the output when button is pressed
        self.butQue = butQue

        #startAgainQue for sending the startAgain comamnd
        self.startAgainQue=startAgainQue

        #stAgFix to fix the error when the start button is pressed while the process is still on
        self.stAgFix = stAgFix
        
    #This is the autoclicker function
    def loop1(self):


        #going into the actual loop
        while True:

            #I can't figure out how to stop the loop so I used try and except
            try:

                #As in above we got the value from the variable from the queue so this line generates an error
                #So when we want to stop it we just need to put something in that queue and this won't generate an error and we could break out of loop and turn off the autoclciker
                self.istru=self.queue.get_nowait()

                #Just for my preference(You Can also remove it but it helps in error detection)
                print("Stopped")
                break
            except:
                #This tiny code is the real autocliker which clciks
                while win32api.GetKeyState(0x01) == 1:  #This line of code means if user does the action: left mouse button down(One time)
                    ptg.tripleClick(button='left')   #This code clicks three times when user clicks one time
                    exit  #I dont know what it does


                while win32api.GetKeyState(0x0002) == 1: #This line of code means if user does the action: right mouse button down(One time)
                    ptg.tripleClick(button='right')  #This code clicks three times when user clicks one time
                    exit  #I dont know what it does
        exit

    def loop_handler(self):
        #All the logics are handled by this process

        #This variable checks for if the start button has been ever pressed during the whole time
        self.isOn=False   #If pressed it would change to True

        #This variable checks if after running the stop button has once pressed or not
        self.isOff=False  #If pressed it would change to True
        #The loop which is constantly checking for commands and doing as given

        while True:

            #Waiting for tkinter app to put some command in the butQue queue
            
            self.switch = self.butQue.get()

            #off is send when the stop button is pressed 
            if self.switch =="off":

                #isAlive command is send to the manin code to get the state of the process(Either on for True or off for False)
                self.startAgainQue.put('isAlive')

                #waiting for the response
                self.isAlive: bool = self.stAgFix.get()
                
                #If the autoclicker is on is alive would be on
                if self.isAlive==True:

                    #If the stop button has not been pressed after pressing start once then this would execute
                    if self.isOff==False:
                        #This code gives some thing the autoclicker's queue to stop it
                        self.queue.put_nowait('off')
                        
                        #Chaning the variable to True because it has been pressed
                        self.isOff=True

                    #If the autoclcikler is off already then this code will execute
                    elif self.isOff==True: #<-- This is for some rare cases when we sent two off in the autoclicker and to start it again we need to clcik twice ,So, to stop that from happening this code is needed
                        continue
                #If the autoclcikler is off already then this code will execute        
                elif self.isAlive==False:
                    continue

            
            #If any one clicks the start button this will execute
            elif self.switch =='on':

                #We are setting the variable which contains that if after stopping 
                self.isOff=False

                #This condition doesn't does anything it used to earlier but still I kept it as it does no error
                if self.isOn ==True:

                    #This command is sent to the function in our main pogram which handles every processes
                    self.startAgainQue.put('startAgain')

                    #Just a confirmation statement that the work has been done
                    self.isAlive:bool = self.stAgFix.get()
                    continue


            #'totalOff' is on;ly sent by app if it closes comepletly
            elif self.switch=='totalOff':

                #This condition doesn't does anything it used to earlier but still I kept it as it does no error
                if self.isOn==True:

                    #If the autoclickler is already off then sending any message would not cause anything if it is on sending the message would stop it
                    self.queue.put_nowait('off')
                    #This command is sent to the function of main code to tell it to break out of its loop and exit the code

                    self.startAgainQue.put('totalStop')
                    #Then we are breaking out of the loop 
                    break

            #'start' is sent by the app when it has runned fully and is shown to the user
            elif self.switch=='start':
                #This line stops the autoclicker which is running  <-- Yes until the gui prompts the autoclickler is running in background
                #This is a loop hole   <-- You can fix it by writing 'butQue.put('start')' line in the main code and removing 'self.butQue.put('start')' line from the tkinter function
                self.queue.put_nowait('off')

                #Making the condition true that was used earlier but now does nothing but still I kept it as it does no error
                self.isOn=True


    def loop2(self):
        #This is the visual application

        #If you wish you can add some more widgets and customize (Please do it thsi layout is very very booring)

        #Creating the screen
        self.root=tkinter.Tk()
        self.root.geometry("500x300")

        #Creating the widgets
        self.label1=tkinter.Label(self.root,text="Process")
        self.butStart = tkinter.Button(text='Start',width=10,height=3,command=lambda:self.butQue.put('on',False))
        self.butStop = tkinter.Button(text='Stop',width=10,height=3,command=lambda:self.butQue.put('off',False))

        #Placing the widgets
        self.label1.pack()
        self.butStart.pack()
        self.butStop.pack()

        #This is the command given to loop_handler process to start the auto clicker
        self.butQue.put('start')
        self.root.mainloop()

        #This is the command given to loop_handler process to totally terminate whole app
        self.butQue.put('totalOff')
        
        

if __name__=='__main__':
    #Creating The required Queues
    istruQue = multiprocessing.Queue(2)
    butQue = multiprocessing.Queue()
    startAgainQue = multiprocessing.Queue()
    stAgFix = multiprocessing.Queue()

    #Creating the class variable
    loop_class=loops(istruQue,butQue,startAgainQue,stAgFix)

    #Creating required processes
    main = multiprocessing.Process(target=loop_class.loop1)
    app=multiprocessing.Process(target=loop_class.loop2)
    handler=multiprocessing.Process(target=loop_class.loop_handler)

    #Starting the processes
    handler.start()
    main.start()
    app.start()

    #This is the process in our main function which handles every other processes
    while True:
        #Waiting for and command from loop handler function
        startAgainCond = startAgainQue.get()

        #The messages which tells to do which function

        #'startAgain' message is sent when one time the start button is pressed and again pressed even after pressing any other button in between
        if startAgainCond =='startAgain':

            #checking when the start button is pressed is the autoclicker(main) function is already started
            if main.is_alive()==True:
                #If the autoclciker is already on it just send the confirmation and does nothing
                stAgFix.put(True)
                continue
            
            #If the autoclicker is off then this condition is true
            elif main.is_alive()==False:
                #Now clcosing the Process to start it fresh again
                main.close()
                #After closing , again we are initilazing the process
                main = multiprocessing.Process(target=loop_class.loop1)
                #then starting the process
                main.start()
                #Sending Confirmation
                stAgFix.put(False)

        #This is the command to check if the autoclciker is already running or not
        elif startAgainCond =='isAlive':

            #When the autoclicker if off this executes
            if main.is_alive() == False:
                #It just sends false
                stAgFix.put(False)
                continue
            #When the autoclicker if on this executes
            elif main.is_alive()==True:
                #It just sends true
                stAgFix.put(True)
                continue

        #'totalStop' is only sent by the function if the pogram exits fully
        elif startAgainCond=='totalStop':
            break
    

    



