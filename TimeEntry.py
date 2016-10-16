from tkinter import *
from tkinter import font
import time


def process_values(self, values):
    """
    This procedure applies changes in config of self to its children.
    Values are cnf or kw from configure
    """
    key_list = [k for k in values.keys()]
    for k in key_list:
        for c in self.winfo_children():
            if k in c.config().keys():
                if k in ('bg', 'background', 'fg') and isinstance(c, Button):
                    continue
                c[k] = values[k]
            elif k in ('font', 'state') and isinstance(c, SpinButton):
                c[k] = values[k]
        if k not in self.config().keys():
            values.pop(k)


def get_copy_kwargs_for_class(classname, kwargs):
    """
    return a copy of kwargs where keys that are not present in classname.config() are popped
    """
    if classname is None or not callable(classname):
        return None
    args = kwargs.copy()
    available_options = [l for l in classname().config().keys()]
    for k in kwargs.keys():
        if k not in available_options:
            args.pop(k)
    return args


class DigitEntry(Entry):
    """
    Entry that allows input only integers
    max_value, min_value - maximum and minimum allowed values. if user inputs incorrect value, programm restores last correct
    max_length is used for filling with zeros

    you can specify handlers for up, down, right, left keys in two ways:
    1. specify them in constructor like this
        DigitEntry(frame, on_left_press=your handler)
    2. set your handler to on_left_press
        de = DigitEntry(frame)
        de.on_left_press = your_handler
    """
    def __init__(self, master=None, max_value=None, min_value=None, max_length=None, default_value=0, **kwargs):
        self.max_value = max_value
        self.min_value = min_value
        self.max_length = max_length
        self.prev_value = None

        self.on_left_press = None
        self.on_right_press = None
        self.on_up_press = None
        self.on_down_press = None

        if 'on_left_press' in kwargs.keys():
            self.on_left_press = kwargs.pop('on_left_press')
        if 'on_right_press' in kwargs.keys():
            self.on_right_press = kwargs.pop('on_right_press')
        if 'on_up_press' in kwargs.keys():
            self.on_up_press = kwargs.pop('on_up_press')
        if 'on_down_press' in kwargs.keys():
            self.on_down_press = kwargs.pop('on_down_press')

        self.value = StringVar()
        self.value.trace("w", self.validate)
        self.set_value(default_value)
        self.prev_value = self.value.get()

        Entry.__init__(self, master, textvariable=self.value, width=max_length, **kwargs)

        self.bind('<Left>', self.left_press)
        self.bind('<Right>', self.right_press)
        self.bind('<Up>', self.up_press)
        self.bind('<Down>', self.down_press)

    def left_press(self, event):
        if callable(self.on_left_press):
            self.on_left_press()

    def right_press(self, event):
        if callable(self.on_right_press):
            self.on_right_press()

    def up_press(self, event):
        if callable(self.on_up_press):
            self.on_up_press()

    def down_press(self, event):
        if callable(self.on_down_press):
            self.on_down_press()

    def get_value(self):
        return int(self.value.get())

    def set_value(self, value):
        if value is None:
            value = 0
        self.validate({'new_value': str(value)})

    def validate(self, *args):
        is_valid = True
        value = None
        try:
            '''
            If you will set value using self.value.set(some_value), validate won't be able to update entry.
            That's why you should use set_value method, which calls validate and sends new value with *args
            '''
            if args and isinstance(args[0], dict):
                if 'new_value' in args[0].keys():
                    value = args[0]['new_value']
            if value is None:
                value = self.value.get()
            if self.max_length is not None:
                value = value[:self.max_length]
            value = 0 if value == '' else int(value)
        except ValueError:
            is_valid = False
        if is_valid and self.max_value is not None:
            is_valid = value <= self.max_value
        if is_valid and self.min_value is not None:
            is_valid = value >= self.min_value
        if is_valid:
            self.prev_value = value
            value = str(value)
            if self.max_length is not None:
                value = value.zfill(self.max_length)
            self.value.set(value)
        else:
            self.value.set(self.prev_value)


class SpinButton(Frame):
    """
    Simple frame with spin buttons.
    You can specify your handlers with on_up_click and on_down_click
    Size of buttons is determinded by size of font (1/3 of size of font)
    """
    def __init__(self, master, on_up_click, on_down_click, **kwargs):
        if 'font' in kwargs.keys():
            f = self.get_font(kwargs.pop('font'))
        else:
            f = self.get_font(font.nametofont('TkDefaultFont').actual())

        frame_args = get_copy_kwargs_for_class(Frame, kwargs)
        Frame.__init__(self, master, **frame_args)

        button_args = get_copy_kwargs_for_class(Button, kwargs)
        for i in ('relief', 'border', 'bg', 'background', 'fg'):
            if i in button_args.keys():
                button_args.pop(i)

        self.up_button = Button(self, text='▲', command=on_up_click, width=2, font=f, **button_args)
        self.up_button.pack(fill=BOTH, expand=1)
        self.down_button = Button(self, text='▼', command=on_down_click, width=2, font=f, **button_args)
        self.down_button.pack(fill=BOTH, expand=1)

    def get_font(self, f):
        f = font.Font(font=f)
        f['size'] //= 4
        return f

    def configure(self, cnf=None, **kw):
        if cnf is not None:
            if 'font' in cnf.keys():
                cnf['font'] = self.get_font(cnf['font'])
            process_values(self, cnf)

        if kw is not None:
            if 'font' in kw.keys():
                kw['font'] = self.get_font(kw['font'])
            process_values(self, kw)

        self._configure('configure', cnf, kw)


