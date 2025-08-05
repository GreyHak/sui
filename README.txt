                  Status User Interface (SUI) Python Library
                    Application Programming Interface (API)
                              Written by GreyHak

This document was written for SUI v1.45.8, released 5 August 2025.

Copyright © 2023-2025, GreyHak (github.com/GreyHak), All rights reserved.

** 1 Machine Setup

To use the SUI library, install Python 3, pycryptodome, and a version of
pygame-ce compatible with your version of Python.  For using the <clock>
element, it is also recommend, but not required, to have the tzdata Python
module included in Python 3.9 and later.

   python -m pip install --upgrade pip
   pip install pycryptodome
   pip install pygame_ce
   pip install tzdata

This release of SUI has been built for and tested on:
 - Windows 11 using Python 3.9.13  and pygame-ce 2.5.0 and pycryptodome 3.20.0
 - Windows 11 using Python 3.10.11 and pygame-ce 2.5.0 and pycryptodome 3.20.0
 - Windows 11 using Python 3.11.9  and pygame-ce 2.5.0 and pycryptodome 3.20.0
 - Windows 11 using Python 3.12.10 and pygame-ce 2.5.0 and pycryptodome 3.20.0
 - Windows 11 using Python 3.13.5  and pygame-ce 2.5.5 and pycryptodome 3.23.0

Also tested on:
 - Ubuntu 22.04.3 LTS using Python 3.7.17 and pygame-ce 2.3.2
 - Ubuntu 22.04.3 LTS using Python 3.10.12 and pygame-ce 2.3.2
 - Windows 11 using Python 3.10.6 and pygame-ce 2.5.0 and pycryptodome 3.20.0
 - Windows 11 using Python 3.11.3 and pygame-ce 2.5.0 and pycryptodome 3.20.0
 - Windows 11 using Python 3.12.0 and pygame-ce 2.3.2 and pycryptodome 3.19.0
 - Windows 11 using Python 3.12.0 and pygame-ce 2.5.0 and pycryptodome 3.19.0
 - Windows 11 using Python 3.12.4 and pygame-ce 2.5.0 and pycryptodome 3.19.0
 - Windows 11 using Python 3.12.4 and pygame-ce 2.5.0 and pycryptodome 3.20.0

If you do not require rendering of multi-line text strings, pygame works too:
 - Windows 11 using Python 3.12.0 and pygame 2.5.2

** 2 Including the SUI Python Library

Import the SUI Python library as follows, being sure to reference the package
built for your Python version.

import sys
sys.path.insert(0, "sui_pyc-37.pyc")
import sui_window

*** 2.1 SUI No-Op

"sui_pyc-37.pyc" can be replaced with "sui_pyc-37-noop.pyc" for all the same
API calls to remove the SUI functionality from your application without
removing the API calls from your application.  This no-op library is provided
to allow your application to be of limited use to users without the SUI
license, through they won't have the SUI functionality such as a GUI.  When
using this variant of the library, the frameCallbackFunction described in
Section 4.3 will not be called because no valid Surface can be provided.

** 3 Initialization

suiWindow = sui_window.sui_window(str configFilename,
                                  callbackHandler = None)

This initializes the display, loading the XML configuration file and creating
all the display elements.  The configFilename must provide a path to an XML
file which complies with the sui_config_schema.xsd schema.  callbackHandler,
an optional argument, is the class instance which will handle all callbacks
except the loop frame and loop termination.  These callbacks are described in
Section 7, Callbacks to Your Application's Routines.

*** 3.1 Window Element Colors

The XML configuration file provides a <set-colors> setting for controlling the
color of all window element components.  Window element components can also be
controlled by the application using the API:

   sui_colors.map[nameOfComponentHere] = yourColorHere

This API should be used before initializing sui_window.  The component names
are the <color part> values in sui_config_schema.xsd.  Your color can be any
type which pygame will accept as a color: a 3 or 4 length tuple, a 3 or 4
length list, or a pygame.Color.  You can also use the pygame color dictionary:

   sui_colors.map["border.text"] = pygame.colordict.THECOLORS["orange"]

** 4 Main Loop

suiWindow.loop(terminationCallbackFunction = None,
               terminationCheckCallbackFunction = None,
               frameCallbackFunction = None)

This is the main loop which refreshes the display.  This routine must be
called in the main thread, and it will not return until the display
terminates.  So all other application processing needs to be in a thread.

The callback arguments are defined in the following 4.x sections.  If any of
the callbacks are provided, but not callable, a TypeError exception will be
thrown.

*** 4.1 terminationCallbackFunction

