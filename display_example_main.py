# Copyright (c) 2023-2024, GreyHak (github.com/GreyHak), All rights reserved.
# This file alone is licensed under the BSD 3-Clause License.
# The SUI library files are proprietary software usable under license.

import sys
import time
import random
import threading
import sui_window
import sui_colors
import sui_icons
import pygame # Only used here for demonstrating usage of the onFrame callback.

runningFlag = True
activeFlag = True
imagePointerPositionIdx = 0

class CallbackHandler:

   suiWindow = None
   errorIdx = -1
   errors = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
   imagePointerIconIndex = [53, 53]
   imagePointerPosition = [None, None]

   def __init__(self):
      pass

   def onChangePage(self, parameter, xy):
      print(f"Clicked on element at position {xy}")
      if self.suiWindow:
         print(f"Switching from {self.suiWindow.getCurrentDisplayedPage()} to {parameter}")
         self.suiWindow.displayPage(parameter)

   def onPopupPage(self, parameter, xy):
      parameter = parameter.lower() in ('y', 'yes', 't', 'true', 'on', '1')
      self.suiWindow.setBoxEnable("PopupBox", parameter)

   def onAddError(self, parameter, xy):
      if self.suiWindow:
         self.errorIdx += 1
         if self.errorIdx >= len(self.errors):
            self.errorIdx = 0
         self.errors[self.errorIdx] += 1
         self.suiWindow.setValue(f"error{self.errorIdx+1}",  self.errors[self.errorIdx], 0)

   def onKeyPressed(self, key, modifier):
      modifierName = ""
      if modifier & sui_window.KMOD_CTRL:
         modifierName += "Ctrl-"
      if modifier & sui_window.KMOD_ALT:
         modifierName += "Alt-"
      if modifier & sui_window.KMOD_SHIFT:
         modifierName += "Shift-"

      if key == sui_window.K_BACKSPACE:
         print(f"{modifierName}Backspace ({key})")
      elif key == sui_window.K_RETURN:
         print(f"{modifierName}Enter ({key})")
      elif key == sui_window.K_UP:
         print(f"{modifierName}Up ({key})")
      elif key == sui_window.K_DOWN:
         print(f"{modifierName}Down ({key})")
      elif key == sui_window.K_LEFT:
         print(f"{modifierName}Left ({key})")
      elif key == sui_window.K_RIGHT:
         print(f"{modifierName}Right ({key})")
      elif key == sui_window.K_PAGEUP:
         print(f"{modifierName}PageUp ({key})")
         if self.suiWindow.getCurrentDisplayedPage() == "SecondPage":
            self.suiWindow.displayPage("PrimaryPage")
      elif key == sui_window.K_PAGEDOWN:
         print(f"{modifierName}PageDown ({key})")
         if self.suiWindow.getCurrentDisplayedPage() == "PrimaryPage":
            self.suiWindow.displayPage("SecondPage")
      elif key == sui_window.K_DELETE:
         print(f"{modifierName}Delete ({key})")
      elif key == sui_window.K_HOME:
         print(f"{modifierName}Home ({key})")
      elif key == sui_window.K_END:
         print(f"{modifierName}End ({key})")
      elif key == sui_window.K_INSERT:
         print(f"{modifierName}Insert ({key})")
      else:
         print(f"{modifierName}{chr(key)} ({key})")
         if key == ord("q") and (modifier & sui_window.KMOD_CTRL) == 0:
            suiWindow.terminate()
            return

   def onFunctionKeyPressed(self, number, modifier):
      modifierName = ""
      if modifier & sui_window.KMOD_CTRL:
         modifierName += "Ctrl-"
      if modifier & sui_window.KMOD_ALT:
         modifierName += "Alt-"
      if modifier & sui_window.KMOD_SHIFT:
         modifierName += "Shift-"
      print(f"{modifierName}F{number}")
      self.suiWindow.setValue("dynamicUserText", f"{modifierName}F{number}")

   def onTextValueChanged(self, dataName, newValue):
      print(f"{dataName} changed to '{newValue}'")

   def onToggleDataPause(self, unused, xy):
      global activeFlag
      activeFlag = not activeFlag

   def onTableClick(self, tableTuple, xy):
      print(f"Clicking on table provided the callback with: {tableTuple}, {xy}")

   def onIconTableClick(self, tableTuple, xy):
      self.imagePointerIconIndex[imagePointerPositionIdx] = tableTuple[0] * 16 + int(tableTuple[1] / 2)
      print(f"Clicking on icon index {self.imagePointerIconIndex[imagePointerPositionIdx]}")

   def onAddTimeToTable(self, unused, xy):
      randValue = random.random()
      if pygame.key.get_mods() & pygame.KMOD_CTRL:
         try:
            index = self.suiWindow.removeTableRow("DataTable", -1)
            operation = f"{index} removed."
         except ValueError:
            operation = "No rows in table to delete."
      elif randValue < 0.33:
         index = self.suiWindow.insertTableRow("DataTable", ("Time as float", time.time()))
         operation = f"{index} added."
      elif randValue < 0.67:
         index = self.suiWindow.insertTableRow("DataTable", ("Time based on locale", time.strftime("%c", time.localtime())))
         operation = f"{index} added."
      else:
         index = self.suiWindow.insertTableRow("DataTable", ("Time explicit format", time.strftime("%m/%d/%Y %H:%M:%S", time.localtime())))
         operation = f"{index} added."
      (numRows, numColumns, rowHeight, columnWidths) = suiWindow.getTableSize("DataTable")
      print(f"{operation}  The table now has {numRows} rows and {numColumns} columns.  Rows are {rowHeight} pixels high.  Columns are {columnWidths} pixels wide.")

   def onPlaceImagePointer(self, unused, xy):
      self.imagePointerPosition[imagePointerPositionIdx] = xy

   def onFrame(self, surface, pageName):
      if pageName == "PrimaryPage":
         if self.suiWindow.getValue("arcCount") % 36 < 18:
            pygame.draw.circle(surface, sui_colors.map["box.circle"], (1828, 949), 6.5, 0)
      elif pageName == "SecondPage":
         if self.imagePointerPosition[imagePointerPositionIdx]:
            icon = pygame.transform.smoothscale(sui_icons.icons[self.imagePointerIconIndex[imagePointerPositionIdx]], (32, 32))
            surface.blit(icon, (self.imagePointerPosition[imagePointerPositionIdx][0] + 667 - 16, self.imagePointerPosition[imagePointerPositionIdx][1] + 98 - 16))

   def getOkayToTerminate(self):
      return True

   def onTerminate(self):
      global runningFlag
      runningFlag = False
      print("SUI notified main application that it is terminating normally.")

