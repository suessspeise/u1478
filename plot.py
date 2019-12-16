
"""@package U1478_html_generator
Documentation for this module.
 
More details.
"""

#### LIBRARIES ####
# calculating
import pandas as pd
import numpy as np
from scipy.stats import linregress
import math

# plotting
import matplotlib.pyplot as plt; plt.rcdefaults()
cmap = plt.cm.viridis
import matplotlib.ticker as plticker

# system level
from os import listdir
from os.path import isfile, join
import sys
import datetime
import subprocess # to invoke bash processes


#### TODO ####
### maybe rename : dataset 
# (make a more general container, and a container for data subsets, 
#  also pollenidentdata has to be loaded)

#  container div: https://stackoverflow.com/questions/354739/why-should-i-use-a-container-div-in-html
#	but there already is a container div for the pollen images page. 
#	this has to be separated first.

#  syntax checking? https://stackoverflow.com/questions/35538/validate-xhtml-in-python

# elemente einrücken in (element in Html class)

# generate class diagram from python code:

# menage image width in css?

# event plot has empty points


class FolderStructure:
	'''folder structure storage class 

	This class stores information on the folder structure used in other classes 
	'''
	def __init__(self, base=False):
		''' constructor
		
		@parameter base Base path, setting all values to default if none (or False) is given
		'''
		if base == False:
			self.setdefault()
		else:
			self.base = base

	def __str__(self):
		''' string

		@return short description of the object containing path to used csv table and dimensions of the dataset
		'''
		return 'filestructure (base path="' + self.base + '")' 

	def set(self, attribute, value=False):
		# allow to feed tuple instead of two separate variables
		# length of tuple is not checked!
		if type(attribute) == tuple:
			value     = attribute[1]
			attribute = attribute[0]
		if value == False:
			print("error: no value given")
			return "error: no value given"
		else:
			setattr(self, attribute, value)

	def get(self, attribute):
		return self.base + "/" + getattr(self, attribute)

	def setdefault(self):
		defaults = [
			("base", ".."),
			("html", "html"),
			("script", "script"),
			("img", "img"),
			("plot", "img/plot"),
			("protocol", "protocol"),
			("data", "data"),
			("agedata", "data/age_data"),
			("pollendata", "data/pollen"),
			("agemodeldata", "data/agemodel")
			]
		for d in defaults:
			self.set(d)


class Container:
	'''Container for dataframe. 

	This class manages access to a dataframe and brings along tools to acess columns of the data frame in ways, that are useful e.g. for plotting.
	'''
	default_dataset = "../data/pollen/U1478.csv"
	ages = "Age [Ma]"

	def __init__(self, filename="", agestring=''):
		''' constructor
		
		@parameter filename Path to the csv to be loaded as pandas dataframe. if nothing specified the class specific default_dataset will be used.
		@parameter agestring Name of the column containing Age information. As everything is plotted over time this column has special significance.
		'''
		if filename == "":
			self.filename = self.default_dataset
		else:
			self.filename = filename
		if not agestring == "":
			self.ages = agestring
		self.reload_table()
		self.label = self.labels()

	def __str__(self):
		''' string

		@return short description of the object containing path to used csv table and dimensions of the dataset
		'''
		return "Container for " + self.filename + " " + str(self.d.shape)
	
	def reload_table(self):
		''' load table
		
		loads (when called from the constructor) or reloads a table as pandas dataframe into Container.
		'''
		self.d = pd.read_table(self.filename, sep=',')
		return 0
	
	def set_ages(agestring):
		''' set ages

		resets the object variable, declaring the name of the column containing age data. 
		As everything is plotted over time this column has special significance.

		@parameter agestring name of the column containing age information. 
		'''
		if type(agestring) == 'str':
			self.ages = agestring
			return 0
		else:
			print("error: argument must be a string!")
			return 1

	def labels(self):
		''' get labels

		@return labels (or headers, or columnnames) of the contained pandas dataframe
		'''
		return list(self.d.columns.values)

	def get(self, label="", modus="absolute"):
		""" get column

		This function takes a column with the label ("label") out of a pandas data frame ("df"), 
		removes values == 0 and returns the shortened list. The SUM column of the data frame is 
		used as a reference point for diferenciating between zero findings and empty values.

		@parameter label The label of the column to be chosen. If none is specified, the whole datafram is returned
		@parameter modus The way the column is returned. This can be absolute values ("absolute", default), boolean values ("boolian"), relative values ("relative"), values converted to string ("string") timeseries ("timeseries") or single events without points containing zeros ("event").
		"""
		def absolute():
			"""
			@return list containing a column from the dataframe.
			"""
			x = list(self.d[label])
			boolx = list(self.d["SUM"])
			for i in range(len(x)):
				if boolx[i] > 0:
					if type(x[i]) == type("string"): # if table uses comma as decimal seperator
						x[i] = float(x[i].replace(',','.'))
					if x[i] == 0:
						x[i] = None
			return x
		def boolian():
			"""
			@return list containg information about where non zero values are False, values containing information are True
			"""
			x = list(self.d[label])
			for i in range(len(x)):
				if type(x[i]) == type("string"): # if table uses comma as decimal seperator
					x[i] = float(x[i].replace(',','.'))
				if x[i] > 0:
					x[i] = True
				else:
					x[i] = False
			return x
		def relative():
			"""
			@return like absolute, but divided by column "SUM"
			"""
			x = self.get(label)
			m = self.get(label, "boolian")
			s = self.get("SUM")
			for i in range(len(m)):
				if m[i]:
					x[i] = x[i] / s[i]
			return x

		def string():
			"""
			takes column of df and erases empty values

			[not valid description] Does the same as load(df, label), without relying on the column labeled "SUM", thus not differing 
			between zero values and empty values
			
			Args:
				df:	A pandas dataframe
				label:	The label of the column, that should be extracted
			
			"""
			x = list(self.d[label])
			y = []
			for i in range(len(x)):
				y.append(str(x[i]))
			return y

		# loads two equally long lists with pollen data and ages
		# @return tuple containing (age, pollendata)
		def timeseries():
			y = self.get(label, "relative")
			x = self.get(self.ages)
			m = self.get(label, "bool")
			xx = [] 
			yy = []
			for i in range(len(m)):
				if m[i]:
					xx.append(x[i])
					yy.append(y[i])
			return xx, yy

		# returns list of ages with non zero values (for matplotlib.eventplot() )
		def event():
			x = self.get(label, "bool")
			y = self.getage()
			export = []
			for i in range(len(x)):
				if x[i]:
					export.append(y[i])
			return export

		# case statement (kind of) to choose opearational modus
		if label == "": #  in case no label is given, give whole dataset.
			return self.d
		elif modus == "absolute"    or modus == "abs"  or modus == "a":
			return absolute() 
		elif modus == "boolian"     or modus == "bool" or modus == "b":
			return boolian()
		elif modus == "relative"    or modus == "rel"  or modus == "r":
			return relative()
		elif modus == "string"      or modus == "str"  or modus == "s":
			return string()
		elif modus == "timeseries"  or modus == "time" or modus == "t":
			return timeseries()
		elif modus == "event"       or modus == "e":
			return event()
		else:
			print("Container Error, get: unknown modus.")
			return None

	def getage(self):
		return self.get(self.ages)




	@staticmethod
	def printpair(pair):
		"""
		print plotable pair of arrays to terminal

		This function prints two plotable (i.e. numerical arrays of the same length) 
		into standard output. Used for debugging purposes

		Args:
			pair:	A tuple of two lists or arrays 

		"""
		x, y = pair
		string = ""
		for i in range(len(x)):
			string += str(x[i])[0:5] + "\t"
			if type(y[i]) == float: 
				string += str(round(y[i], 3)) + "\n"
			else:
				string += str(y[i]) + "\n"
		return string

	@staticmethod
	def removezeros(x,y):
		# remove emptys (for example for the counting summary scatterplot)
		xx, yy = [], []
		for i in range(len(x)):
			if y[i] != 0.0 and y[i] != float('NaN'): # not math.isnan(y[i]):
				xx.append(x[i])
				yy.append(y[i])
		return xx, yy



	def getrow(self, sampleID, clean=False):
		# def relevant(item):
		# 	if (item == 0) or (pd.isnull(item)):
		# 		return False
		# 	else:
		# 		return True
		# def clean(data):
		# 	for item in data:
		# 		if not relevant:
		# 			data.drop["HOLE"]

		for index, row in self.d.iterrows():
			rowID = (row["HOLE"] + row["CORE"] + row["SECT"] + str(int(row["bottom depth in core [cm]"]))).lower()
			if rowID == sampleID: 	
				if clean:
					return row
				else:
					return row


