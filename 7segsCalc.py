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

"""
Цвета сегмента индикатор и фона
"""
ACTIVE_COLOR = "green2"
DEACTIVE_COLOR = "dark green"
BG_COLOR = "gray14"
OUTLINE_COLOR = "green"
"""
Порядок следования сегментов при перевернутом индикаторе
"""
BLOCK_ROTATE = (3, 4, 5, 0, 1, 2, 6)

def setbit(target, bit):
    """
    Устанавливает бит bit в 1 в байте target
    """
    return target | (1 << bit)

def unsetbit(target, bit):
    """
    Сбрасывает бит bit в 0 в байте target
    """
    return target & ~ (1 << bit)

def calck_bit(active, anode, target, bit):
    """
    Определяет установить или сбросить бит bit
    в байте target в зависимости от типа индикатора:
    с общим анодом или с общим катодом
    active - сегмент сетиться или нет
    anode - общий аноде (1) или катод (0)
    target - байт цель
    bit - номер бита
    """
    if anode == 1:
        if active:
            return unsetbit(target, bit)
        else:
            return setbit(target, bit)
    else:
        if active:
            return setbit(target, bit)
        else:
            return unsetbit(target, bit)

def detect_bit(target, connect_type, anode, active, index):
    """
    Определяет какой бит надо изменить в байте target в зависимости
    от типа подключения и типа индикатора
    target - байт цель
    connect_type - тип подключения
    anode - общий аноде (1) или катод (0)
    active - сегмент сетиться или нет
    index - индекс сегмента индикатора (от 0 до 6 (от 'a' до 'g'))
    возвращает байт с измененным битом
    """
    if connect_type == 0:
        return calck_bit(active, anode, target, 7 - index)
    elif connect_type == 1:
        return calck_bit(active, anode, target, 1 + index)
    elif connect_type == 2:
        return calck_bit(active, anode, target, 6 - index)
    elif connect_type == 3:
        return calck_bit(active, anode, target, index)
    return target

class Segment():
    """
    Класс отрисовки сегмента индикатора на канве
    """
    def __init__(self, canvas, index):
        """
        canvas - канва Tkinter
        index - символьный индекс сегмента индикатора (от 'a' до 'g' и 'dp')
        """
        self.canvas = canvas
        self.index = index
        self.active = False #Светиться сегмент или нет, изначально выключен
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
        """
        Переворачивает индикатор верх ногами
        """
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
        """
        Определяет нахождение координат x, y в области сегмента.
        При попадании меняет цвет и статус active сегмента
        """
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
    """
    Класс основного окна программы
    """
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
        #в каком положении находится индикатор, нормальном (0) или вверх ногами (1)
        self.var_rotate = IntVar() 
        self.btn_rotate = Checkbutton(self.conf_frame, text="Перевернуто", variable=self.var_rotate, \
                                    onvalue=1, offvalue=0, command=self.rotate);
        self.btn_rotate.pack(side="top")
        #тип индикатора: с общим катодом (0) или анодом (1)
        self.var_anode = IntVar()
        self.var_anode.set(1)
        self.btn_anode = Checkbutton(self.conf_frame, text="Общий анод", variable=self.var_anode, \
                                    onvalue=1, offvalue=0, command=self.calck);
        self.btn_anode.pack(side="top")
        #группа радиокнопок определяющих тип подключения индикаторов
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
        #вывод результата
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
        """
        Создание массива сегментов
        """
        self.segments = [Segment(self.canva, "a"), Segment(self.canva, "b"),
                         Segment(self.canva, "c"), Segment(self.canva, "d"),
                         Segment(self.canva, "e"), Segment(self.canva, "f"),
                         Segment(self.canva, "g"), Segment(self.canva, "dp")]

    def rotate(self):
        """
        Разворачивает индикатор
        """
        self.segments[len(self.segments) - 1].headup(self.var_rotate.get())
        self.calck()


    def calck(self):
        """
        Вычисление байта результата
        """
        if self.var_anode.get() == 0:
            result = 0
        else:
            result = 0xFF
        #вычисление битов (от 'a' до 'g') и их изменение
        for i in range(len(self.segments) - 1):
            if self.var_rotate.get() == 0:
                seg = self.segments[i]
            else:
                seg = self.segments[BLOCK_ROTATE[i]]
            result = detect_bit(result, self.var_type.get(), self.var_anode.get(), seg.active, i)
        #определение бита десятичной точки
        if self.segments[len(self.segments)-1].active:
            if self.var_type.get() < 2:
                if self.var_anode.get() == 0:
                    result = setbit(result, 0)
                else:
                    result = unsetbit(result, 0)
            else:
                if self.var_anode.get() == 0:
                    result = setbit(result, 7)
                else:
                    result = unsetbit(result, 7)
        #вывод результата
        self.result2["text"] = "%9s" % bin(result)
        self.result16["text"] = "0x%02X" % result

    def lbtn_click(self, event):
        """
        Отработка нажатие ЛКМ на канве
        """
        for i in range(len(self.segments)):
            self.segments[i].check_mouse(event.x, event.y)
        self.calck()

    def mainloop(self):
        """
        Основной цикл окна программы
        """
        self.tk.mainloop()

    def copy2(self):
        """
        Копирование в буфер обмена текстового значения
        результата в двойчном формате
        """
        self.tk.clipboard_clear()
        self.tk.clipboard_append(self.result2["text"])

    def copy16(self):
        """
        Копирование в буфер обмена текстового значения
        результата в шестнадцатеричном формате
        """
        self.tk.clipboard_clear()
        self.tk.clipboard_append(self.result16["text"])
        
if __name__ == '__main__':
    main = SevenSegWin()
    main.mainloop()
