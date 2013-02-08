#!/usr/bin/env python3
import subprocess
import shlex

class Dialog:
	def mkDialog(self, command):
		proc = subprocess.Popen(command, stderr=subprocess.PIPE)
		outs, errs = proc.communicate()
		rc = proc.returncode
		return (rc, str(errs, "UTF-8"))


	def menu(self, title, items=[], height=15, width=54, menu_height=7, common="", debug=False):
		command = "dialog " + common +" --menu \"" + title + "\" " + str(height) + " " + str(width) + " " + str(menu_height)
		for k, v in items:
			command += " \"" + k + "\" \"" + v +"\""
		if debug:
			print(command)
		else:
			return(self.mkDialog(shlex.split(command)))
	
	def checklist(self, title, items=[], height=15, width=54, menu_height=7, common="", debug=False):
		command = "dialog " + common + " --checklist \"" + title + "\" " + str(height) + " " + str(width) + " " + str(menu_height)
		for tag, item, status in items:
			command += " \"" + tag + "\" \"" + item + "\" \"" + status +"\""
		if debug:
			print(command)
		else:
			return(self.mkDialog(shlex.split(command)))