When the loop terminates, but before the loop routine returns, if provided,
sui_window will call the provided callback function.  This is important for
thread-safe termination.  When the loop routine returns, your application
needs to stop using the sui_window instance.

*** 4.2 terminationCheckCallbackFunction

By default the loop termines when the user presses Escape.  If the application
so wishes, this can be overridden by supplying a
terminationCheckCallbackFunction which returns True to terminate or False to
ignore the Escape and continue the loop.

*** 4.3 frameCallbackFunction

If sui_window does not provide all the graphical elements that the application
needs, the application can provide a frame callback which will be called for
each frame to add additional graphics using pygame when sui_window has
completed drawing its own elements.  Be cautious because any delays in this
routine can result in frame rate slow down.  The frame callback provides two
arguments, pygame.Surface and a string specifying the page name.

** 5 Setting Data

suiWindow.setValue(str dataName, value, xValue = 0, bool initializationFlag = False)

This is the method for setting data on the display.  It is thread safe.  The
SUI data handling system works as a set of name/value pairs where the
data-name is configured for various display elements in the XML configuration
file, and setValue is used to set the data.  setValue can set the value for
multiple elements at once if they are all configured with the same data-name.
setValue updates all elements with data-name across all pages, not just the
current page.  value can be a string, integer, decimal/float, boolean or
pygame.Surface.  The types are restricted based on the elements which are
configured to display them.  The xValue parameter is only used for <plot>
elements.

initializationFlag allows for setting the initial value for data.  Setting
initializationFlag to True avoids resetting the activity timer.  So, using
initializationFlag=True to initialize data will prevent the display from
appearing as through data was just received through color changes.

*** 5.1 Setting color-bulb Data

Calling setValue can be supplied with a value specifying any color allowed by
the schema's BulbColorEnum.  Color integers can be either string or integers.
value can also be a 2-D tuple or list where the [0] element is the color and
the [1] element is a bool specifying whether the bulb is lit or not.

*** 5.2 Setting Plot Data

For <plot> elements the value parameter sets the vertical y value.  The <plot>
element was designed and tested for the horizontal xValue to be a time, but
this need not be the case.  The <plot> element knows nothing about time, but
the data lays out on the display in a way that works well for time.

<plot> elements store the data provided with setValue in an array.  Each time
a value is set, all the data from the beginning of the array with an xValue
less than (the largest x value minus the configured x-span) are removed from
the array.  The plot is then drawn to connect the points in the order in which
setValue was called such that the largest x value is always at the far right
of the plot.  Using the far right, as opposed to always plotting the lowest x
value on the left, causes the least disruption when the plot fills up.  The
plot always has the x-axis at y=0.  The plot will plot negative y values and y
values greater than the configured max-y-value.  If the application needs to
plot negative y values, just leave the space below the plot empty when laying
out the display elements in the XML file.

Plot data limitation:  Since the plot was designed for a time-based x-axis,
the y-axis position is always set at the (the largest x value minus the
configured x-span).  As a result the y-axis position is not controlled
explicitly by the application, and the plot will always include at least one
line to the plot's right-most edge.  Since the y-axis position is always based
on the largest x value, the y-axis can only stay in the same place or move up
the x-axis.  The y-axis can never move down the x-axis.  These two constraints
make plotting with anything other than increasing time a bit finicky.

*** 5.3 Setting Table Data

int sui_window.insertTableRow(str dataName, value, int row = -1)

insertTableRow inserts a new row into the named table.  The value must be a
tuple or list with a length matching that of the table's number of columns.
If value is not a length of the number of columns, a ValueError exception is
thrown.  row identifies where to add the new row.  If row is not provided,
negative, or larger than the table, the new row is added to the end of the
table.  The new row's index is returned, or None if the <table> dataName is
unknown.

sui_window.setTableData(str dataName, value, row)

setTableData sets data in the named table.  It handles the value and row
arguments in any of the following ways

1) Setting a whole row identified by the row index.
   The row must be a valid row index integer.  The value must be a tuple or
   list with a length matching that of the table's number of columns.

2) Setting a single cell identified by (row index, column index).
   The row must be tuple or list of length 2.  row[0] and row[1] must be valid
   row and column index integers, respectively.

3) Setting a single cell identified by the row index in a 1-D table.
   The row must be a valid row index integer.

int sui_window.removeTableRow(str dataName, int row = -1)

removeTableRow removes a row from the named table.  If row is negative, it
will be interpreted as wrapping around the end of the table.  The removed
row's index is returned, or None if the <table> dataName is unknown.  If row
specifies an row beyond the range of the table data, a ValueError exception is
thrown.