class Html:
	def __init__(self, title = ""):
		self.content = []
		self.addasciiart()
		self.title = " - " + title

	def __str__(self):
		return "hmtl object, " + str(len(self.content)) + " elements in body"

	def generate(self):
		# return "HTML class (provides building blocks for html pages)"
		html  = '<!DOCTYPE html>\n<html>\n'
		html += self.head()
		html += '<body>\n\n'
		for element in self.content:
			html += '' + element + '\n' 
			# html += '' + element.replace('\n','\n\t') + '\n' 
		html += self.foot()
		html += '\n</body>\n</html>'
		return html

	def tofile(self, filename):
		print(self.generate(), file=open(filename, 'w') )
		return 0

	def add(self, element):
		self.content.append(element)
		return 0

	def head(self, 
			 icon="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/233/owl_1f989.png", 
			 stylesheet="https://uni.camposcampos.de/u1478/html/main.css"):
		html  = '<head>\n'
		html += '\t<!-- auto generated webpage -->\n'
		html += '\t<!-- all robots are welcome -->\n'
		html += '\t<meta charset="UTF-8">\n'
		html += '\t<title>U1478' + self.title + '</title>\n'
		html += '\t<link rel="shortcut icon" href="' + icon + '" type="image/vnd.microsoft.icon">\n'
		html += '\t<link rel="stylesheet" type="text/css" href="' + stylesheet + '">\n'
		html += '</head>\n'
		return html

	@staticmethod
	def foot(content='<a href="http://uni.camposcampos.de" target="_blank">uni.camposcampos.de &#x1F989 </a>'):
		html =  '\t<footer style="position:fixed; font-size:.8em; text-align:right; bottom:3px; right: 5px; height:20px; width:100%;">\n'
		html += '\t\t' + content + '\n'
		html += '\t</footer>\n'
		# html += '\t</body>\n'
		# html += '</html>\n'
		return html

	@staticmethod
	def image(path, width=800):
		path = str(path)
		html = '<img src="' + path + '" alt="' + path + '" width="' + str(width) + 'px" max-width="90%">\n'
		return html

	@staticmethod
	def image(path, text="", width=800):
		path = str(path)
		if text == "":
			html = '<img src="' + path + '" alt="' + path + '" width="' + str(width) + 'px" max-width="90%">\n'
		else:
			html  = '<div class="overlayimage">\n'
			html += '\t<img src="' + path  + '">\n'
			html += '\t<div class="top-left">' + text + '</div>\n'
			html += '</div>'
		return html

	@staticmethod
	def paragraph(text):
		text = str(text)
		html = '<p>' + text + '</p>'
		return html

	@staticmethod
	def link(text, location=""):
		if location == "":
			location = text
		text = str(text)
		location = str(location)
		html = '<a href="' + location + '">' + text + '</a>'
		return html

	@staticmethod
	def comment(text):
		html = '<!-- ' + str(text) + ' -->'
		return html

	@staticmethod
	def headline(text, weight=3):
		html = '<h' + str(weight) + '>' + str(text) + '</h' + str(weight) + '>'
		return html

	@staticmethod
	def unorderedlist(items):
		html  = '<ul>\n'
		for item in items:
			html += '\t<li>' + str(item) + '</li>\n'	
		html += '</ul>\n'
		return html

	@staticmethod
	def table(columns, labels=False):
		html  = '<table   class="dataframe">\n'
		if labels:
			html += "\t<thead>\n"
			html += '\t\t<tr style="text-align: right;">\n'
			for label in labels: 
				html += "\t\t\t<th>" + str(label) + "</th>\n"
			html += '\t\t</tr>\n'
			html += "\t</thead>\n"
		html += "\t<tbody>\n"
		for i, v in enumerate(columns[0]):
			html += '\t\t<tr>\n'
			for c in columns:
				html += '\t\t\t<td>' + str(c[i]) + '</td>\n'
			html += '\t\t</tr>\n'
		html += "\t</tbody>\n"
		html += "</table>\n\n"
		return html

	@staticmethod
	def asciiart(font=3):
		# generated at http://patorjk.com/software/taag/#p=testall&f=Doom&t=U1478
		#
		# these are also very nice: 
		#	 https://onlineasciitools.com/convert-text-to-ascii-art
		
		ascistring = ""
		if font == 1:
			# font: Slant Relief
			ascii01  = '__/\\\\\\________/\\\\\\______/\\\\\\____________/\\\\\\_____/\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\_____/\\\\\\\\\\\\\\\\\\____        \n'
			ascii01 += ' _\\/\\\\\\_______\\/\\\\\\__/\\\\\\\\\\\\\\__________/\\\\\\\\\\____\\/////////////\\\\\\___/\\\\\\///////\\\\\\__       \n'
			ascii01 += '  _\\/\\\\\\_______\\/\\\\\\_\\/////\\\\\\________/\\\\\\/\\\\\\_______________/\\\\\\/___\\/\\\\\\_____\\/\\\\\\__      \n'
			ascii01 += '   _\\/\\\\\\_______\\/\\\\\\_____\\/\\\\\\______/\\\\\\/\\/\\\\\\_____________/\\\\\\/_____\\///\\\\\\\\\\\\\\\\\\/___     \n'
			ascii01 += '    _\\/\\\\\\_______\\/\\\\\\_____\\/\\\\\\____/\\\\\\/__\\/\\\\\\___________/\\\\\\/________/\\\\\\///////\\\\\\__    \n'
			ascii01 += '     _\\/\\\\\\_______\\/\\\\\\_____\\/\\\\\\__/\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\______/\\\\\\/_________/\\\\\\______\\//\\\\\\_   \n'
			ascii01 += '      _\\//\\\\\\______/\\\\\\______\\/\\\\\\_\\///////////\\\\\\//_____/\\\\\\/__________\\//\\\\\\______/\\\\\\__  \n'
			ascii01 += '       __\\///\\\\\\\\\\\\\\\\\\/_______\\/\\\\\\___________\\/\\\\\\_____/\\\\\\/_____________\\///\\\\\\\\\\\\\\\\\\/___ \n'
			ascii01 += '        ____\\/////////_________\\///____________\\///_____\\///_________________\\/////////_____\n'
			ascistring = ascii01
		elif font == 2:
			# font:  Larry 3D
			ascii02  = ' __  __     _  __ __     ________    __     \n'
			ascii02 += '/\\ \\/\\ \\  /\' \\/\\ \\\\ \\   /\\_____  \\ /\'_ `\\   \n'
			ascii02 += '\\ \\ \\ \\ \\/\\_, \\ \\ \\\\ \\  \\/___//\'/\'/\\ \\L\\ \\  \n'
			ascii02 += ' \\ \\ \\ \\ \\/_/\\ \\ \\ \\\\ \\_    /\' /\' \\/_> _ <_ \n'
			ascii02 += '  \\ \\ \\_\\ \\ \\ \\ \\ \\__ ,__\\/\' /\'     /\\ \\L\\ \\\n'
			ascii02 += '   \\ \\_____\\ \\ \\_\\/_/\\_\\_/\\_/       \\ \\____/\n'
			ascii02 +=  '    \\/_____/  \\/_/  \\/_/ \\//         \\/___/ \\n'
			ascistring = ascii02
		elif font == 3:
			# font: Big Money-sw
			ascii03  = ' __    __    __  __    __  ________  ______  \n'
			ascii03 += '/  |  /  | _/  |/  |  /  |/        |/      \\ \n'
			ascii03 += '$$ |  $$ |/ $$ |$$ |  $$ |$$$$$$$$//$$$$$$  |\n'
			ascii03 += '$$ |  $$ |$$$$ |$$ |__$$ |    /$$/ $$ \\__$$ |\n'
			ascii03 += '$$ |  $$ |  $$ |$$    $$ |   /$$/  $$    $$< \n'
			ascii03 += '$$ |  $$ |  $$ |$$$$$$$$ |  /$$/    $$$$$$  |\n'
			ascii03 += '$$ \\__$$ | _$$ |_     $$ | /$$/    $$ \\__$$ |\n'
			ascii03 += '$$    $$/ / $$   |    $$ |/$$/     $$    $$/ \n'
			ascii03 += ' $$$$$$/  $$$$$$/     $$/ $$/       $$$$$$/  \n'
			ascistring = ascii03
		elif font == 4:
			# font: Slant	
			ascii04  = '   __  _______ ___________ \n'
			ascii04 += '  / / / <  / // /__  ( __ )\n'
			ascii04 += ' / / / // / // /_ / / __  |\n'
			ascii04 += '/ /_/ // /__  __// / /_/ / \n'
			ascii04 += '\\____//_/  /_/  /_/\\____/  \n'
			ascistring = ascii04
		elif font == 5:
			# font: Big
			ascii05  = '  _    _ __ _  _ ______ ___  \n'
			ascii05 += ' | |  | /_ | || |____  / _ \\ \n'
			ascii05 += ' | |  | || | || |_  / / (_) |\n'
			ascii05 += ' | |  | || |__   _|/ / > _ < \n'
			ascii05 += ' | |__| || |  | | / / | (_) |\n'
			ascii05 += '  \\____/ |_|  |_|/_/   \\___/ \n'
			ascistring = ascii05
		elif font == 6:
			# alligator2 (onlineasciitools)
			ascii06  = ':::    :::   :::     ::: :::::::::::  ::::::::  \n'
			ascii06 += ':+:    :+: :+:+:    :+:  :+:     :+: :+:    :+: \n'
			ascii06 += '+:+    +:+   +:+   +:+ +:+      +:+  +:+    +:+ \n'
			ascii06 += '+\#+    +:+   +\#+  +\#+  +:+     +\#+    +\#++:++\#  \n'
			ascii06 += '+\#+    +\#+   +\#+ +\#+\#+\#+\#+\#+  +\#+    +\#+    +\#+ \n'
			ascii06 += '\#+\#    \#+\#   \#+\#       \#+\#   \#+\#     \#+\#    \#+\# \n'
			ascii06 += ' \#\#\#\#\#\#\#\#  \#\#\#\#\#\#\#     \#\#\#   \#\#\#      \#\#\#\#\#\#\#\# \n'
			ascistring = ascii06
		elif font == 7:
			# 3-d (onlineasciitools)
			ascii07  = ' **     **  **     **  ******  **** \n'
			ascii07 += '/**    /** ***    */* //////* */// *\n'
			ascii07 += '/**    /**//**   * /*      /*/*   /*\n'
			ascii07 += '/**    /** /**  ******     * / **** \n'
			ascii07 += '/**    /** /** /////*     *   */// *\n'
			ascii07 += '/**    /** /**     /*    *   /*   /*\n'
			ascii07 += '//*******  ****    /*   *    / **** \n'
			ascii07 += ' ///////  ////     /   /      ////  \n'
			ascistring = ascii07
		else:
			ascistring = "unknown font type"
		return ascistring

	def addimage(self, path, text=""):
		self.add(self.image(path, text) + '\n')
		return 0

	def addparagraph(self, text):
		self.add(self.paragraph(text) + '\n')
		return 0	

	def addlink(self, text, location=""):
		self.add(self.link(text, location) + '\n')
		return 0	

	def addheadline(self, text, weight=5):
		self.add(self.headline(text, weight) + '\n')
		return 0		

	def addcomment(self, text):
		self.add(self.comment(text) + '\n')
		return 0

	def addasciiart(self, font=1):
		self.addcomment("\n" + self.asciiart(font) + '\n')
		return 0
	
	def addlist(self, items):
		self.add(self.unorderedlist(items) + '\n')
		return 0

	def addtable(self, columns, labels=False):
		self.add(self.table(columns, labels) + '\n')
		return 0


