# -*- coding: ascii -*-
# $Id$
#
# Author: charles@polymorphic-solutions.com
# Date: 11-April-2020

from __future__ import absolute_import
from __future__ import print_function
__author__ = "Charles Morgan"
__email__  = "charles@polymorphic-solutions.com"

import sys
# import time
import math

try:
	from Tkinter import *
	import tkMessageBox
except ImportError:
	from tkinter import *
	import tkinter.messagebox as tkMessageBox

from CNC import CNC, Block
import Utils
import Ribbon
import tkExtra
import CNCRibbon

try:
	from serial.tools.list_ports import comports
except:
	print("Using fallback Utils.comports()!")
	from Utils import comports

BAUDS = [2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400]


#===============================================================================
# Connection Group
#===============================================================================
class IOExpanderGroup(CNCRibbon.ButtonGroup):
	def __init__(self, master, app):
		CNCRibbon.ButtonGroup.__init__(self, master, N_("IOExpander"), app)

		self.tab = StringVar()
		# ---
		col,row=0,0
		b = Ribbon.LabelRadiobutton(self.frame,
				image=Utils.icons["serial48"],
				text=_("Connection"),
				compound=TOP,
				variable=self.tab,
				value="Connection",
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=5, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Configure connection for the IO Expander"))

		# ---
		row += 1
		b = Ribbon.LabelRadiobutton(self.frame,
				image=Utils.icons["reset"],
				text=_("Reset"),
				compound=TOP,
				variable=self.tab,
				value="Reset",
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=5, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Reset the IO Expander"))

		# ---
		col += 1
		row = 0
		b = Ribbon.LabelRadiobutton(self.frame,
				image=Utils.icons["config32"],
				text=_("Configure"),
				compound=TOP,
				variable=self.tab,
				value="Configure",
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=5, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Configure the IO Expander"))

		# ---
		col += 1
		b = Ribbon.LabelRadiobutton(self.frame,
				image=Utils.icons["stats"],
				text=_("Monitor"),
				compound=TOP,
				variable=self.tab,
				value="Monitor",
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=5, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Monitor the IO Expander"))

		# ---
		col += 1
		b = Ribbon.LabelRadiobutton(self.frame,
				image=Utils.icons["target32"],
				text=_("Test"),
				compound=TOP,
				variable=self.tab,
				value="Test",
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=5, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Test configuration of the IO Expander"))

		self.frame.grid_rowconfigure(0, weight=1)


#===============================================================================
# Configuration Group
#===============================================================================
class IOEConfigurationGroup(CNCRibbon.ButtonGroup):
	def __init__(self, master, app):
		CNCRibbon.ButtonGroup.__init__(self, master, "IOExpander:Config", app)
		self.label["background"] = Ribbon._BACKGROUND_GROUP2
		self.grid3rows()

		# ---
		col,row=0,0
		b = Ribbon.LabelButton(self.frame, self, "T-Probes",
				image=Utils.icons["optimize"],
				text=_("T-Probes"),
				compound=LEFT,
				anchor=W,
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=0, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Configure the Temperature Probes"))
		self.addWidget(b)

		# ---
		row += 1
		b = Ribbon.LabelButton(self.frame, self, "Relays",
				image=Utils.icons["rc"],
				text=_("Relays"),
				compound=LEFT,
				anchor=W,
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=0, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Configure the relays"))
		self.addWidget(b)

		# ---
		row += 1
		b = Ribbon.LabelButton(self.frame, self, "P-Sensors",
				image=Utils.icons["measure"],
				text=_("P-Sensors"),
				compound=LEFT,
				anchor=W,
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=0, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Configure the Pressure Sensors"))
		self.addWidget(b)

		# ---
		row = 0
		col += 1
		b = Ribbon.LabelButton(self.frame, self, "Lvl-Sensors",
				image=Utils.icons["level"],
				text=_("Lvl-Sensors"),
				compound=LEFT,
				anchor=W,
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=0, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Configure the Level Sensors"))
		self.addWidget(b)

		# ---
		row = 0
		col += 1
		b = Ribbon.LabelButton(self.frame, self, "RTC",
				image=Utils.icons["level"],
				text=_("RTC"),
				compound=LEFT,
				anchor=W,
				background=Ribbon._BACKGROUND)
		b.grid(row=row, column=col, padx=0, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(b, _("Configure the Realtime Clock"))
		self.addWidget(b)


#===============================================================================
# IOExpander Frame
#===============================================================================
class IOExpanderFrame(CNCRibbon.PageFrame):
	def __init__(self, master, app):
		CNCRibbon.PageLabelFrame.__init__(self, master, "IOESerial", _("IOESerial"), app)
		self.autostart = BooleanVar()

		# ---
		col, row = 0, 0
		b = Label(self, text=_("Port:"))
		b.grid(row=row, column=col, sticky=E)
		self.addWidget(b)

		self.portCombo = tkExtra.Combobox(self, False, background=tkExtra.GLOBAL_CONTROL_BACKGROUND, width=16, command=self.comportClean)
		self.portCombo.grid(row=row, column=col + 1, sticky=EW)
		tkExtra.Balloon.set(self.portCombo, _("Select (or manual enter) port to connect"))
		self.portCombo.set(Utils.getStr("Connection", "port"))
		self.addWidget(self.portCombo)

		self.comportRefresh()

		# ---
		row += 1
		b = Label(self, text=_("Baud:"))
		b.grid(row=row, column=col, sticky=E)

		self.baudCombo = tkExtra.Combobox(self, True, background=tkExtra.GLOBAL_CONTROL_BACKGROUND)
		self.baudCombo.grid(row=row, column=col + 1, sticky=EW)
		tkExtra.Balloon.set(self.baudCombo, _("Select connection baud rate"))
		self.baudCombo.fill(BAUDS)
		self.baudCombo.set(Utils.getStr("Connection", "baud", "115200"))
		self.addWidget(self.baudCombo)

		# ---
		row += 1
		b = Label(self, text=_("Controller:"))
		b.grid(row=row, column=col, sticky=E)

		self.ctrlCombo = tkExtra.Combobox(self, True, background=tkExtra.GLOBAL_CONTROL_BACKGROUND, command=self.ctrlChange)
		self.ctrlCombo.grid(row=row, column=col + 1, sticky=EW)
		tkExtra.Balloon.set(self.ctrlCombo, _("Select controller board"))
		# self.ctrlCombo.fill(sorted(Utils.CONTROLLER.keys()))
		self.ctrlCombo.fill(self.app.controllerList())
		self.ctrlCombo.set(app.controller)
		self.addWidget(self.ctrlCombo)

		# ---
		row += 1
		b = Checkbutton(self, text=_("Connect on startup"),
						variable=self.autostart)
		b.grid(row=row, column=col, columnspan=2, sticky=W)
		tkExtra.Balloon.set(b, _("Connect to serial on startup of the program"))
		self.autostart.set(Utils.getBool("Connection", "openserial"))
		self.addWidget(b)

		# ---
		col += 2
		self.comrefBtn = Ribbon.LabelButton(self,
											image=Utils.icons["refresh"],
											text=_("Refresh"),
											compound=TOP,
											command=lambda s=self: s.comportRefresh(True),
											background=Ribbon._BACKGROUND)
		self.comrefBtn.grid(row=row, column=col, padx=0, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(self.comrefBtn, _("Refresh list of serial ports"))

		# ---
		# col += 2
		row = 0

		self.connectBtn = Ribbon.LabelButton(self,
											 image=Utils.icons["serial48"],
											 text=_("Open"),
											 compound=TOP,
											 command=lambda s=self: s.event_generate("<<Connect>>"),
											 background=Ribbon._BACKGROUND)
		self.connectBtn.grid(row=row, column=col, rowspan=3, padx=0, pady=0, sticky=NSEW)
		tkExtra.Balloon.set(self.connectBtn, _("Open/Close serial port"))
		self.grid_columnconfigure(1, weight=1)

	#-----------------------------------------------------------------------
	def ctrlChange(self):
		self.app.controllerSet(self.ctrlCombo.get())

	#-----------------------------------------------------------------------
	def comportClean(self, event=None):
		clean = self.portCombo.get().split("\t")[0]
		if(self.portCombo.get() != clean):
			print("comport fix")
			self.portCombo.set(clean)

	#-----------------------------------------------------------------------
	def comportsGet(self):
		try:
			return comports(include_links=True)
		except TypeError:
			print("Using old style comports()!")
			return comports()

	def comportRefresh(self, dbg=False):
		#Detect devices
		hwgrep = []
		for i in self.comportsGet():
			if dbg:
				#Print list to console if requested
				comport = ''
				for j in i: comport+=j+"\t"
				print(comport)
			for hw in i[2].split(' '):
				hwgrep += ["hwgrep://"+hw+"\t"+i[1]]

		#Populate combobox
		devices = sorted([x[0]+"\t"+x[1] for x in self.comportsGet()])
		devices += ['']
		devices += sorted(set(hwgrep))
		devices += ['']
		if sys.version_info[0] != 3: #Pyserial raw spy currently broken in python3
			devices += sorted(["spy://"+x[0]+"?raw&color"+"\t(Debug) "+x[1] for x in self.comportsGet()])
		else:
			devices += sorted(["spy://"+x[0]+"?color"+"\t(Debug) "+x[1] for x in self.comportsGet()])
		devices += ['', 'socket://localhost:23', 'rfc2217://localhost:2217']

		#Clean neighbour duplicates
		devices_clean = []
		devprev = '';
		for i in devices:
			if i.split("\t")[0] != devprev: devices_clean += [i]
			devprev = i.split("\t")[0]

		self.portCombo.fill(devices_clean)

	#-----------------------------------------------------------------------
	def saveConfig(self):
		# Connection
		Utils.setStr("IOEConnection", "controller",  self.app.controller)
		Utils.setStr("IOEConnection", "port",        self.portCombo.get().split("\t")[0])
		Utils.setStr("IOEConnection", "baud",        self.baudCombo.get())
		Utils.setBool("IOEConnection", "openserial", self.autostart.get())

#===============================================================================
# IO Expander Page
#===============================================================================
class IOExpanderPage(CNCRibbon.Page):
	__doc__ = _("IO Expander and configuration")
	_name_  = "IOExpander"
	_icon_  = "gantry"

	#----------------------------------------------------------------------
	# Add a widget in the widgets list to enable disable during the run
	#----------------------------------------------------------------------
	def register(self):
		self._register((IOExpanderGroup, IOEConfigurationGroup), (IOExpanderFrame,))
		self.tabGroup = CNCRibbon.Page.groups["IOExpander"]
		self.tabGroup.tab.set("IOExpander")
		self.tabGroup.tab.trace('w', self.tabChange)

	#-----------------------------------------------------------------------
	def tabChange(self, a=None, b=None, c=None):
		tab = self.tabGroup.tab.get()
		self.master._forgetPage()

		# remove all page tabs with ":" and add the new ones
		self.ribbons = [ x for x in self.ribbons if ":" not in x[0].name ]
		self.frames  = [ x for x in self.frames  if ":" not in x[0].name ]

		try:
			self.addRibbonGroup("Probe:%s"%(tab))
		except KeyError:
			pass
		try:
			self.addPageFrame("Probe:%s"%(tab))
		except KeyError:
			pass

		self.master.changePage(self)
