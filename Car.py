''' # CarGUI
Application for simulating of 1D car movement with constant speed.

Short Guide:
* Textbox receives only integers
* Type desired speed and distance
* Press "start" to simulate car movement with given parameters.
* Press "stop" to stop car movement.
* Press "Resume" to resume stopped movement.
* Press "reset" to reset car position.
'''


import tkinter as tk  # for GUI purposes
from tkinter import messagebox
import os


from PIL import ImageTk, Image # for reading and displaying images


class CarGUI: # create a class for the GUI
    def __init__(self, window=None):

        # init params for movement function
        self.window = window
        self.endpoint = 340  # pixels the car needs to move. line length in pixels = 355-15 = 340 pix
        self.stop_flag = False
        self.dx = 0
        self.pos = 0

        # canvas object to create car image + boxframe
        self.canvas = tk.Canvas(self.window, highlightthickness=1, highlightbackground="black")
        self.canvas.configure(background='white')
        self.canvas.create_rectangle(10, 50, 490, 250, outline='grey', width=3)

        # create current position indicator (title + value)
        self.position_title = tk.Label(self.window, height=1, width=14, text=f'Current Position: ', bg='white')
        self.position_ind = tk.Label(self.window, height=1, width=5, text=f' {self.pos} ', bg='white')

        self.canvas.create_window(15, 300, anchor='nw', window=self.position_title)
        self.canvas.create_window(150, 300, anchor='nw', window=self.position_ind)
        self.canvas.create_line(15, 200, 485, 200, arrow=tk.LAST) # display arrow

        # configure and create position interface (title + textbox + units)
        self.position_txtBox = tk.Text(self.window, height=1, width=10)
        self.position_label = tk.Label(self.window, height=1, width=15, text='Target Position:', bg='white')
        self.position_units = tk.Label(self.window, height=1, width=7, text='[steps]', bg='white')
        self.canvas.create_window(140, 350, anchor='nw', window=self.position_txtBox)
        self.canvas.create_window(5, 350, anchor='nw', window=self.position_label)
        self.canvas.create_window(230, 350, anchor='nw', window=self.position_units)

        # configure and create velocity interface (title + textbox + units)
        self.velocity_txtBox = tk.Text(self.window, height=1, width=10)
        self.velocity_label = tk.Label(self.window, height=1, width=14, text='Input Velocity:', bg='white')
        self.velocity_units = tk.Label(self.window, height=1, width=10, text='[steps/sec]', bg='white')
        self.canvas.create_window(140, 400, anchor='nw', window=self.velocity_txtBox)
        self.canvas.create_window(5, 400, anchor='nw', window=self.velocity_label)
        self.canvas.create_window(230, 400, anchor='nw', window=self.velocity_units)

        # creating car image and axis on canvas
        self.img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.curdir, 'car.png')))
        self.car = self.canvas.create_image(15, 100, anchor='nw', image=self.img)
        self.canvas.pack(fill='both', expand=1)

        # create command button
        self.command_b = tk.Button(self.canvas, text="Start", command=self.read_params)
        self.canvas.create_window(10, 450, anchor='nw', window=self.command_b)

        # create stop button
        self.stop_b = tk.Button(self.canvas, text="Stop", command=self.stop)


        # create reset button
        self.reset_b = tk.Button(self.canvas, text="Reset", command=self.reset)
        self.canvas.create_window(100, 450, anchor='nw', window=self.reset_b)



    def read_params(self):


        # read target position and velocity inputs from user
        posIn = self.position_txtBox.get(1.0, "end-1c")
        velIn = self.velocity_txtBox.get(1.0, "end-1c")

        # validate input is numeric
        if not (posIn.isnumeric() and velIn.isnumeric()):
            messagebox.showwarning("Wrong Input", "Please enter numeric values")
            return

        #change input to float
        posIn = float(posIn)
        velIn = float(velIn)
        
        
        if not (posIn > 1 and velIn > 1):
            messagebox.showwarning("Wrong Input", "Please enter non-zero values")
            return

        # calculate time_step [(m):(m/sec)=sec].
        time_to_complete = (posIn / velIn)

        self.dist2pix_ratio = posIn/self.endpoint # for displaying current position in terms of input steps

        # calculate step size in pixels (calls of the movement function) are needed
        self.dx = self.endpoint/time_to_complete/100  # divided by 100 --> function is called to move each 10ms
        self.movement()

    def movement(self):

        if self.stop_flag: # stop when pressed "Stop".
            return

        # change button function to 'stop'
        self.command_b["command"] = self.stop
        self.command_b["text"] = "Stop"

        # run until reaching the end of line
        if not(self.pos < self.endpoint):
            messagebox.showinfo("Movement Info", "Finished Moving. Reseting position.")
            self.reset()
            return

        # disable textboxes
        self.position_txtBox["state"] = "disabled"
        self.position_txtBox["bg"] = "grey"
        self.velocity_txtBox["state"] = "disabled"
        self.velocity_txtBox["bg"] = "grey"

        # This moves the car to x, y coordinates (add the step)
        self.canvas.move(self.car, self.dx, 0)  # 1-dimensional movement
        self.pos = (self.pos + self.dx) # update global position
        self.position_ind["text"] = f'{int(self.dist2pix_ratio*self.pos)}  ' # update current position text according to input position
        self.canvas.after(10, self.movement) # call again after 10ms (for smooth movement)

    def resume(self):
        self.stop_flag = False
        self.movement()

    def stop(self):
        self.stop_flag = True
        self.command_b["text"] = "Resume"
        self.command_b["command"] = self.resume

    def reset(self): #reset back to default, keeping last values in textboxes
        self.canvas.move(self.car, -self.pos, 0)
        self.position_txtBox["state"] = "normal"
        self.position_txtBox["bg"] = "white"
        self.velocity_txtBox["state"] = "normal"
        self.velocity_txtBox["bg"] = "white"
        self.command_b["text"] = "Start"
        self.command_b["command"] = self.read_params
        self.pos = 0
        self.position_ind["text"] = 0
        self.stop_flag = False


if __name__ == "__main__":
    # object of class Tk, responsible for creating
    # a tkinter toplevel window
    window = tk.Tk()
    window.title('Car Movement App')
    window.geometry('500x550') # window size
    gui = CarGUI(window)  # pass the tk object to the CarGUI class

    # Start function main loop (start the app)
    window.mainloop()