class CountingSummary:
	def __init__(self, datacontainer, figurename="counting.png"):
		self.dataset = datacontainer
		fs = FolderStructure()
		self.figurename = fs.get("plot") + "/" + figurename
		self.figurename2 = fs.get("plot") + "/" + "gap.png"
		
	def __str__(self):
		return "counting summary for " + str(self.dataset)
		
	# plot visualizing the quality and coverage of the counting sums
	def plot(self):

		x = self.dataset.getage() #load(df, "Age [Ma]")
		y = self.dataset.get("SUM")
		x, y = self.dataset.removezeros(x,y)

		e = self.dataset.get("SUM", "event") 
		# make figure, ax
		fig = plt.figure()
		ax1 = fig.add_subplot(111)
		# axis labels, title
		plt.title('Counting summary of U1478 ' + "(" + str(datetime.datetime.now())[0:10] + ")")
		plt.xlabel('Age [Ma]')
		plt.ylabel('Counting sums')
		#plotting
		colors = [[0, 0, 0]]
		lineoffsets = 200
		linelengths = 400
		ax1.eventplot(e, 
			colors=colors, 
			lineoffsets=lineoffsets,
			linelengths=linelengths, 
			linewidth=0.6
			)
		ax1.scatter(x, y)
		 # horizontal lines indicating quality thresholds
		ax1.set_ylim([0,350])
		ax1.axhline(y=50 , color='red')
		ax1.axhline(y=150, color='yellow')
		ax1.axhline(y=300, color='green')
		# ticks
		tick_frequency = 0.2
		loc = plticker.MultipleLocator(base=tick_frequency) # this locator puts ticks at regular intervals
		ax1.xaxis.set_major_locator(loc)
		# plt.show()
		fig.savefig(self.figurename, dpi=300)

	def gapplot(self):
		fig = plt.figure()
		ax1 = fig.add_subplot(111)
		plt.title('Remaining gaps ' + "(" + str(datetime.datetime.now())[0:10] + ")")
		plt.xlabel('Age [Ma]')
		plt.ylabel('step size between samples [ka]')
		g, a = self.gaps()
		plt.scatter(g, a, color='red')
		fig.savefig(self.figurename2, dpi=300)

	def gaps(self):
		x = self.dataset.getage() #load(df, "Age [Ma]")
		y = self.dataset.get("SUM")
		x, y = self.dataset.removezeros(x,y)
		g, a = [], []
		# for i, age in enumerate(x)
		for i in range(len(x) - 1):
			age = (x[i] + x[i+1]) / 2
			gap = x[i+1] - x[i]
			a.append(age)
			g.append(gap)
		return a, g

	def biggestgap(self):
		a, g = self.gaps()
		return max(g), a[g.index(max(g))]



	def picklist(self, filename="picklist.html"):
		html = Html()
		# columns to be used
		columnlist =[
			"ID",
			"HOLE",
			"CORE",
			"SECT",
			"top depth in core [cm]",
			"bottom depth in core [cm]",
			"Bottom depth in composite core [cm]",
			"Age [Ma]", 
			"Box position",
			"SUM", 
			"Comment"
			]
		# take from dataset
		picklist = self.dataset.get()[columnlist] 
		# make names shorter for online display
		picklist = picklist.rename(columns={
			"top depth in core [cm]": 'TOP [cm]', 
			"bottom depth in core [cm]": "BOT [cm]",
			"Bottom depth in composite core [cm]": "CCD [m]",
			"Box position": "Box"
			})
		# convert correlated core depth from cm to m 
		picklist['CCD [m]'] = picklist['CCD [m]'].apply(lambda x: x * 0.01)
		return picklist

	def countedsamples(self):
		# get number of counted samples
		# assuming there is cyperaceae in every sample (which so far is the case)
		return sum([1 for i in self.dataset.get("Cyperaceae", "bool") if i]) 
		
	def html(self, filename=""):
		# make stuff
		self.plot() # where? here: self.figurename
		self.gapplot()  # self.figurename2
		countingtext = str(self.countedsamples()) + " samples counted (" + str(datetime.datetime.now())[0:10] + ")"
		gap, age = self.biggestgap()
		gaptext = "Biggest remaining gap around " + str(round(age, 3)) + "&thinsp;Ma (" + str(round(gap*1000, 3)) + "&thinsp;ka)"
		picklist = self.picklist().to_html().replace('border="1"',' ')
		# put into html object
		html = Html("Counting Summary")
		html.addheadline("Counting Summary")
		html.addparagraph(countingtext) 
		html.addimage(self.figurename)
		html.addparagraph("")
		html.addtable( list(self.gaps()), ["Age [Ma]", "Gap size [ka]"] )
		html.addparagraph(gaptext)
		html.addimage(self.figurename2)
		html.addparagraph("")
		html.add(picklist)
		# put to file or stdout
		if filename == "":
			return html.generate()
		else: 
			html.tofile(filename)
			print("Counting summary saved to", filename)
			return 0


class SampleSummary:
	def __init__(self, datacontainer, sampleID):
		self.dataset = datacontainer
		self.id = str(sampleID)
		self.barplotpath = "../img/plot/" + self.id + "_barplot.png"
		self.figurename2 = "../img/plot/" + self.id + "_00.png"
		self.filename = "../html/sample/" + sampleID + "_oop.html"

	def __str__(self):
		return "sample summary for sample " + self.sampleid
		
	def singlesamplebarplot(self): #, objects, performance, sampleID):
		def digitalize(item):
			if (item == 0) or (pd.isnull(item)):
				return False
			else:
				return True

		label, row = Container.removezeros(
						self.dataset.labels(), 
						list(self.dataset.getrow(probe, clean=False))
						)
		# cut off unwanted columns
		label = label[12::]
		row = row[12::]
		relevant = [digitalize(i) for i in row]

		c, l = [], []
		l = []
		for i in range(len(row)):
			if relevant[i] and not label[i] == "Lycopodium":
				c.append(row[i])
				l.append(label[i])
		c = c[:-4]; l = l[:-4]
		# c.sort(); l.sort() #  this sorts them seperately... maybe sort inside pandas?
		sortedlists = [list(x) for x in zip(*sorted(zip(c, l), key=lambda pair: pair[0]))]
		c = sortedlists[0]
		l = sortedlists[1]
		c.reverse()
		l.reverse()

		# create new fig
		fig, ax1 = plt.subplots(figsize=(8, 6)) 
		y_pos = np.arange(len(c)) # [0,1,2,3....]
		# actual plot	 
		ax1.bar(l, c, align='center', alpha=0.5)
		
		# set labels
		ax1.set_xticks(y_pos) # without this, plt more ore less randomly sets labels at weird positions
		ax1.set_xticklabels(sortedlists[1], rotation=90)
		ax1.set_ylabel('Counting')
		plt.tight_layout() # impeding rotated labels to be cut 

		# save
		fig.savefig(
			self.barplotpath, 
			dpi=300, 
			#tranparent=True
			)
		plt.close()#

	def images(self):
		img_folder  = "../img/" + self.id 
		fotos = [each for each in listdir(img_folder) if each.endswith('.png')]
		return fotos

	def protocols(self):
		prot_folder = "../protocol"
		protocols = [each for each in listdir(prot_folder) if each.startswith(self.id)]
		return protocols

	def html(self, filename=""):
		# make stuff
		self.singlesamplebarplot() # where? here: self.barplotpath
		protocols = self.protocols()
		protocol_links = []
		for p in protocols:
			protocol_links.append(Html.link(p, "../protocol/" + str(p)))

		# images
		images = self.images()
		images.sort()

		# put into html object
		html = Html("Sample " + str(self.id))
		html.addheadline("Sample " + str(self.id), weight=2)
		html.addimage(self.barplotpath)
		html.addheadline("Protocols")
		html.addlist(protocol_links)
		html.addheadline("Images")
		for image in images:
			html.addimage("../img/" + self.id + "/" + image, text=str(image)[:-4])

		# put to file or stdout
		if filename == "":
			return html.generate()
		else: 
			html.tofile(filename)
			print("Counting summary saved to", filename)
			return 0


class Interpolation:
	'''Interpolation between data points 

	stores a set of data points and constructs a function based on interpolation between those datapoints. Made for containing an age model.
	'''
	d = "dataframe with fixed points"
	t = "list containing thresholds"
	p = "list containing polynoms"

	def __init__(self, dataframe):
		''' constructor
		
		@parameter datapoints dataframe, containing points between which will be interpolated
		'''
		# use tie points of preliminary age model

		if type(dataframe) == 'pandas.core.frame.DataFrame':
			self.d = dataframe
		else: 
			self.d = pd.DataFrame(dataframe).T
		# sort
		self.d = self.d.sort_values(self.d.columns[0]).reset_index(drop=True)
		self.establish()

	def __str__(self):
		''' string

		@return short description of the object
		'''
		return 'Interpolation based on ' + str(self.d.shape[0]) + ' data points\n' + str(self.d)


	def establish(self):
		t, p = [], []
		# start with 1(!) to allow acces element i-1
		# polynom list is then 1 shorter than tie point list
		# this makes sense as interpolation is always between two points 
		for i in range(1, len(self.d[0])):
			# assign two points
			p1 = [self.d[0][i-1], self.d[0][i]]
			p2 = [self.d[1][i-1], self.d[1][i]]
			# generate polynom
			coefficients = np.polyfit(p1, p2, 1)
			polynom = np.poly1d(coefficients)
			# put in list
			t.append(p1[0])
			p.append(polynom)
		# act locally, then send back to mommy
		self.t = t
		self.p = p

	def calc(self, x):
		# if below lowest threshold:
		if x <= self.t[0]:
			return self.p[0](x)
		# other cases must be higher than some threshold
		# so we check them in (from highest to lowest)
		else:
			for i in reversed(range(len(self.t))):
				if x > self.t[i]:
					return self.p[i](x)


class Agemodel(Interpolation):

	figurename  = "unspecified_agemodel.png"
	figuretitle = 'Age model for IODP site U1478'

	def plotself(ax):
		pass
	
	def plot(self, save=False):
		f, ax = plt.subplots()
		f.suptitle(self.figuretitle, fontsize=12)
		f.gca().invert_yaxis()
		
		self.plotself(ax)

		ax.axhspan(197.076, 256.745, color=cmap(1.0), alpha=0.5)
		ax.set_xlabel('Age [Ma]')
		ax.set_ylabel('Depth [m]')

		if save: 
			print('figure saved as "', self.figurename, '"')
			f.savefig(self.figurename, dpi=300,)
		else:
			plt.show()


