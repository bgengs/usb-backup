from Tkinter import *
import scan

class ScrolledList(Frame):
    def __init__(self, master=None, items=[]):
        Frame.__init__(self, master)
        #self.pack()
        self.config(bg="black")
        self.make_wigets(items)

    def runCommand(self, lable, event):
        print(lable, event)

    def handleList(self, event):
        #index = self.listbox.curselection()
        label = self.listbox.get(ACTIVE)
        self.runCommand(label, event)

    def make_wigets(self, items):
        sbar = Scrollbar(self)
        lst = Listbox(self, relief=SUNKEN)
        sbar.config(command=lst.yview)
        lst.config(yscrollcommand=sbar.set, width=50, height=30)
        sbar.pack(side=RIGHT, fill=Y)
        lst.pack(side=LEFT, expand=YES, fill=BOTH)
        for row, label in enumerate(items):
            lst.insert(row, label)
        lst.config(selectmode=SINGLE, setgrid=1)
        lst.bind('<Button-1>', self.handleList)
        self.listbox = lst

class Extensions(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        #self.config(bg="white")
        #self.pack()
        self.make_wigets()

    def make_wigets(self):
        Checkbutton(self, text="Personal (.docx, .pdf, etc)").pack(anchor=NW)
        Checkbutton(self, text="Business (.xls, .ppt, etc)").pack(anchor=NW)
        Checkbutton(self, text="Images (.jpg, .png, etc)").pack(anchor=NW)
        Checkbutton(self, text="Music (.mp3, .mp4, etc)").pack(anchor=NW)
        Checkbutton(self, text="Movies (.avi, .mkv, etc)").pack(anchor=NW)
        Checkbutton(self, text="Development (.html, .py, etc)").pack(anchor=NW)
        Checkbutton(self, text="Design (.psd, .ai, etc)").pack(anchor=NW)

class Buttons(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.make_wigets()

    def make_wigets(self, funcScan=scan.scan()):
        Button(self, text="Folders").pack(side=LEFT)
        Button(self, text="Previews").pack(side=LEFT, padx=5)
        Button(self, text="Options").pack(side=LEFT)
        Button(self, text="Help").pack(side=LEFT, padx=5)
        Button(self, text="Scan").pack(side=LEFT)
        Button(self, text="Backup").pack(side=LEFT, padx=5)

class Log(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.make_wigets()

    def make_wigets(self):
        text = Text(self)
        text.config(width=35, height=6, pady=5)
        text.pack()
        text.insert(END, "This is log massage...")


class Window(Tk):
    def __init__(self, master=None):
        Tk.__init__(self, master)
        self.title("Secure USB backup")
        #self.config(bg="red")
        #self.geometry("700x500")
        self.pack_content()

    def pack_content(self):
        options = ['File4ddddddddddd.jpg - %s' %x for x in range(20)]
        Label(self, text="Files Found").grid(row=0, column=0, sticky=W+S)
        ScrolledList(self, items=options).grid(row=1, column=0, rowspan=3, sticky=N+W+E+S)
        Buttons(self).grid(row=1, column=1, sticky=N+W+E+S)
        Extensions(self).grid(row=2, column=1, sticky=N+W+E+S)
        Log(self).grid(row=3, column=1, sticky=W+E+S)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

if __name__ == '__main__':
    #options = ['File.jpg - 1 %s' %x for x in range(20)]
    Window().mainloop()