sui_window.getTableSize(str dataName)

getTableSize returns a tuple (number of rows, number of columns, row height in
pixels, tuple of column widths in pixels).

** 6 Optional Routines

*** 6.1 Getting Data

suiWindow.getValue(str dataName)

Returns the value for the first element defined with name=dataName.  All
elements with name=dataName should have the same value, so this function's
limit of returning only the first one's value really isn't a limitation.

In the example display_example_main.py see how getValue is used to append a
typed character to the value of a string displayed with a <text-value>.

*** 6.2 Changing Display Page

suiWindow.displayPage(str pageName)

Changes the page layout being displayed to the page identified by pageName.
This can be used in conjunction with a left-click on a <button>, <image>,
<on-off-bulb>, <color-bulb> or even <text-value> to switch the page layout.

*** 6.3 Getting Display Page

pageName = suiWindow.getCurrentDisplayedPage()

Returns the name of the page being displayed.

*** 6.4 Setting Data Alert

suiWindow.setAlert(str dataName, bool alertFlag)

Sets the alert flag for all <text-value> and <linear-plot> elements defined
with name=dataName.  This causes the value to be shown in a warning color.
This is intended to highlight out-of-bounds value as determined by the main
application, but it is available for any use case.

*** 6.5 Setting the Focus

suiWindow.setTextValueFocus(str dataName, bool focusFlag)

Sets the focus to all <text-value> elements defined with name=dataName.  Focus
is shown as a box around the whole <text-value> element.  Note that the box is
drawn outside the bounds configured by <text-value left top font-size width>
by 2 pixels.  setTextValueFocus is intended to be used in conjunction with
<text-value callback> for selecting data to be altered, but it is available
for any use case.

*** 6.6 Getting the Focus

flag = suiWindow.getTextValueFocus(str dataName)

Returns the focus value for the first <text-value> element defined with
name=dataName.  Since setTextValueFocus sets the focus for all associated
<text-value> elements, this function's limit of returning only the first one's
focus really isn't a limitation.  If there is no <text-value> element defined
with name=dataName, None is returned.

*** 6.7 Active/Inactive State

suiWindow.setApplicationControlledActivityFlag(bool activeFlag, str dataName = None)
suiWindow.setTimeForAutomaticActivity(float timeInSeconds, str dataName = None)

SUI can display <on-off-bulb>, <color-bulb>, <error-bulb>, <text-value>,
<plot>, <linear-percent>, and <circular-percent> elements in an inactive state
to convey when data backing the elements is no longer being received.  The
active flag which determines when these elements should display as inactive is
determined using two settings.  First, setApplicationControlledActivityFlag
can be used to supply an active flag.  The provided application flag can be
used to force the element to be displayed as inactive.  If the application
does not provide a flag, or the provided flag is True, then SUI can determine
activity automatically based on a time delay.  This active flag is automatic
when the application provides a positive time delay.

dataName is an optional parameter for both of these API calls.  If not
supplied, all elements' settings are changed.

When passing False to setApplicationControlledActivityFlag, the element will
show an inactive state, but setValue calls will still update the element.

When <error-bulb>, <text-value>, <linear-percent>, and/or <circular-percent>
elements are in their alert state, the alert will still be displayed when the
element is inactive.  For <error-bulb> alert is when an error has occurred and
not yet acknowledged.  For <text-value> and <linear-plot> alert is set with
the setAlert API.  For <linear-percent> and <circular-percent> elements
alert is set automatically when the set value exceeds the max-value set in the
configuration file.

*** 6.8 Terminating the Display

suiWindow.terminate()

Terminates the sui_window loop at the end of drawing the current frame.  If
a termination callback was provided to the loop routine, the termination
callback is likely, but not guaranteed, to be called after the terminate
routine.

*** 6.9 Popup Boxes

bool suiWindow.getBoxEnable(str boxDataName)

Call getBoxEnable to determine if a named box is being displayed.  Returns
true if the box is being displayed, false if the box is hidden, or None if the
a box was not identified by the name specified.

suiWindow.setBoxEnable(str boxDataName, bool enableFlag)

Set enableFlag to true to display a box and the elements it contains, or false
to hide it.

** 7 Callbacks to Your Application's Routines

All callbacks are provided to the main application in the main thread.  So all
callback routines can hold up the display refresh rate if they take to long.

*** 7.1 Display Callbacks

As described in Section 4, sui_window's loop routine calls the application
just prior to the sui_window instance becoming invalid.