class NanofossilAgemodel(Agemodel):

	figurename  = "agemodel_nannofossil.png"
	figuretitle = 'Age model for IODP site U1478\nbased on shipboard nanno fossils (Hall et al. 2017)'
	
	tie_points  = [
		(175.42, 1.95, "T D. triradiatus"),
		(203.59, 2.39, "T D. pentaradiatus"),
		(205.78, 2.49, "T D. surculus"),
		(221.12, 2.80, "T D. tamalis"),
		(235.23, 3.54, "T Sphenolithus spp."),
		(241.81, 3.70, "T R. pseudoumbilicus")]

	def __init__(self):
		tiepoints = pd.DataFrame(self.tie_points).T
		Interpolation.__init__(self, tiepoints)


	def plotself(self, ax, annotate=True):
		resolution = 1000
		x = np.linspace(170,270,resolution)
		y = [self.calc(i) for i in x]

		# ax.plot(tie_points_np[1], tie_points_np[0])
		ax.plot(y, x, color=cmap(0.0), zorder=1, label="Hall et al. (2017)")
		ax.scatter(self.d[1], self.d[0], color=cmap(0.15), zorder=2, label="Nanofossil tie points")

		# labels
		labels = [i[2] for i in self.tie_points]
		pos_x  = [i[0] for i in self.tie_points]
		pos_y  = [i[1] for i in self.tie_points]

		if annotate:
			for i in range(len(labels)):
				ax.annotate(labels[i], 
							(pos_y[i]+0.02, pos_x[i]-2), 
							bbox=dict(boxstyle='round,pad=0.2', alpha=0.0),
							fontsize=9)


class CyclostratigraphyAgemodel(Agemodel):

	figurename  = "agemodel_cyclostratigraphy.png"
	figuretitle = 'Age model for IODP site U1478\nbased on Cyclostratigraphy (Nakajima 2019)'
	
	datapath = '../data/age_data/cyclostrat_agemodel.csv'

	def __init__(self):
		tie_points = Container(self.datapath)
		Interpolation.__init__(self, tie_points.d.T.reset_index(drop=True))

	def plotself(self, ax):
		resolution = 2000
		x = np.linspace(170,270,resolution)
		y = [self.calc(i) for i in x]

		# ax.plot(tie_points_np[1], tie_points_np[0])
		ax.plot(y, x, color=cmap(0.3), zorder=1, label="Nakajima (2019)")

		# x = [i for i in self.d[0]]
		# y = [i for i in self.d[1]]
		# ax.scatter(y, x, color=cmap(0.3), zorder=1, label="Nakajima (2019)")


class CompareAgemodel(Agemodel):

	figurename = "agemodel_comparison.png"

	def __init__(self):
		self.figuretitle += '\nComparison'
		self.cs = CyclostratigraphyAgemodel()
		self.nf = NanofossilAgemodel()
		fs = FolderStructure()
		self.figurename = fs.get("plot") + "/" + self.figurename
		print(self.figurename)


	def diff(self):
		# get the depths
		data = Container()
		depths = data.get("Bottom depth in composite core [cm]", "absolute")
		points = data.get("SUM", "bool")
		# only use those, that have a counting sum
		datapoints = []
		for i, sampleexistence in enumerate(points):
			if sampleexistence:
				datapoints.append(depths[i])
		datapoints = [d / 100 for d in datapoints]

		# set the ages	
		# nf = [self.nf.calc(x) for x in datapoints]
		age = [self.cs.calc(x) for x in datapoints]
		# calculate difference
		d = []
		for i in datapoints:
			nanno = self.nf.calc(i)
			cyclo = self.cs.calc(i)
			diffe = abs(nanno - cyclo)
			d.append(diffe)

		return (age, d)
	

	def plot(self, save=False):
		f, (ax, diff) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1]})
		ax.invert_yaxis()
		# f.gca().invert_yaxis()

		# calculate differences
		age, difference = self.diff()

		#diff.scatter(age, difference)
		color     = 'grey'
		linestyle = '-'
		linewidth = 0.5
		for a in age:
			diff.axvline(a, color=color, linestyle=linestyle, linewidth=linewidth, zorder=0)
			ax.axvline(  a, color=color, linestyle=linestyle, linewidth=linewidth, zorder=0)
		

		self.cs.plotself(ax)
		self.nf.plotself(ax, annotate=False)

		resolution = 2000
		n = np.linspace(197,260,resolution)
		x = [self.cs.calc(i) for i in n]
		y = [abs(self.cs.calc(i) - self.nf.calc(i)) for i in n]
		highest = max(y)
		where = x[y.index(highest)]
		print("Highest difference at", where, "Ma (", highest, "Ma)")
		# diff.bar(age, difference, width=0.03)
		diff.plot(x, y, color='r') 


		# nice up and label
		f.suptitle(self.figuretitle, fontsize=12)
		# f.tight_layout()
		ax.axhspan(197.076, 256.745, color=cmap(1.0), alpha=0.5, zorder=1)
		ax.set_ylabel('Depth [m]')
		ax.legend(framealpha=1.0)
		diff.set_xlabel('Age [Ma]')
		diff.set_ylabel('Difference\nAge [Ma]')
		# spacing and dealing with overlap
		plt.subplots_adjust(hspace = -0.2)  # move together
		ax.set_xticks([]) #  remove ticks of upper plot
		ax.spines['bottom'].set_visible(False) # hide plot border 
		diff.spines['top'].set_visible(False)
		diff.patch.set_alpha(0.0) #  make background transparent


		if save: 
			print('figure saved as "', self.figurename, '"')
			f.savefig(self.figurename, dpi=300,)
		else:
			plt.show()



comp = CompareAgemodel()
comp.plot(save=True)
print("\n\n\n\n\n\n")

neu = Html("Agemodel")
neu.addheadline("Agemodel")
neu.addimage("../img/plot/agemodel_comparison.png")
neu.addparagraph("Highest difference at 2.830 Ma (136 ka)")
neu.addlist(["why does kai not use nanno plancton dates as tie points?", 
			 "why is kais age model linear on the shallower part (ca. until 208.63 m)?",
			 "why does the cruise report not state error margins for the nanno plancton ages?",
			 "should i look these up in the literature?"
			 ])
print(neu.generate())

# CountingSummary(Container()).html("test.html")


# gg = NanofossilAgemodel()
# gg.establish()
# print(200, gg.calc(200))
# # gg.plot()

# cg = CyclostratigraphyAgemodel()
# # print(cg)
# cg.establish()
# print(200, cg.calc(200))
# cg.plot()


# # BashStuff.convertODS()

# sevenup = Container()
# seven = sevenup.get("SUM", "event")
# print("7!!", seven[0])
# nn = [gg.calc(x) for x in seven]
# cc = [cg.calc(x) for x in seven]
# diff = [nn[i] - cc[i] for i in range(len(seven))]
# plt.scatter(seven, cc)
# plt.show()



# print(gg)

# plt.scatter(gg.d[0], gg.d[1])
# plt.plot(x, y)
# plt.show()

# probe = "a31f3w13"
# probe = "d20f3w3"

# ss = SampleSummary(Container(), probe)
# # print(list(d.getrow(probe, clean=False)))
# # print(d.labels())
# # label, row = Container.removezeros(d.labels(), list(d.getrow(probe, clean=False)))
# ss.html("test.html")


sys.exit("\n\nabort!")




#######################
##					 ##
## WORK IN PROGRESS! ##
##					 ##
#######################
class BashStuff:
	def __init__(self):
		pass

	@staticmethod
	def bash(bashCommand):
		# based on advice found here: https://stackoverflow.com/questions/4256107/running-bash-commands-in-python
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		output, error = process.communicate() 

	@staticmethod
	def convertODS():
		fs = FolderStructure()
		bashCommand = "ssconvert " + fs.get("pollendata") + "/U1478_mastertable.ods " + fs.get("pollendata") + "/U1478.csv"
		bash(bashCommand)
		return 0



























































































#################################
## ACCESS DATA FRAME FUNCTIONS ##
#################################







def print_xy(pair):
	"""
	print plotable pair of arrays to terminal

	This function prints two plotable (i.e. numerical arrays of the same length) 
	into standard output. Used for debugging purposes

	Args:
		pair:	A tuple of two lists or arrays 

	"""
	x, y = pair
	for i in range(len(x)):
		print(str(x[i])[0:5], "\t", y[i])

def load(df, label):
	"""
	takes column of df and erases zero values from record

	This function takes a column with the label ("label") out of a pandas data frame ("df"), 
	removes values == 0 and returns the shortened list. The SUM column of the data frame is 
	used as a reference point for diferenciating between zero findings and empty values.

	Args:
		df:	A pandas dataframe
		label:	The label of the column, that should be extracted

	"""
	x = list(df[label])
	boolx = list(df["SUM"])
	for i in range(len(x)):
		if boolx[i] > 0:
			if type(x[i]) == type("string"): # if table uses comma as decimal seperator
				x[i] = float(x[i].replace(',','.'))
			if x[i] == 0:
				x[i] = None
	return x

def stupidload(df, label):
	"""
	takes column of df and erases zero values from record

	Does the same as load(df, label), without relying on the column labeled "SUM", thus not differing 
	between zero values and empty values
	
	Args:
		df:	A pandas dataframe
		label:	The label of the column, that should be extracted
	
	"""
	x = list(df[label])
	for i in range(len(x)):
		if type(x[i]) == type("string"): # if table uses comma as decimal seperator
			x[i] = float(x[i].replace(',','.'))
		if x[i] == 0:
			x[i] = None
	return x


 
def loadflat(df, label):
	"""
	[outdated] load() + replaces non zero values with zero (early version of loadbool() )

	Args:
		df:	A pandas dataframe
		label:	The label of the column, that should be extracted
	"""
	x = list(df[label])
	for i in range(len(x)):
		if type(x[i]) == type("string"): # if table uses comma as decimal seperator
			x[i] = float(x[i].replace(',','.'))
		if x[i] == 0:
			x[i] = float('NaN')
		else:
			x[i] = 0
	return x


def loadbool(df, label):
	"""
	returns list containig information about where non zero values are

	Args:
		df:	A pandas dataframe
		label:	The label of the column, that should be extracted
	"""
	x = list(df[label])
	for i in range(len(x)):
		if type(x[i]) == type("string"): # if table uses comma as decimal seperator
			x[i] = float(x[i].replace(',','.'))
		if x[i] > 0:
			x[i] = True
		else:
			x[i] = False
	return x

def loadrel(df, label):
	"""
	load() + divide by SUM

	Loads a column of a pandas data frame as relative values (divided by sum given in "SUM" column)

	Args:
		df:	A pandas dataframe
		label:	The label of the column, that should be extracted
	"""

	x = load(df, label)
	m = loadbool(df, label)
	s = load(df, "SUM")
	for i in range(len(m)):
		if m[i]:
			x[i] = x[i] / s[i]
	return x


