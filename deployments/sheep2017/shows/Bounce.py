#
# Bounce
#
# Show draws 3 balls that bounce horizontally
# 
# Background is black
#
# Starting ball color is random
#
# Ball color can get controlled by Touch OSC
# If OSC is not used, balls slowly changes color
# 

import sheep
import time
from random import randint, choice
from color import RGB, HSV
            
# Converts a 0-1536 color into rgb on a wheel by keeping one of the rgb channels off

def Wheel(color):
	color = color % 1536  # just in case color is out of bounds
	channel = color / 255
	value = color % 255
	
	if channel == 0:
		r = 255
		g = value
		b = 0
	elif channel == 1:
		r = 255 - value
		g = 255
		b = 0
	elif channel == 2:
		r = 0
		g = 255
		b = value
	elif channel == 3:
		r = 0
		g = 255 - value
		b = 255
	elif channel == 4:
		r = value
		g = 0
		b = 255
	else:
		r = 255
		g = 0
		b = 255 - value
	
	return RGB(r,g,b)

# Interpolates between colors. Fract = 1 is all color 2
def morph_color(color1, color2, fract):
	morph_h = color1.h + ((color2.h - color1.h) * fract)
	morph_s = color1.s + ((color2.s - color1.s) * fract)
	morph_v = color1.v + ((color2.v - color1.v) * fract)
	
	return HSV(morph_h, morph_s, morph_v)
	
class Fader(object):
	def __init__(self, sheep, cell, decay):
		self.sheep = sheep
		self.cell = cell
		self.decay = decay
		self.life = 1.0
	
	def draw_fader(self, fore_color, back_color):
		adj_color = morph_color(back_color, fore_color, self.life)
		self.sheep.set_cell(self.cell, adj_color)
	
	def age_fader(self):
		self.life -= self.decay
		if self.life > 0:
			return True	# Still alive
		else:
			return False	# Life less than zero -> Kill

class Path(object):
	def __init__(self, sheep, trajectory):
		self.sheep = sheep
		self.faders = []	# List that holds fader objects
		self.pos = 0	# Where along the sheep
		self.dir = 1	# 1 or -1 for left or right
		self.decay = 1.0 / randint(2,8)	# Trail length
		self.trajectory = trajectory				
		
	def draw_path(self, foreground, background):
		for f in self.faders:
			f.draw_fader(foreground, background)
		for f in self.faders:
			if f.age_fader() == False:
				self.faders.remove(f)
	
	def move_path(self):
		self.pos += self.dir
		if self.pos <= 0 or self.pos >= len(self.trajectory) - 1:
			self.dir *= -1	# Flip direction: bounce

		new_fader = Fader(self.sheep, self.trajectory[self.pos], self.decay)
		self.faders.append(new_fader)
		
		if randint(1,30) == 1:
			self.decay = 1.0 / randint(2,8)	# Change trail length
		
class Bounce(object):
	def __init__(self, sheep_sides):
		self.name = "Bounce"
		self.sheep = sheep_sides.both
		self.paths = []	# List that holds paths objects
		self.trajectories = (sheep.LOW, sheep.MEDIUM, sheep.HIGH)
		self.background  = RGB(0,0,0) # Always Black
		
		self.last_osc = time.time()
		
		self.OSC = False	# Is Touch OSC working?
		self.noOSCcolor = randint(0,1536)	# Default color if no Touch OSC
		self.OSCcolor = Wheel(self.noOSCcolor)
		
		# Set up 3 balls on low, medium, and high levels
		
		for i in range(3):
			new_path = Path(self.sheep, self.trajectories[i])
			self.paths.append(new_path)
			
		self.speed = 0.2
		
	def set_param(self, name, val):
		# name will be 'colorR', 'colorG', 'colorB'
		rgb255 = int(val * 0xff)
		if name == 'colorR':
			self.OSCcolor.r = rgb255
			self.last_osc = time.time()
			self.OSC = True
		elif name == 'colorG':
			self.OSCcolor.g = rgb255
			self.last_osc = time.time()
			self.OSC = True
		elif name == 'colorB':
			self.OSCcolor.b = rgb255
			self.last_osc = time.time()
			self.OSC = True
							
	def next_frame(self):	
					
		while (True):
			
			# Set background cells
			
			self.sheep.set_all_cells(self.background)						
			
			# Which color to use for balls?
			
			if self.OSC:	# Which color to use?
				adj_color = self.OSCcolor.copy()
			else:
				adj_color = Wheel(self.noOSCcolor)
			
			# Draw paths
				
			for p in self.paths:
				p.draw_path(adj_color, self.background)
				p.move_path()
			
			# Change the ball color
				
			if time.time() - self.last_osc > 120:	# 2 minutes
				self.OSC == False
				
			if self.OSC == False:
				self.noOSCcolor += 1
				if self.noOSCcolor > 1536:
					self.noOSCcolor -= 1536
			
			yield self.speed