def runDataThread(suiWindow):

   arcCount = 0
   errorBulbCounter = 0

   plotFraction = 0.23456
   maxPlotValue = 80000 / plotFraction
   plotValueLarge = int(maxPlotValue / 2)
   maxGaugeValue = 800 / plotFraction
   gaugeValueLarge = int(maxGaugeValue / 2)

   suiWindow.setValue("dynamicUserText", "<Enter> when done")

   imageForTableOrange = pygame.image.load("cell_orange.png")
   imageForTableSkyBlue = pygame.image.load("cell_blue.png")

   while runningFlag:
      if activeFlag:
         timeInMs = round(time.time() * 1000)

         suiWindow.setValue("bulbOn", True)

         plotValueLarge = random.randrange(
            max(int(-maxPlotValue*0.05), int(plotValueLarge - maxPlotValue*0.1)),
            min(int( maxPlotValue*1.10), int(plotValueLarge + maxPlotValue*0.1)))
         suiWindow.setAlert("plotData", plotValueLarge < 0 or plotValueLarge * plotFraction > 80000)
         suiWindow.setValue("plotData", plotValueLarge * plotFraction, timeInMs)

         gaugeValueLarge = random.randrange(
            max(int(-maxGaugeValue*0.2), int(gaugeValueLarge - maxGaugeValue*0.05)),
            min(int( maxGaugeValue*1.2), int(gaugeValueLarge + maxGaugeValue*0.05)))
         suiWindow.setValue("gaugeData", gaugeValueLarge * plotFraction, timeInMs)

         suiWindow.setValue("arcCount", arcCount, timeInMs)
         suiWindow.setAlert("arcCount", arcCount > 300)
         global imagePointerPositionIdx
         if arcCount == 0:
            imagePointerPositionIdx = 0
            suiWindow.setValue("image", "00114-483670603.png", timeInMs)
         elif arcCount == 180:
            imagePointerPositionIdx = 1
            suiWindow.setValue("image", "00096-3667449550.png", timeInMs)

         if arcCount >=   0 and arcCount <  30:
            suiWindow.setValue("text", "Orange")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Orange")
            suiWindow.setValue("boxTitle", "Dynamic Text")
         elif arcCount >=  30 and arcCount <  60:
            suiWindow.setValue("text", "Yellow")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Yellow")
            suiWindow.setValue("boxTitle", "Dynamic  Text")
         elif arcCount >=  60 and arcCount <  90:
            suiWindow.setValue("text", "Lime")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Lime")
            suiWindow.setValue("boxTitle", "Dynamic   Text")
         elif arcCount >=  90 and arcCount < 120:
            suiWindow.setValue("text", "Green")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Green")
            suiWindow.setValue("boxTitle", "Dynamic    Text")
         elif arcCount >= 120 and arcCount < 150:
            suiWindow.setValue("text", "Aquamarine")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Aquamarine")
            suiWindow.setValue("boxTitle", "Dynamic     Text")
         elif arcCount >= 150 and arcCount < 180:
            suiWindow.setValue("text", "Cyan")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Cyan")
            suiWindow.setValue("boxTitle", "Dynamic      Text")
         elif arcCount >= 180 and arcCount < 210:
            suiWindow.setValue("text", "Blue")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Blue")
            suiWindow.setValue("boxTitle", "Dynamic       Text")
         elif arcCount >= 210 and arcCount < 240:
            suiWindow.setValue("text", "Purple")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Purple")
            suiWindow.setValue("boxTitle", "Dynamic      Text")
         elif arcCount >= 240 and arcCount < 270:
            suiWindow.setValue("text", "Magenta")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Magenta")
            suiWindow.setValue("boxTitle", "Dynamic     Text")
         elif arcCount >= 270 and arcCount < 300:
            suiWindow.setValue("text", "Pink")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Pink")
            suiWindow.setValue("boxTitle", "Dynamic    Text")
         elif arcCount >= 300 and arcCount < 330:
            suiWindow.setValue("text", "Red")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: Red")
            suiWindow.setValue("boxTitle", "Dynamic   Text")
         elif arcCount >= 330 and arcCount < 360:
            suiWindow.setValue("text", "White")
            suiWindow.setValue("dynamicBulbTitle", "Dynamic Bulbs: White")
            suiWindow.setValue("boxTitle", "Dynamic  Text")

         suiWindow.setValue("ColorBulb", (arcCount, arcCount < 270))

         suiWindow.setValue("blink1",  arcCount >=   0 and arcCount <  30, timeInMs)
         suiWindow.setValue("blink2",  arcCount >=  30 and arcCount <  60, timeInMs)
         suiWindow.setValue("blink3",  arcCount >=  60 and arcCount <  90, timeInMs)
         suiWindow.setValue("blink4",  arcCount >=  90 and arcCount < 120, timeInMs)
         suiWindow.setValue("blink5",  arcCount >= 120 and arcCount < 150, timeInMs)
         suiWindow.setValue("blink6",  arcCount >= 150 and arcCount < 180, timeInMs)
         suiWindow.setValue("blink7",  arcCount >= 180 and arcCount < 210, timeInMs)
         suiWindow.setValue("blink8",  arcCount >= 210 and arcCount < 240, timeInMs)
         suiWindow.setValue("blink9",  arcCount >= 240 and arcCount < 270, timeInMs)
         suiWindow.setValue("blink10", arcCount >= 270 and arcCount < 300, timeInMs)
         suiWindow.setValue("blink11", arcCount >= 300 and arcCount < 330, timeInMs)
         suiWindow.setValue("blink12", arcCount >= 330 and arcCount < 360, timeInMs)

         for num in range(0, 13):
            currentValue = suiWindow.getValue(f"error{num}")
            if arcCount == num * 8 and currentValue == -1:
               currentValue = 0
            suiWindow.setValue(f"error{num}", currentValue)

         if (arcCount % 90) == 0:
            try:
               suiWindow.setTableData("DataTable", (imageForTableOrange, imageForTableSkyBlue)[(arcCount % 180) == 0], (TABLE_ROW_IMAGE_SURFACE, 1))
            except ValueError:
               pass

         try:
            suiWindow.setTableData("DataTable", sui_icons.icons[int(arcCount / 5)], (TABLE_ROW_IMAGE_ICON, 1))
         except ValueError:
            pass

         arcCount += 1
         if arcCount >= 360:
            arcCount = 0
            errorBulbCounter += 1

         try:
            suiWindow.setTableData("DataTable", suiWindow.getValue("text"), (TABLE_ROW_TEXT, 1))
            suiWindow.setTableData("DataTable", f'{suiWindow.getValue("arcCount")}\xB0', (TABLE_ROW_ARC, 1))
            suiWindow.setTableData("DataTable", suiWindow.getValue("plotData"), (TABLE_ROW_PLOT, 1))
            suiWindow.setTableData("DataTable", suiWindow.getValue("gaugeData"), (TABLE_ROW_GAUGE, 1))
            suiWindow.setTableData("DataTable", suiWindow.getValue("image"), (TABLE_ROW_IMAGE_FILENAME, 1))
         except ValueError:
            pass

      time.sleep(0.05)