# returns list of ages with non zero values (for matplotlib.eventplot() )
def loadevent(df, label, age):
	x = loadbool(df, label)
	y = load(df, age)
	export = []
	for i in range(len(x)):
		if x[i]:
			export.append(y[i])
	return export

# loads two equally long lists with pollen data and ages
def loadcroped(df, label, age="Age [Ma]"):
	y = loadrel(df, label)
	x = load(df, age)
	m = loadbool(df, label)
	xx = [] 
	yy = []
	for i in range(len(m)):
		if m[i]:
			xx.append(x[i])
			yy.append(y[i])
	return xx, yy


def textload(df, label):
	"""
	takes column of df and erases empty values

	[not valid description] Does the same as load(df, label), without relying on the column labeled "SUM", thus not differing 
	between zero values and empty values
	
	Args:
		df:	A pandas dataframe
		label:	The label of the column, that should be extracted
	
	"""
	x = list(df[label])
	y = []
	for i in range(len(x)):
		y.append(str(x[i]))
	return y















#########################
## PLOT DATA FUNCTIONS ##
#########################


# plot visualizing the quality and coverage of the counting sums
def print_counting(df):
	e = loadevent(df, "SUM", "Age [Ma]")
	x = load(df, "Age [Ma]")
	y = stupidload(df, "SUM")

	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	
	plt.title('Counting summary of U1478 ' + "(" + str(datetime.datetime.now())[0:10] + ")")
	plt.xlabel('Age [Ma]')
	plt.ylabel('counting sums')

	colors = [[0, 0, 0]]
	lineoffsets = 200
	linelengths = 400

	ax1.eventplot(e, colors=colors, lineoffsets=lineoffsets,
					 linelengths=linelengths, linewidth=0.6)
	ax1.scatter(x, y)

	# print_xy((x,y))

	ax1.set_ylim([0,350])
	ax1.axhline(y=50 , color='red') # indicating quality thresholds
	ax1.axhline(y=150, color='yellow')
	ax1.axhline(y=300, color='green')

	# ticks
	tick_frequency = 0.2
	loc = plticker.MultipleLocator(base=tick_frequency) # this locator puts ticks at regular intervals
	ax1.xaxis.set_major_locator(loc)

	# plt.show()
	fig.savefig("counting.png", dpi=300)


# plot some ratios
def print_co2(df):

	def find_nearest(array, value):
		array = np.asarray(array)
		idex = (np.abs(array - value)).argmin()
		return idex


	def rate_correlation(r):
		if r == 0:
			rating =	"no"
		elif r == 1.0:	
			rating =	"perfect positive"
		elif r == -1.0:	
			rating =	"perfect negative"
		elif r < -0.95:
			rating = 	"perfect negative"
		elif r < -0.7:
			rating =	"strong negative"
		elif r < -0.5:
			rating =	"moderate negative"
		elif r < -0.3:
			rating =	"weak negative"
		elif r < 0:
			rating =	"very weak negative"
		elif r > 0.7:	
			rating =	"strong positive"
		elif r > 0.5:	
			rating =	"moderate positive"
		elif r > 0.3:	
			rating =	"weak positive"
		elif r > 0:
			rating =	"very weak positive"
		else: 
			return "error: r should be <= 1 AND >= -1"
		
		return rating + " relationship"



	# get pollen data
	x = load(df, "Age [Ma]")
	boo = loadbool(df, "Poaceae")
	poa = load(df, "Poaceae")
	cyp = load(df, "Cyperaceae")
	res = load(df, "SUM")

	# calculate c3/c4 ratio
	c3c4_rat =	[] 
	c3c4_age = []
	for i in range(len(res)):
		if boo[i]:
			c4 = poa[i] + cyp[i] # total c4 plants
			c3 = res[i] - c4 # total c3 plants
			c3c4_rat.append( c3 / c4 ) # ratio
			c3c4_age.append(x[i]) # age

	# load co2 values (Bartoli et al.; 2011)
	filename="co2.csv"
	co2 = pd.read_table(filename, sep=',')
	# extract co2 data
	co_val = np.asarray(stupidload(co2, "co2 1 atm"))
	co_errlo = np.asarray(stupidload(co2, "error low"))
	co_errhi = np.asarray(stupidload(co2, "error high"))
	co_age = stupidload(co2, "Age [Ma]")

	# add error on values
	upper_error = co_val + co_errhi
	lower_error = co_val - co_errlo
	



	## cross correlation (-> separate to function)
	# interpolate time series
	# >>> np.interp(2.5, xp, fp)
	interpol_age = np.linspace(min(co_age), max(co_age), 1000)
	interpol_co2 = np.zeros(len(interpol_age))
	interpol_c34 = np.zeros(len(interpol_age))
	for i in range(len(interpol_age)):
		#interpolate CO2 values
		interpol_co2[i] = np.interp(interpol_age[i], co_age, co_val )
		# interpolate c3/c4 ratio
		interpol_c34[i] = np.interp(interpol_age[i], c3c4_age, c3c4_rat )
	# trim the arrays: 
	lower_bound = find_nearest(interpol_age, min(c3c4_age))
	upper_bound = find_nearest(interpol_age, max(c3c4_age))
	interpol_age = interpol_age[lower_bound:upper_bound]
	interpol_co2 = interpol_co2[lower_bound:upper_bound]
	interpol_c34 = interpol_c34[lower_bound:upper_bound]
	# get pearson:
	pearson = np.corrcoef(interpol_c34, interpol_co2)[0, 1]
	# print(linregress(interpol_c34, interpol_co2))



	# on overlaying plots see: https://stackoverflow.com/questions/7733693/matplotlib-overlay-plots-with-different-scales#7734614
	fig, ax = plt.subplots()
	# Twin the x-axis twice to make independent y-axes.
	axes = [ax, ax.twinx()]

	# somehow makes more sense to change....
	plt.suptitle('Comparison of pCO$_2$ and C3/C4-ratio' + "	(" + str(datetime.datetime.now())[0:10] + ")")
	
	
	# plt.ylabel('banana')
	suptitle_string = "there is a " + rate_correlation(pearson) + "relationship (r= " + str(round(pearson,3)) + ")"
	plt.title(suptitle_string, fontsize=8 ) #, y=1.05, fontsize=18)

	axes[0].plot(co_age, co_val,	marker='.')
	axes[0].fill_between(co_age, upper_error, lower_error,color='blue',alpha=.3, linewidth=0.0)
	axes[0].set_ylabel('pCO$_2$ [$\mu$atm]', color='blue')

	axes[1].plot(c3c4_age, c3c4_rat, color='darkred', marker='x')
	axes[1].set_ylabel('C3/C4 ratio', color='darkred')
	axes[1].set_ylim([-1,5])

	# plt.xlabel('Age [Ma]')
	# apparently has to be set on both axes...
	axes[0].set_xlabel('Age [Ma]')
	axes[1].set_xlabel('Age [Ma]')

	# ticks
	# tick_frequency = 0.2
	# loc = plticker.MultipleLocator(base=tick_frequency) # this locator puts ticks at regular intervals
	# ax.xaxis.set_major_locator(loc)
	# get rid of 0.0 tick on y-axis
	# not woring:
	# axes[1].yaxis.get_major_ticks()[0].label1.set_visible(False)

	# plt.show()
	fig.savefig("co2.png", dpi=300)



def trendvis_plot(df):
	#import trendvis 

	label = "Cyperaceae"
	c=[]
	x, y = loadcroped(df, label , "Age [Ma]")
	c.append(x)
	c.append(y)
	label = "Poaceae"
	p=[]
	x, y = loadcroped(df, label , "Age [Ma]")
	p.append(x)
	p.append(y)
	label = "Podocarpus"
	o=[]
	x, y = loadcroped(df, label , "Age [Ma]")
	o.append(x)
	o.append(y)

	# Pseudorandom data and plot attributes
	random_generator = np.random.RandomState(seed=123)
	yvals = random_generator.rand(10)

	# Plot attributes
	lw = 1.5

	nums = 10
	# convenience function trendvis.gridwrapper() is available
	# to initialize XGrid and do most of the formatting shown here
	ex0 = trendvis.XGrid([1,2,1], figsize=(5,5))

	# Convenience function for plotting line data
	# Automatically colors y axis spines to
	# match line colors (auto_spinecolor=True)
	trendvis.plot_data(ex0,
		[
			[(c[0],c[1], 'blue')],
		 	[(p[0],p[1], 'red')],
		 	[(o[0],o[1], 'green')]
		],
		lw=lw, 
		markeredgecolor='none', 
		marker='s'
		)

	# Get rid of extra spines
	ex0.cleanup_grid()
	ex0.set_spinewidth(lw)

	ex0.set_all_ticknums([(2, 1)], [(0.2, 0.1), (1, 0.5), (2, 1)])
	ex0.set_ticks(major_dim=(7, 3), minor_dim=(4, 2))

	ex0.set_ylabels(['stack axis 0', 'stack axis 1', 'stack axis 2'])

	# In XGrid.fig.axes, axes live in a 1 level list
	# In XGrid.axes, axes live in a nested list of [row][column]
	ex0.axes[2][0].set_xlabel('Main Axis', fontsize=14)

	# Compact the plot
	ex0.fig.subplots_adjust(hspace=-0.3)

	plt.show()



# used by print_pollen and joypollen to make subplots.
def plotpollen(ax, label, bottom=False, xaxislabel="Age [Ma]"):
	ax.set_ylabel(label, fontsize='small')
	ax.patch.set_alpha(0.0)
	
	x, y = loadcroped(df, label , xaxislabel)

	# actual plotting:
	ax.fill_between(x, 0, y)
	ax.scatter(x,y, color='black', marker='.' ) 

	ax.set_ylim([0,0.75])
	ax.grid(True, axis='x')
	if not bottom:
		xticklabels = ax.get_xticklabels() 
		plt.setp(xticklabels, visible=False)
		# remove spines: 0=left, 1=right, 2=bottom, 3=top
		i=0
		for spine in plt.gca().spines.values():
			if i > 0: # only left spine left
				spine.set_visible(False)
			i += 1	
	else: # i.e. bottom
		i=0
		for spine in plt.gca().spines.values():
			if (i == 1) or (i == 3): # left and bottom spine left
				spine.set_visible(False)
			i += 1
		ax.set_xlabel(xaxislabel)

	# ticks
	tick_frequency = 0.2
	loc = plticker.MultipleLocator(base=tick_frequency) # this locator puts ticks at regular intervals
	ax.xaxis.set_major_locator(loc)
	# get rid of 0.0 tick on y-axis
	ax.yaxis.get_major_ticks()[0].label1.set_visible(False)




