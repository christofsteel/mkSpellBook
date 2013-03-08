#!/usr/bin/env python3
import subprocess
import tempfile
import shlex
import os

class NotYetCreatedError(Exception):
	pass

class Gauge:
	def __init__(self, text="", percentage=0, height=7, width=80, common="", debug=False):
		self.text = text
		self.height = height
		self.width = width
		self.common = common
		self.debug = debug
		self.percentage = percentage
		self.gauge = None

	def show(self):
		command = shlex.split("dialog " + self.common + "--gauge \"" + self.text + "\" " + str(self.height) + " " + str(self.width))
		if self.debug:
			print(command)
		self.gauge = subprocess.Popen(command, stdin=subprocess.PIPE) #, stdout=subprocess.STDOUT, stderr=subprocess.PIPE)
	
	def update(self, percentage, text=None):
		if self.gauge == None:
			raise NotYetCreatedError
		if not text == None:
			self.text = text
		command = "\nXXX\n"+str(percentage)+"\n"+self.text+"\n"+"XXX\n" 
		if self.debug:
			print(command)
		self.gauge.stdin.write(bytes(command, "UTF-8"))
		self.gauge.stdin.flush()

	def close(self):
		if self.gauge == None:
			raise NotYetCreatedError
		self.gauge.stdin.close()
		

class Dialog:
	def __init__(self):
		self.height = 15
		self.width = 50
		self.menu_height = 10
		self.common = ""
		self.debug = False

	def mkDialog(self, command):
		proc = subprocess.Popen(command, stderr=subprocess.PIPE)
		outs, errs = proc.communicate()
		rc = proc.returncode
		return (rc, str(errs, "UTF-8"))

	def setParam(self, height=None, width=None, menu_height=None, common="", debug=False):
		self.height         = height
		self.width          = width
		self.menu_height    = menu_height
		self.common         = common
		self.debug          = debug
	
	def fselect(self, text, startpath, height=25, width=80, debug=None):
		startpath = os.path.abspath(startpath) + "/"
		command = "dialog --title \"" + text + "\" --fselect \"" + startpath + "\" " + str(height) + " " + str(width)
		drc, file = self.mkDialog(shlex.split(command))
		if file:
			if os.path.isdir(file):
				return self.fselect(text, file, height, width, debug)
			else:
				return (drc, file)
		else:
			return (drc, None)

	def msgbox(self, text, height=10, width=50, common=None, debug=None):
		command = "dialog " + (common or self.common) + " --msgbox \"" + text + "\" " + str(height) + " " + str(width)
		if (debug != None and debug) or self.debug:
			print(command)
		else:
			return(self.mkDialog(shlex.split(command)))
	def editbox(self, height=50, width=80):
		with tempfile.NamedTemporaryFile(mode='r+') as f:
			command = "dialog --editbox " + f.name + " " + str(height) + " " + str(width)
			erc, ech = self.mkDialog(shlex.split(command))
		return ((erc, ech))

		

	def yesno(self, text, height=10, width=50, common=None, debug=None):
		command = "dialog " + (common or self.common) + " --yesno \"" + text + "\" " + str(height) + " " + str(width)
		if (debug != None and debug) or self.debug:
			print(command)
		else:
			return(self.mkDialog(shlex.split(command)))
	
	def form(self, text, height=40, width=80, common=None, fields=None, debug=False):
		labelwidth = max([len(item[0]) for item in fields]) + 8
		command_fields = []
		for i in range(1, len(fields) + 1):
			command_fields.append("\"" + fields[i-1][0] + "\" " + str(i*2) + " 4 \"" + fields[i-1][1] + "\" " + str(i*2) + " " + str(labelwidth) + " " + str(fields[i-1][2]) + " 255")
		command = "dialog "+ (common or self.common) + " --form \"" + text + "\" " + str(height) + " " + str(width) + " " + str(height) + " " + " ".join(command_fields)
		if (debug != None and debug) or self.debug:
			print(command)
		else:
			return(self.mkDialog(shlex.split(command)))

	def menu(self, title, items=[], height=None, width=None, menu_height=None, common=None, debug=None):
		command = "dialog " + (common or self.common) +" --menu \"" + (title or self.title) + "\" " + str(height or self.height) + " " + str(width or self.width) + " " + str(menu_height or self.menu_height)
		for k, v in items:
			command += " \"" + str(k) + "\" \"" + str(v) +"\""
		if (debug != None and debug) or self.debug:
			print(command)
		else:
			return(self.mkDialog(shlex.split(command)))

	def inputbox(self, text, height=10, width=50, init=None, common=None, debug=None):
		command = "dialog " + (common or self.common) + " --inputbox \"" + text + "\" " + str(height) + " " + str(width) + (" \"" + init + "\"" if init else "")
		if (debug != None and debug) or self.debug:
			print(command)
		else:
			return(self.mkDialog(shlex.split(command)))

	def checklist(self, title, items=[], height=None, width=None, menu_height=None, common=None, debug=None):
		command = "dialog " + (common or self.common) + " --checklist \"" + (title or self.title) + "\" " + str(height or self.height) + " " + str(width or self.width) + " " + str(menu_height or self.menu_height)
		for tag, item, status in items:
			command += " \"" + tag + "\" \"" + item + "\" \"" + status +"\""
		if (debug != None and debug) or self.debug:
			print(command)
		else:
			return(self.mkDialog(shlex.split(command)))

