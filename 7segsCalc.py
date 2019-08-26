#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  7segsCalc.py
#  
#  Copyright 2019 Alexandr Balatsky <ambclub@yandex.ru>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from Tkinter import *
from functools import partial

ACTIVE_COLOR = "green2"
DEACTIVE_COLOR = "dark green"
BG_COLOR = "gray14"
OUTLINE_COLOR = "green"

def setbit(target, bit):
    return target | (1 << bit)

def unsetbit(target, bit):
    return target & ~ (1 << bit)

def calckbit(active, anode, target, bit):
    print active, ' ', anode, ' ', bit
    if anode == 1:
        print '   anode 1'
        if active:
            print '   unset bit'
            return unsetbit(target, bit)
        else:
            print '   set bit'
            return setbit(target, bit)
    else:
        print '   anode 0'
        if active:
            print '   set bit'
            return setbit(target, bit)
        else:
            print '   unset bit'
            return unsetbit(target, bit)

class Segment():
    def __init__(self, canvas, index):
        self.canvas = canvas
        self.index = index
        self.active = False
        self.id = -1
        if index == "a":
            self.pnts = ((92,50),(112,32),(188,32),(208,50),(188,68),(112,68))
        elif index == "b":
            self.pnts = ((192,72),(210,52),(228,72),(228,148),(210,168),(192,148))
        elif index == "c":
            self.pnts = ((192,192),(210,172),(228,192),(228,268),(210,288),(192,268))
        elif index == "d":
            self.pnts = ((92,292),(112,272),(188,272),(208,290),(188,308),(112,308))
        elif index == "e":
            self.pnts = ((72,192),(90,172),(108,192),(108,268),(90,288),(72,268))
        elif index == "f":
            self.pnts = ((72,72),(90,52),(108,72),(108,148),(90,168),(72,148))
        elif index == "g":
            self.pnts = ((92,170),(112,152),(188,152),(208,170),(188,188),(112,188))
        elif index == "dp":
            self.x = 250
            self.y = 310
            self.rotate = False
        if index == "dp":
            self.id = self.canvas.create_oval(self.x - 20, self.y - 20, self.x + 20, self.y + 20, \
                                                    fill=DEACTIVE_COLOR, outline=OUTLINE_COLOR, width=2)
        else:
            self.id = self.canvas.create_polygon(self.pnts, fill=DEACTIVE_COLOR, outline=OUTLINE_COLOR, width=2) 

    def headup(self, point_down):
        if self.index != "dp":
            return
        if point_down:
            self.x = 50
            self.y = 30
        else:
            self.x = 250
            self.y = 310
        self.canvas.coords(self.id, self.x - 20, self.y - 20, self.x + 20, self.y + 20)

    def check_mouse(self, x, y):
        if self.index == "dp":
            if (y >= self.y - 20 and y <= self.y + 20) \
                and (x >= self.x - 20 and x <= self.y + 20):
                self.active = not self.active
        else:
            if self.index in ('a','d','g'):
                if (x >= self.pnts[1][0] and x <= self.pnts[2][0]) \
                    and (y >= self.pnts[1][1] and y <= self.pnts[4][1]):
                    self.active = not self.active
            else:
                if (x >= self.pnts[0][0] and x <= self.pnts[2][0]) \
                    and (y >= self.pnts[0][1] and y <= self.pnts[3][1]):
                    self.active = not self.active
        if self.active:
            self.canvas.itemconfig(self.id, fill = ACTIVE_COLOR)
        else:
            self.canvas.itemconfig(self.id, fill = DEACTIVE_COLOR)