# plot of relative pollen percentages
def print_pollen(df, plotlist):

	savename = "pollen_countings.png"
	webname = "preliminarypollen"
	figuretitle = 'U1478, pollen concentrations'


	fig = plt.figure(
		# figsize=(3) # replaced by fig.set_size_inches
		)
	fig.set_size_inches(5, len(plotlist)+3 )
	# set title, including date
	plt.title(figuretitle + " (" + str(datetime.datetime.now())[0:10] + ")")

	# delete ticks. lowermost plot gets ticks in plotpollen()
	plt.yticks([])
	plt.xticks([])


	#make all borders invisible. they are set back partially in plotpollen()
	for spine in plt.gca().spines.values():
		spine.set_visible(False)

	subplot = (len(plotlist), 1, 1)
	axes = [None] * len(plotlist)


	for i in range(len(plotlist)):
		# first does not need sharex
		if (i == 0): 
			a,b,c = subplot
			axes[i] = fig.add_subplot(a,b,c)
		else:
			a,b,c = subplot
			axes[i] = fig.add_subplot(a,b,c, sharex = axes[0])
		# last one puts the x-axis labels
		if (i == ( len(plotlist) - 1) ): 
			plotpollen(axes[i], plotlist[i], bottom=True)
		else:
			plotpollen(axes[i], plotlist[i])
			# increment first of subplot-tuple
			a,b,c = subplot
			c += 1
			subplot = (a, b, c)

	# may be worth trying:
	#https://matplotlib.org/tutorials/intermediate/tight_layout_guide.html#use-with-axesgrid1

	#reduce spacing between plots
	plt.subplots_adjust(hspace = .001)

	# fig.show()
	fig.savefig(
		savename, 
		dpi=300, 
		#tranparent=True
		)



# makes a joy division style plot
def joypollen(df, plotlist):

	from PIL import Image
	import PIL.ImageOps	 

	def plotpollen(ax, label, bottom=False):
		ax.set_ylabel(label, fontsize='small', rotation=0)
		ax.patch.set_alpha(0.0)
		
		x, y = loadcroped(df, label , "Age [Ma]")

		# actual plotting:
		ax.fill_between(x, 0, y, color="white")
		ax.plot(x,y, color='black') 

		ax.set_ylim([0,0.75])
		ax.grid(True, axis='x')


		if bottom:
			i=0
			for spine in plt.gca().spines.values():
				if (i == 1) or (i == 3) or (i == 0) :
					spine.set_visible(False)
				i += 1
			plt.yticks([])
			yticklabels = ax.get_yticklabels() 
			plt.setp(yticklabels, visible=False)
		else:
			for spine in plt.gca().spines.values():
				spine.set_visible(False)
			xticklabels = ax.get_xticklabels() 
			plt.setp(xticklabels, visible=False)
			plt.yticks([])
			plt.xticks([])

		# ax.yaxis.set_label_coords(-0.5, 0.5)
		ax.set_facecolor('blue')


	savename = "pollen_cp1919style.png"
	webname = "preliminarypollen"
	figuretitle = 'U1478, pollen concentrations'

	# make figure
	fig = plt.figure(
		# figsize=(3)
		)
	fig.set_size_inches(5, 8)
	plt.rcParams['figure.facecolor'] = 'black'


	plt.title(figuretitle + " (" + str(datetime.datetime.now())[0:10] + ")")


	#make all borders invisible. they are set back partially in plotpollen()
	for spine in plt.gca().spines.values():
		spine.set_visible(False)
	plt.yticks([])

	# make vertically stacked subplots
	subplot = (len(plotlist), 1, 1)
	axes = [None] * len(plotlist)
	for i in range(len(plotlist)):
		# first does not need sharex
		if (i == 0): 
			a,b,c = subplot
			axes[i] = fig.add_subplot(a,b,c)
		else:
			a,b,c = subplot
			axes[i] = fig.add_subplot(a,b,c, sharex = axes[0])
		# last one puts the x-axis labels
		if (i == ( len(plotlist) - 1) ): 
			plotpollen(axes[i], plotlist[i], bottom=True)
		else:
			plotpollen(axes[i], plotlist[i])
			# increment first of subplot-tuple
			a,b,c = subplot
			c += 1
			subplot = (a, b, c)

	#reduce spacing between plots
	plt.subplots_adjust(hspace = -0.9)

	# fig.show()
	fig.savefig(
		savename, 
		dpi=300, 
		#tranparent=True
		)

	# invert colors
	image = Image.open(savename)
	if image.mode == 'RGBA':
		r,g,b,a = image.split()
		rgb_image = Image.merge('RGB', (r,g,b))
		inverted_image = PIL.ImageOps.invert(rgb_image)
		r2,g2,b2 = inverted_image.split()
		final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))		
		inverted_image.save(savename)
	else:
		inverted_image = PIL.ImageOps.invert(image)
		inverted_image.save(savename)

# same as joypollen, failed attempt using joypy
# joyplot produces histograms. useless!
def joypollen_fail(df, plotlist):
	#import joypy as joy

	savename = "joypollen.png"

	joylist = []
	joydf = pd.DataFrame() #creates a new dataframe that's empty
	for label in plotlist:
		joydf = joydf.append(df[label])
	# joydf = joydf.append(df["Age [Ma]"])
	joydf = joydf.T # transpose
	# print(joydf)

	fig, axes = joy.joyplot(joydf	#,
	# 						by="Age [Ma]", 
	# 						#column="Anomaly", 
	# 						ylabels=False, xlabels=False, 
	# 						grid=False, fill=False, 
	# 						background='k', linecolor="w", linewidth=1,
	# 						legend=False, overlap=0.5, figsize=(6,5),
	# 						kind="counts", bins=80
							)

	fig.savefig(
		savename, 
		dpi=300, 
		#tranparent=True
		)


def pca_plot(df, species):
	#from rpy2.robjects import pandas2ri
	
	savename = "pca.png"

	pcalist = []
	pcadf = pd.DataFrame() #creates a new dataframe that's empty
	for label in species:
		pcadf = pcadf.append(df[label])
	# pcadf = pcadf.append(df["Age [Ma]"])
	pcadf = pcadf.T # transpose

	#pandas2ri.activate()
	print(pcadf)

	plt.hist(pcadf["Cyperaceae"])

	plt.show()
	# fig.savefig(
	# 	savename, 
	# 	dpi=300, 
	# 	#tranparent=True
	# 	)


def species_stat(df, columnname):
	from matplotlib import gridspec
	savename = "stat_" + columnname + ".png"

	# load data
	relabundances = loadcroped(df, columnname)[1]
	# fig, axs = plt.subplots(nrows=1, ncols=2)
	# make boxplot smaller
	fig = plt.figure(figsize=(8, 6)) 
	gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1]) 
	fig.suptitle('Distribution of relative abundance of ' + columnname + " (" +str(datetime.datetime.now())[0:10] + ")")
	# generate subplots
	axs = [None] * 2
	axs[0] = plt.subplot(gs[0])
	axs[1] = plt.subplot(gs[1])
	# histogram
	ax = axs[0]
	ax.hist(relabundances, 10)#, density=True)
	ax.set_title('Histogram')
	# box
	ax = axs[1]
	ax.boxplot(relabundances)
	ax.set_title('mean: '+ str(np.mean(np.asarray(relabundances)))[0:5] + 
				'\nvar: '+ str(np.var(np.asarray(relabundances)))[0:5])

	print(columnname, np.var(np.asarray(relabundances)))
	
	fig.savefig(
		savename, 
		dpi=300, 
		#tranparent=True
		)
	plt.close()


def print_agemodel():
	savename = "agemodel_nannofossil.png"
	resolution = 1000
	x = np.linspace(170,270,resolution)
	y = np.zeros(resolution)
	for i in range(len(y)):
		y[i] = age(x[i])
	labels = ["Splice Depth (m)", "Age (Ma)", "Event"]
	tie_points_l = [
		(175.42, 1.95, "T D. triradiatus"),
		(203.59, 2.39, "T D. pentaradiatus"),
		(205.78, 2.49, "T D. surculus"),
		(221.12, 2.80, "T D. tamalis"),
		(235.23, 3.54, "T Sphenolithus spp."),
		(241.81, 3.70, "T R. pseudoumbilicus")]
	tie_points_df = pd.DataFrame.from_records(tie_points_l, columns=labels)
	tie_points_np = np.transpose(tie_points_df.drop('Event', 1).values)

	f, ax = plt.subplots()
	# ax.plot(tie_points_np[1], tie_points_np[0])
	ax.plot(y, x, color=cmap(0.0), zorder=1)
	ax.scatter(tie_points_np[1], tie_points_np[0], color=cmap(0.5), zorder=2)

	labels = tie_points_df['Event'].values.tolist()
	for i in range(len(labels)):
	    ax.annotate(labels[i], (tie_points_np[1][i]-0.05, tie_points_np[0][i]-3),
	    	 bbox=dict(boxstyle='round,pad=0.2', alpha=0.0))

	ax.axhspan(197.076, 256.745, color=cmap(1.0), alpha=0.5)
	f.gca().invert_yaxis()
	ax.set_xlabel('Age [Ma]')
	ax.set_ylabel('Depth [m]')
	f.suptitle('Age model for IODP site U1478\nbased on shipboard nanno fossils (Hall et al. 2017) ', fontsize=12)




	f.savefig(
		savename, 
		dpi=300, 
		#tranparent=True
		)



def singlesamplebarplot(objects, performance, sampleID):
	# create new fig
	fig, ax1 = plt.subplots(figsize=(8, 6)) 
	y_pos = np.arange(len(objects)) # [0,1,2,3....]
	savename = "../img/plot/" + sampleID + ".png"
	# actual plot	 
	ax1.bar(y_pos, performance, align='center', alpha=0.5)
	# set labels
	ax1.set_xticks(y_pos) # without this, plt more ore less randomly sets labels at weird positions
	ax1.set_xticklabels(objects, rotation=90)
	ax1.set_ylabel('Counting')
	
	plt.tight_layout() # impeding rotated labels to be cut 

	fig.savefig(
		savename, 
		dpi=300, 
		#tranparent=True
		)
	plt.close()