The <sui> element defines key-pressed-callback and
function-key-pressed-callback attributes.  The key-pressed-callback will
receive two arguments, a key and a modifier.  The key is an integer for any
typed ASCII character and the following special values:

   sui_window.K_BACKSPACE
   sui_window.K_RETURN
   sui_window.K_UP
   sui_window.K_DOWN
   sui_window.K_LEFT
   sui_window.K_RIGHT
   sui_window.K_PAGEUP
   sui_window.K_PAGEDOWN
   sui_window.K_DELETE
   sui_window.K_HOME
   sui_window.K_END
   sui_window.K_INSERT

If the application needs to use the key integer as a character, it should
perform chr(key).  If the application needs to compare the key integer to a
character, it can do something like

   if key == ord("q"):

The function-key-pressed-callback will receive two arguments, an integer and a
modifier.  The integer represents the function key pressed, 1 for F1 through
15 for F15.

The modifier for these two callbacks is a bitwise-ORing of:
   sui_window.KMOD_LSHIFT
   sui_window.KMOD_RSHIFT
   sui_window.KMOD_SHIFT
   sui_window.KMOD_LCTRL
   sui_window.KMOD_RCTRL
   sui_window.KMOD_CTRL
   sui_window.KMOD_LALT
   sui_window.KMOD_RALT
   sui_window.KMOD_ALT
   sui_window.KMOD_LMETA
   sui_window.KMOD_RMETA
   sui_window.KMOD_META
   sui_window.KMOD_CAPS
   sui_window.KMOD_NUM
   sui_window.KMOD_MODE

*** 7.2 Element Callbacks

The <image>, <on-off-bulb>, <color-bulb>, <button>, and <text-value> elements
can all, optionally, provide a callback to the application when they are
left-clicked.  The callbacks all receive two parameters, a string parameter
which is controlled in the XML file and defaults to an empty string, and x/y
coordinates where the click occurred on the element.  These are configured
with the element's callback and callback-parameter attributes in the XML file.

<text-value> produces one of two different types of callbacks.  It can produce
the type described in the previous paragraph which provides the x/y
coordinates when clicked.  If <text-value editable="true">, then it will not
provide a callback when clicked, but instead when the value is edited.  The
first parameter is the <text-value data-name> and the second value is the new
value as a string.

*** 7.3 Table Callbacks

Like other callbacks, left-clicking on a table will provide a callback with
two parameters.  The second parameter is also the x/y coordinates.  The first
parameter is the tuple:
   (row index, column index, cell value in its original data type)
The cell for which data is provided is specifically the cell under the mouse
the when the left-click ends (on the mouse up event).

** 8 Built-In Icons

sui_icons.icons[index] provides access to the built-in icons in the
pygame.Surface format.  These include
   0 = Empty box
   1 = Box with x
   2 = Box with check mark
   3 = Trash can
   4 = Globe
   5 = Camera
   6 = Headphones
   7 = Position marker
   8 = Question mark
   9 = Recycle symbol
   10 = Speaker, front
   11 = Speaker, askew
   12 = Document
   13 = Spreadsheet
   14 = List
   15 = Scissors (cut)
   16 = USB drive
   17 = Magnifying glass
   18 = Phone, desk
   19 = Phone, flip
   20 = Phone, smart
   21 = Drone
   22 = Drink
   23 = Ribbon
   24 = Star
   25 = Pencil
   26 = Pen
   27 = Crayon
   28 = Heart, outline
   29 = Heart, full
   30 = Scale, thin
   31 = Scale, thick
   32 = Calculator
   33 = Calendar
   34 = Compus
   35 = Gauge
   36 = Lock
   37 = Key
   38 = Monitor, front
   39 = Monitor, askew
   40 = Plane, side
   41 = Plane, askew
   42 = Plane, top
   43 = Rocket
   44 = Box with plus
   45 = Triangle (play)
   46 = Circle (record)
   47 = Square (stop)
   48 = Target, circle
   49 = Target, crosshair
   50 = Crosshair, plus
   51 = Crosshair, x
   52 = Crosshair, squart
   53 = Crosshair, four
   54 = Arrow, up
   55 = Arrow, right
   56 = Arrow, down
   57 = Arrow, left
   58 = Arrow, upper right
   59 = Arrow, lower right
   60 = Arrow, lower left
   61 = Arrow, upper left
   62 = Pause
   63 = Wifi
   64 = Plus
   65 = Dash (minus)
   66 = X
   67 = Check mark
   68 = Gear
   69 = Copy
   70 = Guitar
   71 = Audio (music)
   72 = Microphone
   73 = Upload
   74 = Download
   75 = Save
   76 = Paste (clipboard)
   77 = Clock (time)
   78 = Rewind
   79 = Fast forward