class TimeEntry(Frame):
    """
    Time entry. You can specify time with default_time in constructor or you can change it after creation
    using set_time. You can specify it with time.struct_time or just tuple(hour, minute, second)
    """
    def __init__(self, master=None, default_time=None, **kwargs):

        if 'bg' not in kwargs.keys():
            kwargs['bg'] = 'white'
        if 'relief' not in kwargs.keys():
            kwargs['relief'] = SUNKEN
        if 'borderwidth' not in kwargs.keys():
            kwargs['borderwidth'] = 1

        entry_args = get_copy_kwargs_for_class(DigitEntry, kwargs)
        entry_args['relief'] = FLAT
        entry_args['border'] = 0
        entry_args['on_up_press'] = self.up_press
        entry_args['on_down_press'] = self.down_press
        entry_args['on_left_press'] = self.left_press
        entry_args['on_right_press'] = self.right_press

        label_args = get_copy_kwargs_for_class(Label, entry_args)
        btn_args = get_copy_kwargs_for_class(Button, entry_args)
        frame_args = get_copy_kwargs_for_class(Frame, kwargs)

        Frame.__init__(self, master, **frame_args)
        self.entry_hour = DigitEntry(self, max_value=23, min_value=0, max_length=2, **entry_args)
        self.entry_hour.pack(side=LEFT)
        Label(self, text=':', **label_args).pack(side=LEFT)
        self.entry_minute = DigitEntry(self, max_value=59, min_value=0, max_length=2, **entry_args)
        self.entry_minute.pack(side=LEFT)
        Label(self, text=':', **label_args).pack(side=LEFT)
        self.entry_second = DigitEntry(self, max_value=59, min_value=0, max_length=2, **entry_args)
        self.entry_second.pack(side=LEFT)

        if not isinstance(default_time, time.struct_time) and not isinstance(default_time, tuple):
            default_time = time.localtime()
        self.set_time(default_time)

        SpinButton(self, self.up_press, self.down_press, **btn_args).pack(side=LEFT, fill=Y, expand=1)

    def configure(self, cnf=None, **kw):
        if cnf is not None:
            process_values(self, cnf)
        if kw is not None:
            process_values(self, kw)

        self._configure('configure', cnf, kw)

    def set_time(self, new_time):
        hour, minute, second = (0, 0, 0)
        if isinstance(new_time, time.struct_time):
            hour = new_time.tm_hour
            minute = new_time.tm_min
            second = new_time.tm_sec
        elif isinstance(new_time, tuple):
            hour, minute, second = new_time
        self.entry_hour.set_value(hour)
        self.entry_minute.set_value(minute)
        self.entry_second.set_value(second)

    def get_time(self):
        """
        return entered time in tuple (hour, minute, second)
        """
        return self.entry_hour.get_value(), self.entry_minute.get_value(), self.entry_second.get_value()

    def get_active_entry(self):
        """
        Get current active entry
        """
        if self.focus_get() == self.entry_hour:
            return self.entry_hour
        elif self.focus_get() == self.entry_minute:
            return self.entry_minute
        elif self.focus_get() == self.entry_second:
            return self.entry_second

    def up_press(self):
        """
        increments value in active entry. this method is called with SpinButtons or by hitting up arrow key
        """
        entry = self.get_active_entry()
        if entry:
            value = int(entry.get_value())
            value += 1
            if entry.max_value is not None and entry.min_value is not None and value > entry.max_value:
                value = entry.min_value
            entry.set_value(value)

    def down_press(self):
        """
        decrements value in active entry. this method is called with SpinButtons or by hitting down arrow key
        """
        entry = self.get_active_entry()
        if entry:
            value = int(entry.get_value())
            value -= 1
            if entry.max_value is not None and entry.min_value is not None and value < entry.min_value:
                value = entry.max_value
            entry.set_value(value)

    def left_press(self):
        """
        set focus to previous entry if you press left arrow key and caret position is 0
        """
        entry = self.get_active_entry()
        if entry:
            if entry.index(INSERT) == 0:
                if entry == self.entry_second:
                    self.entry_minute.focus()
                    self.entry_minute.icursor(END)
                elif entry == self.entry_minute:
                    self.entry_hour.focus()
                    self.entry_hour.icursor(END)

    def right_press(self):
        """
        set focus to next entry if you press right arrow key and caret position is at the end of entry
        """
        entry = self.get_active_entry()
        if entry:
            if entry.index(INSERT) == len(entry.get()):
                if entry == self.entry_hour:
                    self.entry_minute.focus()
                    self.entry_minute.icursor(0)
                elif entry == self.entry_minute:
                    self.entry_second.focus()
                    self.entry_second.icursor(0)

if __name__ == '__main__':
    root = Tk()
    frame = Frame(root, relief=SUNKEN)
    frame.pack(side=LEFT)
    te = TimeEntry(frame, font=('Helvetica', 14, NORMAL))
    te.pack(side=TOP)

    root.mainloop()