def everybarplot(df, columnlist):
	# makes a mask to sort out empty cells
	def digitalize(item):
		if (item == 0) or (pd.isnull(item)):
			return False
		else:
			return True

	n = 1 # just for printing 
	for index, row in df.iterrows():
		if (row['SUM'] > 0):

			sampleID = (row["HOLE"] + row["CORE"] + row["SECT"] + str(int(row["bottom depth in core [cm]"]))).lower()
			countings = list(row[columnlist])
			relevant = [digitalize(i) for i in countings]
			count = []
			label = []
			for i in range(len(countings)):
				if relevant[i]:
					count.append(countings[i])
					label.append(columnlist[i])
			# print(n, sampleID, ": ")
			# print(label)
			# print(count)
			# print("")
			# n += 1
			
			if (sampleID != "c29f2w99"): # photos not on disk yet...
				singlesamplebarplot(label, count, sampleID)
				singlesamplehtml(sampleID)









###############################
## HTML GENERATING FUNCTIONS ##
###############################

def picklist(df):
	filename = "picklist.html"
	# columns to be used
	columnlist =[
		"ID",
		"HOLE",
		"CORE",
		"SECT",
		"top depth in core [cm]",
		"bottom depth in core [cm]",
		"Bottom depth in composite core [cm]",
		"Age [Ma]", 
		"Box position",
		"SUM", 
		"Comment"
		]
	# hmtl header containing style
	html_head='''
	<!DOCTYPE html>
	<html>
		<head>
			<meta charset="UTF-8">
			<title>uni</title>
			<link rel="shortcut icon" href="https://www.camposcampos.de/img/maroon-owl-256.ico" type="image/vnd.microsoft.icon">
			<link rel="stylesheet" type="text/css" href="https://uni.camposcampos.de/u1478/html/main.css">
			<style>
				table.dataframe {
					border: 1px solid #1C6EA4;
					background-color: #EEEEEE;
	<!--			width: 100%;-->
					text-align: left;
					border-collapse: collapse;
				}
				table.dataframe td, table.dataframe th {
					border: 1px solid #444444;
					padding: 3px 2px;
				}
				table.dataframe tbody td {
					font-size: 13px;
				}
				table.dataframe tr:nth-child(even) {
					background: #D0E4F5;
				}
				table.dataframe thead {
					background: #D0E4F5;
					border-bottom: 2px solid #444444;
				}
				table.dataframe thead th {
					font-size: 15px;
					font-weight: bold;
					color: #000000;
					border-left: 2px solid #444444;
				}
				table.dataframe thead th:first-child {
					border-left: none;
				}
				table.dataframe tfoot td {
					font-size: 14px;
				}
				table.dataframe tfoot .links {
					text-align: right;
				}
				table.dataframe tfoot .links a{
					display: inline-block;
					background: #1C6EA4;
					color: #FFFFFF;
					padding: 2px 8px;
					border-radius: 5px;
				}
			</style>
		</head>
		<body>'''
	# only take some columns
	picklist = df[columnlist]
	# make names shorter for online display
	picklist = picklist.rename(columns={
		"top depth in core [cm]": 'TOP [cm]', 
		"bottom depth in core [cm]": "BOT [cm]",
		"Bottom depth in composite core [cm]": "CCD [m]",
		"Box position": "Box"
		})
	# convert correlated core depth from cm to m 
	picklist['CCD [m]'] = picklist['CCD [m]'].apply(lambda x: x * 0.01)
	
	# get number of counted samples
	summe = sum([1 for i in loadbool(df, "Cyperaceae") if i])
	html_sum_div = "<p>" + str(summe) + " samples counted (" + str(datetime.datetime.now())[0:10] + ")"


	# write to file
	print(html_head,
		html_sum_div,
		picklist.to_html().replace('border="1"',' '),
		html_footer(),
		file=open(filename, 'w')
		)
	#picklist.to_html().replace('border="1"',' ')




def singlesamplehtml(sampleID):
	html_filename = "../html/sample/" + sampleID + ".html"
	# hmtl header containing style
	html_head='''
	<!DOCTYPE html>
	<html>
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1">
			<title>uni</title>
			<link rel="shortcut icon" href="https://www.camposcampos.de/img/maroon-owl-256.ico" type="image/vnd.microsoft.icon">
			<link rel="stylesheet" type="text/css" href="../html/main.css">
			<style>

			</style>
		</head>
		<body>'''
	# fotos and protocols
	img_folder  = "../img/" + sampleID 
	prot_folder = "../protocol"
	fotos = [each for each in listdir(img_folder) if each.endswith('.png')]
	protocols = [each for each in listdir(prot_folder) if each.startswith(sampleID)]

	html_headline = "\n\n<h3>Sample " + sampleID + "</h3>\n\n"
	html_headline += '<img src="../../img/plot/' + sampleID + '.png" width="600px">\n\n' 


	html_protocols="<h5>Protocols:</h5>\n<ul>"
	for item in protocols:
		html_protocols += '<li><a href="../' + prot_folder + "/" + item + '">' + item + "</a></li>\n"
	html_protocols += "</ul>\n\n"

	html_images="<h5>Images:</h5>\n\n<div>\n\n"
	fotos.sort()
	for item in fotos:
		html_images += '<div class="container">\n'
		html_images += '\t<img src="../' + img_folder + "/" + item + '">\n'
		html_images += '\t<div class="top-left">Image Nr. ' + item[:-4] + '</div>\n'
		html_images += '</div>\n\n'
	html_images += "\n</div>\n\n"

	# print(fotos)
	# print(protocols)
	# print(html_headline)
	# print(html_protocols)
	# print(html_images)

	# write to file
	print(html_head,
		html_headline,
		html_protocols,
		html_images,
		html_footer(),
		file=open(html_filename, 'w')
		)

	return "saved in " + html_filename


def html_sample_list():
	html_folder = "../html/sample"
	prot_folder = "protocols.html"
	samples = [each for each in listdir(html_folder) if each.endswith('.html')]
	html  = '<h3>Countings</h3>\n'
	html += "<ul>\n"
	html += '\t<li><p><a href="picklist.html">Picklist</a></p>\n'
	html += '\t<li><p><a href="../misc/zaehlblatt.pdf">Counting sheet (PDF)</a></p>\n'
	html += '\t<li><p><a href="' + prot_folder + '">Scanned protocols</a></p>\n'
	html += '\t<li><p>Individual sample summaries:</p>\n'
	html += "<ul>\n"
	for item in samples:
		html += "\t<li>" + '<a href="' + html_folder + "/" + item + '">' + item[:-5] + "</a></li>\n"
	html += "</ul>\n\n"
	html += "</ul>\n\n"
	return html


def html_footer():
	#old
	html  = '\t<footer style="position:fixed; font-size:.8em; text-align:right; bottom:0px; margin-left:-25px; height:20px; width:100%;">'
	html += '\t\t<a href="http://uni.camposcampos.de" target="_blank"><img src="owl.ico"></a>'
	html += '\t</footer>\n'
	html += '\t</body>\n'
	html += '</html>'
	# new
	html =  '\t<footer style="position:fixed; font-size:.8em; text-align:right; bottom:3px; right: 5px; height:20px; width:100%;">\n'
	html += '\t\t<a href="http://uni.camposcampos.de" target="_blank">uni.camposcampos.de &#x1F989 </a>\n'
	html += '\t</footer>\n'
	html += '\t</body>\n'
	html += '</html>\n'
	
	return html

def html_header():
	html = '''
	<!DOCTYPE html>
	<html>
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1">
			<title>uni</title>
			<link rel="shortcut icon" href="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/emojidex/112/owl_1f989.png" type="image/vnd.microsoft.icon">
			<link rel="stylesheet" type="text/css" href="../html/main.css">
			<style>
				div.container {
				  position: relative;
				  text-align: center;
				  float: left;
				}
				.top-left {
				  position: absolute;
				  background: rgba(255, 255, 255, 0.3); /* white see-through */
				  top: 8px;
				  left: 16px;
				  font-size: 12px;
				  padding: 20px;
				}
				h5 {
				  text-decoration: underline;
				}
				div.bunch {
				  float: none;
				  width: 100%;
				}
				div.slide {
				  heigth: 100%;        
				}
				section.container {
				  height: 80%px;
				  margin: auto;
				  padding: 10px;
				  display: flex;
				}
				.clearfix::after {
				  clear: both;
				  display: block;
				}
			</style>
		</head>
		<body>
		<h1>U1478</h1>
	'''
	html = '''
	<!DOCTYPE html>
	<html>
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1">
			<title>uni</title>
			<link rel="shortcut icon" href="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/emojidex/112/owl_1f989.png" type="image/vnd.microsoft.icon">
			<link rel="stylesheet" type="text/css" href="../html/main.css">
		</head>
		<body>
		<h1>U1478</h1>
	'''
	return html

def html_taxo():
	html = '''
			<h3>Taxonomic References</h3>
		    <ul>
				<li><a href="../misc/taxo/EastAfricanPollenAtlas.pdf">Taxonomic Reference Collenction (PDF, 46MB)</a></li>
				<li><a href="../misc/taxo/pollen_posterA0.pdf">Pollen Poster (PDF, 37MB)</a></li>
				<li><a href="../misc/taxo/tricolp.png">Tricolpate Collection (PNG, 6MB)</a></li>
				<li><a href="identities.html">Grouping on the run (a lot of images, slow server)</a></li>
			</ul>
	'''
	return html


def html_protocols():
	prot_folder = "../protocol"
	protocols = [each for each in listdir(prot_folder) if each.endswith(".pdf")]
	html="\t\t\t<h3>Protocols</h3>\n\t\t\t<ul>\n"
	for item in protocols:
		html += '\t\t\t\t<li><a href="' + prot_folder + "/" + item + '">' + item + "</a></li>\n"
	html += "\t\t\t</ul>\n\n"
	# alternativly just link the folder:
	#html  = '\t\t\t<p><a href="' + prot_folder + '">scanned protocols</a></p>\n'
	#html += '\t\t\t<p><a href="pollen/sample/file/zaehlblatt.pdf">Z&auml;hlblatt (PDF)</a></p>\n'
	return html