if __name__ == '__main__':

   # You can control window element colors with the XML config file or any/all of these settings:
   #sui_colors.map["border.text"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["border.line"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["border.poly"] = pygame.colordict.THECOLORS["dodgerblue"]
   #sui_colors.map["border.circle"] = pygame.colordict.THECOLORS["green3"]
   #sui_colors.map["border.circle.fpsWarning"] = pygame.colordict.THECOLORS["yellow"]
   #sui_colors.map["border.circle.fpsError"] = pygame.colordict.THECOLORS["red"]
   #sui_colors.map["box.text"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["box.background"] = pygame.colordict.THECOLORS["gray93"]
   #sui_colors.map["box.border"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["box.bigFin"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["box.titleBlock"] = pygame.colordict.THECOLORS["gray73"]
   #sui_colors.map["box.smallFins"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["box.circle"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["box.zip"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["bulb.borderTop"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["bulb.borderBottom"] = pygame.colordict.THECOLORS["gray76"]
   #sui_colors.map["bulb.mouse"] = pygame.colordict.THECOLORS["blue"]
   #sui_colors.map["bulb.inactive"] = (pygame.colordict.THECOLORS["gray93"][0], pygame.colordict.THECOLORS["gray93"][1], pygame.colordict.THECOLORS["gray93"][2], 208)
   #sui_colors.map["bulb.inactiveOff"] = (0, 0, 0, 72)
   #sui_colors.map["button.text"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["button.line"] = pygame.colordict.THECOLORS["gray23"]
   #sui_colors.map["button.mouse"] = pygame.colordict.THECOLORS["orange"]
   #sui_colors.map["button.noFocus"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["clock.text"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["image.mouse"] = pygame.colordict.THECOLORS["orange"]
   #sui_colors.map["cplot.text"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["cplot.textRange"] = pygame.colordict.THECOLORS["red"]
   #sui_colors.map["cplot.arcRange"] = pygame.colordict.THECOLORS["red"]
   #sui_colors.map["cplot.arc"] = pygame.colordict.THECOLORS["blue"]
   #sui_colors.map["cplot.textInactive"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["cplot.arcInactive"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["gplot.warnTick"] = pygame.colordict.THECOLORS["red"]
   #sui_colors.map["gplot.tick"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["gplot.text"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["gplot.needle"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["gplot.textInactive"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["gplot.needleInactive"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["gplot.needleWarning"] = pygame.colordict.THECOLORS["orange"]
   #sui_colors.map["gplot.textWarning"] = pygame.colordict.THECOLORS["red"]
   #sui_colors.map["gplot.needleRange"] = pygame.colordict.THECOLORS["red"]
   #sui_colors.map["lplot.range"] = pygame.colordict.THECOLORS["red"]
   #sui_colors.map["lplot.foreground"] = pygame.colordict.THECOLORS["blue"]
   #sui_colors.map["lplot.background"] = pygame.colordict.THECOLORS["white"]
   #sui_colors.map["lplot.border"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["lplot.fgInactive"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["lplot.borderInactive"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["iplot.mask"] = (pygame.colordict.THECOLORS["gray93"][0], pygame.colordict.THECOLORS["gray93"][1], pygame.colordict.THECOLORS["gray93"][2], 192)
   #sui_colors.map["iplot.range"] = pygame.colordict.THECOLORS["white"]
   #sui_colors.map["iplot.borderInactive"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["xplot.background"] = pygame.colordict.THECOLORS["gray93"]
   #sui_colors.map["xplot.line"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["xplot.inactive"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["xplot.fill"] = pygame.colordict.THECOLORS["gray88"]
   #sui_colors.map["xplot.axis"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["table.text"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["table.grid"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["table.2row"] = pygame.colordict.THECOLORS["gray93"]
   #sui_colors.map["table.scrollBorder"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["table.scrollBar"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["text.text"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["value.name"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["value.value"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["value.inactive"] = pygame.colordict.THECOLORS["gray59"]
   #sui_colors.map["value.alert"] = pygame.colordict.THECOLORS["orange"]
   #sui_colors.map["value.focus"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["value.cursor"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["icon.icon"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["window.bg"] = pygame.colordict.THECOLORS["gray88"]
   #sui_colors.map["window.dot"] = pygame.colordict.THECOLORS["yellow"]
   #sui_colors.map["window.title"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["window.msgInfo"] = pygame.colordict.THECOLORS["black"]
   #sui_colors.map["window.msgError"] = pygame.colordict.THECOLORS["red"]

   callbackHandler = CallbackHandler()
   suiWindow = sui_window.sui_window("display_example_configuration.xml", callbackHandler)
   callbackHandler.suiWindow = suiWindow

   suiWindow.setTimeForAutomaticActivity(3.0)
   suiWindow.setTimeForAutomaticActivity(0.0, "dynamicUserText")

   suiWindow.insertTableRow("ElementTable", ("page",          "Multiple different screen layouts"))
   suiWindow.insertTableRow("ElementTable", ("clock",         "REPLACED"))  # Set down below
   suiWindow.setTableData  ("ElementTable",                   "24-hour clock in configurable TZ", (1, 1))
   suiWindow.insertTableRow("ElementTable", ("replaced",      "Replaced"))
   suiWindow.setTableData  ("ElementTable", ("box",           "Grouping of display elements"), 2)
   suiWindow.insertTableRow("ElementTable", ("image",         "RePlAcEd"))
   suiWindow.setTableData  ("ElementTable",                   "Static or dynamic image", [3, 1])
   suiWindow.insertTableRow("ElementTable", ("Deleted",       "DELETED Down Below"))
   suiWindow.insertTableRow("ElementTable", ["on-off-bulb",   "Dynamic on/off light bulb"])
   suiWindow.insertTableRow("ElementTable", ("color-bulb",    "Multi-color light bulb"))
   suiWindow.insertTableRow("ElementTable", ("error-bulb",    "Two-color error light bulb"))
   suiWindow.insertTableRow("ElementTable", ("xy-plot",       "X/Y (time-based) data plot"))
   suiWindow.insertTableRow("ElementTable", ("button",        "Application callback button"))
   suiWindow.insertTableRow("ElementTable", ("text-static",   "Just unchanging text"))
   suiWindow.insertTableRow("ElementTable", ("text-value",    "Dynamic data with name & units"))
   suiWindow.insertTableRow("ElementTable", ("gauge-plot",    "Dynamic data on a needle gauge"))
   suiWindow.insertTableRow("ElementTable", ("circular-plot", "Percent from min to max on circle"))
   suiWindow.insertTableRow("ElementTable", ("linear-plot",   "Percent from min to max on line"))
   suiWindow.insertTableRow("ElementTable", ("linear-image",  "Percent from min to max on image"))
   suiWindow.insertTableRow("ElementTable", ("table",         "Dynamic 2D table"))
   suiWindow.insertTableRow("ElementTable", ("Display Elements","Short Description"), 0)  # Insert at top
   suiWindow.removeTableRow("ElementTable", 5)

   suiWindow.insertTableRow("DataTable", ("Data", "Value"))
   TABLE_ROW_TEXT  = suiWindow.insertTableRow("DataTable", ("Color", ""))
   TABLE_ROW_ARC   = suiWindow.insertTableRow("DataTable", ("Angle", ""))
   TABLE_ROW_PLOT  = suiWindow.insertTableRow("DataTable", ("Plot Data", ""))
   TABLE_ROW_GAUGE = suiWindow.insertTableRow("DataTable", ("Gauge Data", ""))
   TABLE_ROW_IMAGE_FILENAME = suiWindow.insertTableRow("DataTable", ("Image Filename", ""))
   TABLE_ROW_IMAGE_SURFACE  = suiWindow.insertTableRow("DataTable", ("Image in Table", ""))
   TABLE_ROW_IMAGE_ICON     = suiWindow.insertTableRow("DataTable", ("Demo of icon", ""))
   suiWindow.insertTableRow("DataTable", ("Demo of boolean", True))
   suiWindow.insertTableRow("DataTable", ("Demo of integer", 1234))
   suiWindow.insertTableRow("DataTable", ("Demo of float", 12.34))
   suiWindow.insertTableRow("DataTable", ("Demo of tuple", (12, 34)))
   suiWindow.insertTableRow("DataTable", ("Demo of list", [12, 34]))
   suiWindow.insertTableRow("DataTable", ("Demo of set", {12, 34}))
   suiWindow.insertTableRow("DataTable", ("Demo of dict", {1: 2, 3: 4}))
   suiWindow.insertTableRow("DataTable", ("Demo of bytes", b"1234"))
   suiWindow.insertTableRow("DataTable", ("Demo of bytearray", bytearray(b"1234")))
   suiWindow.insertTableRow("DataTable", ("Demo of range", range(1, 4)))
   suiWindow.insertTableRow("DataTable", ("Demo of complex", complex(12, 34)))
   suiWindow.insertTableRow("DataTable", ("Demo of None", None))

   #for extra in range(1, 3000):
   #   suiWindow.insertTableRow("DataTable", ("Extra", extra))

   suiWindow.insertTableRow("IconTable", (" 0", sui_icons.icons[0], " 1", sui_icons.icons[1], " 2", sui_icons.icons[2], " 3", sui_icons.icons[3], " 4", sui_icons.icons[4], " 5", sui_icons.icons[5], " 6", sui_icons.icons[6], " 7", sui_icons.icons[7], " 8", sui_icons.icons[8], " 9", sui_icons.icons[9], "10", sui_icons.icons[10], "11", sui_icons.icons[11], "12", sui_icons.icons[12], "13", sui_icons.icons[13], "14", sui_icons.icons[14], "15", sui_icons.icons[15]))
   suiWindow.insertTableRow("IconTable", ("16", sui_icons.icons[16], "17", sui_icons.icons[17], "18", sui_icons.icons[18], "19", sui_icons.icons[19], "20", sui_icons.icons[20], "21", sui_icons.icons[21], "22", sui_icons.icons[22], "23", sui_icons.icons[23], "24", sui_icons.icons[24], "25", sui_icons.icons[25], "26", sui_icons.icons[26], "27", sui_icons.icons[27], "28", sui_icons.icons[28], "29", sui_icons.icons[29], "30", sui_icons.icons[30], "31", sui_icons.icons[31]))
   suiWindow.insertTableRow("IconTable", ("32", sui_icons.icons[32], "33", sui_icons.icons[33], "34", sui_icons.icons[34], "35", sui_icons.icons[35], "36", sui_icons.icons[36], "37", sui_icons.icons[37], "38", sui_icons.icons[38], "39", sui_icons.icons[39], "40", sui_icons.icons[40], "41", sui_icons.icons[41], "42", sui_icons.icons[42], "43", sui_icons.icons[43], "44", sui_icons.icons[44], "45", sui_icons.icons[45], "46", sui_icons.icons[46], "47", sui_icons.icons[47]))
   suiWindow.insertTableRow("IconTable", ("48", sui_icons.icons[48], "49", sui_icons.icons[49], "50", sui_icons.icons[50], "51", sui_icons.icons[51], "52", sui_icons.icons[52], "53", sui_icons.icons[53], "54", sui_icons.icons[54], "55", sui_icons.icons[55], "56", sui_icons.icons[56], "57", sui_icons.icons[57], "58", sui_icons.icons[58], "59", sui_icons.icons[59], "60", sui_icons.icons[60], "61", sui_icons.icons[61], "62", sui_icons.icons[62], "63", sui_icons.icons[63]))
   suiWindow.insertTableRow("IconTable", ("64", sui_icons.icons[64], "65", sui_icons.icons[65], "66", sui_icons.icons[66], "67", sui_icons.icons[67], "68", sui_icons.icons[68], "69", sui_icons.icons[69], "70", sui_icons.icons[70], "71", sui_icons.icons[71], "72", sui_icons.icons[72], "73", sui_icons.icons[73], "74", sui_icons.icons[74], "75", sui_icons.icons[75], "76", sui_icons.icons[76], "77", sui_icons.icons[77], "78", sui_icons.icons[78], "79", sui_icons.icons[79]))

   dataThread = threading.Thread(target=runDataThread, args=(suiWindow,))
   dataThread.start()

   suiWindow.loop(callbackHandler.onTerminate, callbackHandler.getOkayToTerminate, callbackHandler.onFrame)

   runningFlag = False
   dataThread.join()
