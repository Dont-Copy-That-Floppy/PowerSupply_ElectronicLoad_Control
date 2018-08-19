#!/usr/bin/python
"""
written by Jake Pring from CircuitSpecialists.com
licensed as GPLv3
"""

# gui classes
try:  # windows
    import tkinter
    from tkinter import Menu, filedialog, Toplevel, Button, messagebox, Entry, Label, Canvas
except:  # unix
    import Tkinter as tkinter
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    from Tkinter import Menu, Toplevel, Button, Entry, Label, Canvas

# devices classes
import powersupply
import electronicload

# dependent classes
import sys
import webbrowser
import threading


class GUI:
    def __init__(self):
        self.threads = []
        self.timestamp = []
        self.voltage = []
        self.current = []
        self.output = []
        self.variable_count = 0
        self.programme_file = []
        self.help_url = "https://circuit-specialists.github.io/PowerSupply_ElectronicLoad_Control/"
        self.floor = tkinter.Tk(className=' cs power control')
        self.floor.tk.call(
            'wm', 'iconphoto', self.floor._w,
            tkinter.Image("photo", file="CircuitSpecialists.gif"))
        self.floor.title('Circuit Specialists Power Control')
        self.setWindowSize(self.floor, 700, 500)
        self.setMenuBar()
        self.drawCanvas()

    def drawCanvas(self):
        self.canvas_width = int(self.window_width / 2)
        self.canvas_height = int(self.window_height / 2)
        self.canvas = Canvas(
            self.floor, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        # w.coords(i, new_xy) # change coordinates
        # w.itemconfig(i, fill="blue") # change color
        # (x1,y1,x2,y2)
        self.graph_x1 = 0
        self.graph_y1 = 0
        self.graph_x2 = int(self.canvas_width)
        self.graph_y2 = int(self.canvas_height)
        self.canvas.create_rectangle(
            self.graph_x1, self.graph_y1, self.graph_x2, self.graph_y2, fill="#1a1a1a")

        # grid lines (reticules)
        self.horizontal_line_distance = int(self.canvas_width / 7)
        self.vertical_line_distance = int(self.canvas_height / 7)
        for x in range(self.horizontal_line_distance, self.canvas_width, self.horizontal_line_distance):
            self.canvas.create_line(x, 0, x, self.canvas_height,
                                    fill="#ffffff", dash=(4, 4))
        for y in range(self.vertical_line_distance, self.canvas_height, self.vertical_line_distance):
            self.canvas.create_line(0, y, self.canvas_width, y,
                                    fill="#ffffff", dash=(4, 4))

    def setWindowSize(self, object, width, height):
        # get screen size
        self.screen_width = object.winfo_screenwidth()
        self.screen_height = object.winfo_screenheight()

        # keep the window in ratio
        self.window_width = width
        if (self.screen_width < 1920):
            self.width_aspect = self.window_width / 1920
            self.window_width *= self.width_aspect
        self.window_height = height
        if (self.screen_height < 1080):
            self.height_aspect = self.window_height / 1080
            self.window_height *= self.height_aspect

        # set window to fit in ratio to screen size
        self.window_x = int(self.screen_width / 2 - self.window_width / 2)
        self.window_y = int(self.screen_height / 2 - self.window_height / 2)
        object.geometry('%dx%d+%d+%d' %
                        (self.window_width, self.window_height, self.window_x, self.window_y))

    def setMenuBar(self):
        self.menubar = Menu(self.floor)
        self.setFileMenu()
        self.setEditMenu()
        self.setHelpMenu()
        self.floor.config(menu=self.menubar)

    def setFileMenu(self):
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(
            label="Open CSV File...", command=self.openCSVFile)
        self.filemenu.add_command(label="Save", command=self.donothing)
        self.filemenu.add_command(
            label="Save as...", command=self.save_AS_CSVFile)
        self.filemenu.add_command(label="Close", command=self.donothing)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.floor.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

    def setEditMenu(self):
        self.editmenu = Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Device", command=self.deviceSelection)
        self.editmenu.add_separator()
        self.editmenu.add_command(
            label="Run Single Loop", command=self.runSingleLoop)
        self.editmenu.add_separator()
        self.editmenu.add_command(
            label="Create CSV File", command=self.createCSVFile)
        self.editmenu.add_separator()
        self.editmenu.add_command(
            label="Time Delay", command=lambda: self.getEntry("Time Delay"))
        self.editmenu.add_command(
            label="Voltage", command=lambda: self.getEntry("Voltage"))
        self.editmenu.add_command(
            label="Amperge", command=lambda: self.getEntry("Current"))
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Mode", command=self.donothing)
        self.editmenu.add_command(label="EL Setting", command=self.donothing)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Output", command=self.setOutput)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)

    def setHelpMenu(self):
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(
            label="Help Index", command=lambda: self.gotoURL(self.help_url))
        self.helpmenu.add_command(label="About...", command=self.about)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

    def donothing(self):
        self.null = None

    def setOutput(self):
        self.device.setOutput(
            messagebox.askyesno(
                title="Output State", message="Turn On Output?"))

    def getEntry(self, parameter):
        # pop-up window
        self.top = Toplevel(self.floor)
        self.setWindowSize(self.top, 250, 80)
        self.top.title(parameter)
        self.top.tk.call(
            'wm', 'iconphoto', self.top._w,
            tkinter.Image("photo", file="CircuitSpecialists.gif"))
        self.top.bind('<Return>', self.okay)

        # window parameters
        if (parameter == "Time Delay"):
            Label(self.top, text="Input Time Delay").pack()
            self.entry_type = "TD"
        elif (parameter == "Voltage"):
            Label(self.top, text="Input Voltage Value").pack()
            self.entry_type = "V"
        elif (parameter == "Current"):
            Label(self.top, text="Input Current Value").pack()
            self.entry_type = "A"

        # window function
        self.entry_dialog = Entry(self.top)
        self.entry_dialog.pack(padx=5)
        button_dialog = Button(self.top, text="OK", command=self.okay)
        button_dialog.pack(pady=5)

    def okay(self, event=None):
        self.entry = self.entry_dialog.get()
        self.top.destroy()
        try:
            if (self.entry_type == "TD"):
                print()
            elif (self.entry_type == "V"):
                self.device.setVoltage(self.entry)
            elif (self.entry_type == "A"):
                self.device.setAmperage(self.entry)
        except:
            messagebox.showerror("Error", "Device Not Connected")

    def openCSVFile(self):
        self.programme_filename = filedialog.askopenfilename(
            initialdir="./",
            title="Select file",
            filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        try:
            with open(self.programme_filename, "r") as f:
                self.programme_file = f.readlines()
        except:
            messagebox.showerror("Error", "Unable to open file")

    def save(self):
        try:
            self.log_file = open(self.save_filename + ".csv", "w")
        except:
            pass
        for i in range(0, self.variable_count):
            self.log_file.writelines("%d, %d, %d, %d" % self.timestamp[i],
                                     self.voltage[i], self.current[i],
                                     self.output[i])

    def save_AS_CSVFile(self):
        self.save_filename = filedialog.asksaveasfilename(
            initialdir="./",
            title="Select file",
            filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        self.save()

    def createCSVFile(self):
        self.top = Toplevel(self.floor)
        Label(self.top, text="Create Run CSV").pack()
        self.entry_type = "CSVC"
        self.entry_dialog = Entry(self.top)
        self.entry_dialog.pack(padx=5)
        button_dialog = Button(self.top, text="OK", command=self.okay)
        button_dialog.pack(pady=5)

    def storeVariabels(self, Timestamp, Voltage, Current, Output):
        self.timestamp.append(Timestamp)
        self.voltage.append(Voltage)
        self.current.append(Current)
        self.output.append(Output)

    def runSingleLoop(self):
        self.null = None

    def deviceSelection(self):
        try:
            self.device = powersupply.POWERSUPPLY()
            self.device = self.device.powersupply
            messagebox.showinfo("Power Supply",
                                "Detected: " + self.device.name)
        except:
            try:
                self.device = electronicload.ELECTRONICLOAD()
                self.device = self.device.electronicload
                messagebox.showinfo("Electronic Load",
                                    "Detected: " + self.device.name)
            except:
                messagebox.showerror(
                    "Error", "Sorry, no devices currently supported are found")

    def gotoURL(self, url):
        webbrowser.open_new_tab(url)

    def about(self):
        messagebox.showinfo(
            "About", "Version 1.3 alpha\n"
            "Operating System: %s" % sys.platform)

    def startWindow(self):
        self.floor.mainloop()


if __name__ == "__main__":
    gui = GUI()
    gui.startWindow()
