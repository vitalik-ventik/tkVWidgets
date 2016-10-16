# tkVWidgets
Widgets for TKinter (DigitEntry, SpinButton and TimeEntry)

DigitEntry is a widget that allows user to input integer values. You can specify max, min and default value. 
Also you can specify max_length - value in entry will be filled with zeros to this length.

SpinButton is a widget that contains buttons with up and down arrows. It is like SpinBox, but without entry.
on_up_click and on_down_click are handlers for corresponding actions.

TimeEntry is a widget that allows user to input time. You can specify default_time in two ways - struct_time from time module 
or simple tuple (hours, minutes, seconds). get_time returns tuple (hours, minutes, seconds). 
Widget doesn't support AM/PM format now, but later I will try to add this feature.