def html_data_and_plots():
	html = '''
			<h3>Data</h3>
			<ul>
				<li>Sample list:  <a href="../data/lists/U1478_printlist.pdf">PDF</a></li>
				<li>pollen countings: <a href="../data/pollen/U1478_mastertable.ods">ODS</a>, <a href="../data/pollen/U1478.csv">CSV</a></li>
				<!--
				<li>XRF: <a href="data/U1478_splice-values-only.xlsx">XLSX</a>, <a href="data/U1478_splice-values-only.csv">CSV</a></li>
				-->
			</ul>
			<h3>Plots</h3>
			<ul>
				<li><a href="../img/plot/agemodel.png">nanno plancton age model</a></li>
				<li><a href="../img/plot/screening.png">pollen density screening</a></li>
				<li><a href="../img/plot/co2.png">CO2 vs. C3/C4-ratio</a></li>
			</ul>
	'''
	return html


def print_index_page():
	html_filename = "../html/u1478.html"

	html = html_header() + html_taxo() + html_sample_list() + html_data_and_plots() + html_footer()

	# write to file
	print(html_header(),
		html_taxo(),
		html_sample_list(),
		html_data_and_plots(),
		html_footer(),
		file=open(html_filename, 'w')
		)


def html_create_protocol_list():
	html_filename = "../html/protocols.html"


	# write to file
	print(html_header(),
		html_protocols(),
		html_footer(),
		file=open(html_filename, 'w')
		)







############################################
## MATHEMATICAL AND STATISTICAL FUNCTIONS ##
############################################



# age for "x" according to five step age model based on tie points "tp"
def age(x):
	# Load tie points
	labels = ["Splice Depth (m)", "Age (Ma)", "Event"]
	tie_points_l = [
	(175.42, 1.95, "T D. triradiatus"),
	(203.59, 2.39, "T D. pentaradiatus"),
	(205.78, 2.49, "T D. surculus"),
	(221.12, 2.80, "T D. tamalis"),
	(235.23, 3.54, "T Sphenolithus spp."),
	(241.81, 3.70, "T R. pseudoumbilicus")]
	tie_points_df = pd.DataFrame.from_records(tie_points_l, columns=labels)
	tp = np.transpose(tie_points_df.drop('Event', 1).values)

	# five step age model
	if x < tp[0][1]:
		p1 = [tp[0][0], tp[0][1]]
		p2 = [tp[1][0], tp[1][1]]
		coefficients = np.polyfit(p1, p2, 1)
		polynom = np.poly1d(coefficients)
		return polynom(x)
	elif x < tp[0][2]:
		p1 = [tp[0][1], tp[0][2]]
		p2 = [tp[1][1], tp[1][2]]
		coefficients = np.polyfit(p1, p2, 1)
		polynom = np.poly1d(coefficients)
		return polynom(x)
	elif x < tp[0][3]:
		p1 = [tp[0][2], tp[0][3]]
		p2 = [tp[1][2], tp[1][3]]
		coefficients = np.polyfit(p1, p2, 1)
		polynom = np.poly1d(coefficients)
		return polynom(x)
	elif x < tp[0][4]:
		p1 = [tp[0][3], tp[0][4]]
		p2 = [tp[1][3], tp[1][4]]
		coefficients = np.polyfit(p1, p2, 1)
		polynom = np.poly1d(coefficients)
		return polynom(x)
	else:
		p1 = [tp[0][4], tp[0][5]]
		p2 = [tp[1][4], tp[1][5]]
		coefficients = np.polyfit(p1, p2, 1)
		polynom = np.poly1d(coefficients)
		return polynom(x)






####################################################
## PROGRAM STRUCTURE AND LIST RETURNING FUNCTIONS ##
####################################################



def standardprogramm(df):
	shortlist=[ # to be used for histograms and pollen plot
	"Cyperaceae",
	"Poaceae",
	"Podocarpus",
	"Asteraceae", 
	"Erica",
	"spores",
	"Chenopod",
	"Buxus spp."
	]
	picklist(df)
	print_counting(df)
	print_pollen(df, shortlist)
	print_co2(df)
	for sp in shortlist:
 		species_stat(df, sp)


def getplotablelist():
	plotable=[ # as of March 2019
		"Cyperaceae",
		 "Poaceae",
		 "Podocarpus",
		 "Asteraceae",
		 "Erica",
		 "Chenopod", 
		 "trilete spore",
		 "monolete spore",
		 "Anemia",
		 "Anthoceros",
		 "Pteris",
		 "Buxus spp.",
		 "Tylophora",
		 "Borreria spp.",
		 "Kibbeh=Anacardiaceae",
		 "Justicia",
		 "Acacia",
		 "Aloe",
		 "Plantago",
		 "Thymelaceae",
		 "Hyphaene", 
		 "Amaranth", 
		 "Pycnanthus"
		]
	return(plotable)

def getfullpollenlist():
	fullpollenlist =[
		"trilete spore",
		"monolete spore",
		"Anemia",
		"Anthoceros",
		"Pteris",
		"Cyperaceae",
		"Poaceae",
		"Podocarpus",
		"Asteraceae",
		"Erica",
		"Buxus spp.",
		"Tylophora",
		"Borreria spp.",
		"Kibbeh=Anacardiaceae",
		"Justicia",
		"Acacia",
		"Aloe",
		"Plantago",
		"Thymelaceae",
		"Hyphaene",
		"Amaranth",
		"Chenopod",
		"Merua",
		"Eremospatha",
		"periporate",
		"Rubiaceae (oderso)",
		"Combretaceae",
		"Malvaceae",
		"Dracaena",
		"Carophylaceae",
		"Rhizophora",
		"Jacaranda",
		"Brachystegia",
		"trilete tricolp",
		"cf. corylous",
		"smooth tricolp",
		"dino pollen",
		"stephanoporate",
		"fenestrate",
		"sid",
		"Pycnanthus",
		"unsorted",
		"unidentifiable"
		]
	return(fullpollenlist)








#################
###	M A I N	###
#################


def list_identifiers():
	filename = "/media/h/Volume/U1478/protocol/photospecies.csv"
	# load
	df = pd.read_table(filename, sep=',')
	ident = textload(df, "identity")

	# get every type once:
	identities = []
	for i in ident:
		if i not in identities:
			identities.append(i)
	# sort
	identities.sort(key=str.lower)

	return identities

def df_images(identity):
	filename = "/media/h/Volume/U1478/protocol/photospecies.csv"
	# load
	df = pd.read_table(filename, sep=',')

	images = []
	fitting_images = df["identity"] == identity
	images = df[fitting_images]

	return images

def list_images(identity):

	df = df_images(identity)
	images = list(df["image"])

	images_new = []
	for i in images:
		a = str(int(i))
		images_new.append(a)

	return images_new


def html_identifiers():
	# single image with overlay describing it
	def overlay_image(image, sample, rating):
		image = int(image)
		overlay_image =  '\t\t\t<div class="container">\n'
		overlay_image += '\t\t\t\t<img src="../img/' + str(sample) + '/' + str(image) + '.png">\n'
		overlay_image += '\t\t\t\t<div class="top-left">Image ' + str(image) + ", sample " +  str(sample) + ", " + str(rating) + '</div>\n'
		overlay_image += '\t\t\t</div>\n'
		return overlay_image

	# single image thumbnail item
	def thumb(image, sample, rating):
		image = int(image)
		overlay_image =  '\t\t\t<li><a href="#' + str(image) + '">'
		overlay_image += '<img src="../img/' + str(sample) + '/' + str(image) + '.png">'
		overlay_image += '<span>Image ' + str(image) + ", sample " +  str(sample) + "</span></a></li>"
		return overlay_image

	# single image slide item
	def slide(image, sample, rating, first=False):
		image = int(image)
		if first:
			overlay_image =  '\t\t\t<li class="first" id="' + str(image) + '">'
		else:
			overlay_image =  '\t\t\t<li id="' + str(image) + '">'
		overlay_image += '<img src="../img/' + str(sample) + '/' + str(image) + '.png"></li>'
		return overlay_image

	# where to write
	html_filename = "../html/identities.html"
	# load table
	filename = "/media/h/Volume/U1478/protocol/photospecies.csv"
	df = pd.read_table(filename, sep=',')
	# get list of names (without doubles)
	identifiers = list_identifiers()
	identifiers.sort()

	# html body
	hmtl_identities = "\n\n"
	for i in identifiers:
		# name
		current  = '\t<div>\n'
		current += "\t\t<h4>" + i + "</h4>\n"
		current += '\t\t<div class="scrollmenu">\n'
#		current += '<section class="container">\n'
		# images
		selection = df.loc[df.identity == i]
		for index, row in selection.iterrows():
		    current += overlay_image(row['image'], row['sample'], row['confidence'])
		current += '\t\t\t<div style="clear: both"></div>\n'
		current += '\t\t</div>\n'
		current += "\t</div>\n"
		hmtl_identities += current + " \n"
#	current += '</section>\n'


# # different approach:
# # https://www.cssscript.com/pure-css-image-slider-thumbnail-navigation/  
# 	# html body
# 	hmtl_identities = "\n\n"
# 	for i in identifiers:
# 		# name
# 		current  = '\t<div>\n'
# 		current += "\t\t<h4>" + i + "</h4>\n"

# 		current += '\t\t<ul class="thumbs">\n'
# 		selection = df.loc[df.identity == i]
# 		for index, row in selection.iterrows():
# 		    current +=  thumb(row['image'], row['sample'], row['confidence'])
# 		current += '\t\t</ul>\n'


# 		current += '\t\t<ul class="slide">\n'
# 		selection = df.loc[df.identity == i]
# 		first_child = True 
# 		for index, row in selection.iterrows():
# 		    current +=  slide(row['image'], row['sample'], row['confidence'], first=first_child)
# 		    first_child = False
# 		current += '\t\t</ul>\n'


# 		current += "\t</div>\n"
# 		hmtl_identities += current + " \n"

	# write to file
	print(html_header(),
		"\n\t<h1>Images sorted by type</h1>\n",
		hmtl_identities,
		html_footer(),
		file=open(html_filename, 'w')
		)



#print(list_images("4porate"))
#print(df_images("4porate"))


# html_identifiers()
# print_index_page()


filename = "../data/pollen/U1478.csv" 
df = pd.read_table(filename, sep=',')
print_counting(df)



# # load table, original table is ODS format. 
# # keep in mind to make a up to date CSV 
# # (if you use plot.sh, it will be generated automatically)
# filename = "../data/pollen/U1478.csv" 
# df = pd.read_table(filename, sep=',')

# html_create_protocol_list()

# # print_agemodel()

# # everybarplot(df, getfullpollenlist())


# print(singlesamplehtml("a31f3w13"))

# print_index_page()