class SevenSegWin:
    def __init__(self):
        self.tk = Tk()
        self.tk.title("Расчет значений 7 сегментного индикатора")
        self.tk.resizable(0,0)

        self.canva = Canvas(self.tk, width = 300, height=350, bg=BG_COLOR)
        self.canva.pack(side="left")
        self.create_segment()
        self.canva.bind("<Button-1>", self.lbtn_click)
        
        self.conf_frame = Frame(self.tk)
        self.conf_frame.pack()
        self.var_rotate = IntVar()
        self.btn_rotate = Checkbutton(self.conf_frame, text="Перевернуто", variable=self.var_rotate, \
                                    onvalue=1, offvalue=0, command=self.rotate);
        self.btn_rotate.pack(side="top")
        self.var_anode = IntVar()
        self.var_anode.set(1)
        self.btn_anode = Checkbutton(self.conf_frame, text="Общий анод", variable=self.var_anode, \
                                    onvalue=1, offvalue=0, command=self.calck);
        self.btn_anode.pack(side="top")
        lbl = Label(self.conf_frame, text='Порядок подключения')
        lbl.pack(side="top")
        self.var_type = IntVar()
        self.rbtn_type0 = Radiobutton(self.conf_frame, text="a b c d e f g DP", variable=self.var_type, \
                                            value=0, command=self.calck)
        self.rbtn_type0.pack(side="top")
        self.rbtn_type1 = Radiobutton(self.conf_frame, text="g f e d c b a DP", variable=self.var_type, \
                                            value=1, command=self.calck)
        self.rbtn_type1.pack(side="top")
        self.rbtn_type2 = Radiobutton(self.conf_frame, text="DP a b c d e f g", variable=self.var_type, \
                                            value=2, command=self.calck)
        self.rbtn_type2.pack(side="top")
        self.rbtn_type3 = Radiobutton(self.conf_frame, text="DP g f e d c b a", variable=self.var_type, \
                                            value=3, command=self.calck)
        self.rbtn_type3.pack(side="top")
        self.var_type.set(0)
        self.result2 = Label(self.conf_frame, text = '0b00000000', bg="yellow")
        self.result2.pack(side="top")
        self.btn_copy2 = Button(self.conf_frame, text = "копировать", command=self.copy2)
        self.btn_copy2.pack(side="top")
        self.result16 = Label(self.conf_frame, text = '0x00', bg="yellow")
        self.result16.pack(side="top")
        self.btn_copy16 = Button(self.conf_frame, text = "копировать", command=self.copy16)
        self.btn_copy16.pack(side="top")
        self.calck()

    def create_segment(self):
        self.segments = [Segment(self.canva, "a"), Segment(self.canva, "b"),
                         Segment(self.canva, "c"), Segment(self.canva, "d"),
                         Segment(self.canva, "e"), Segment(self.canva, "f"),
                         Segment(self.canva, "g"), Segment(self.canva, "dp")]

    def rotate(self):
        self.segments[len(self.segments) - 1].headup(self.var_rotate.get())
        self.calck()

    def calck(self):
        if self.var_anode.get() == 0:
            result = 0
        else:
            result = 0xFF
        #TODO перевернутый индикатор
        for i in range(len(self.segments) - 1):
            if self.var_type.get() == 0:
                result = calckbit(self.segments[i].active, self.var_anode.get(), \
                    result, 7 - i)
            if self.var_type.get() == 1:
                result = calckbit(self.segments[i].active, self.var_anode.get(), \
                    result, i + 1)
            if self.var_type.get() == 2:
                result = calckbit(self.segments[i].active, self.var_anode.get(), \
                    result, 6 - i)
            if self.var_type.get() == 3:
                result = calckbit(self.segments[i].active, self.var_anode.get(), \
                    result, i)
        #TODO установить бит точки
        self.result2["text"] = "%9s" % bin(result)
        self.result16["text"] = "0x%02X" % result

    def lbtn_click(self, event):
        for i in range(len(self.segments)):
            self.segments[i].check_mouse(event.x, event.y)
        self.calck()

    def mainloop(self):
        self.tk.mainloop()

    def close(self):
        self.tk.destroy()

    def copy2(self):
        self.tk.clipboard_clear()
        self.tk.clipboard_append(self.result2["text"])

    def copy16(self):
        self.tk.clipboard_clear()
        self.tk.clipboard_append(self.result16["text"])
        
if __name__ == '__main__':
    main = SevenSegWin()
    main.mainloop()
