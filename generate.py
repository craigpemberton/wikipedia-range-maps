#!/usr/bin/env python

import os, math, Image, ImageDraw, ImageFont, itertools, subprocess

MAX_COLOR = (0, 32, 32)
WHITE = (255, 255, 255)

def scalarProduct(a, c):
	return map(lambda x:x*c, a)

def arraySum(a, b):
	return map(lambda x,y:x+y, a,b)

def colorIntermediate(colorOne, colorTwo, weighting):
	assert 0 <= weighting <= 1
	color = tuple(arraySum(scalarProduct(colorOne, 1-weighting), scalarProduct(colorTwo,weighting)))
	assert len(color) == 3
	return color

def gradient(steps, maxColor = MAX_COLOR):
	"""Generate a vertical gradient"""
	if steps == 1:
		return (maxColor,)
	colors = []
	minColor = colorIntermediate(maxColor, WHITE, 0.5)
	for step in range(steps):
		color = colorIntermediate(minColor, maxColor, float(step)/(steps-1))
		color = map(int, color)
		colors.append(color)
	return colors
		
def freq(items):
	counts = {}
	for item in items:
		counts[item] = counts.get(item, 0) + 1
	counts = [(val, key) for key, val in counts.items()]
	counts.sort(reverse=True)
	for key, value in counts:
		print key, '\t', value
	return counts

def verifyImage(image, filename):
	process = subprocess.Popen(['file', filename], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	fileinfo = process.communicate()[0].split(':')[1].strip()
	if fileinfo != 'PNG image data, 1480 x 625, 1-bit colormap, non-interlaced':
		raise ValueError(filename, fileinfo)

def produceMap(root, files):
	# TODO: make a report instead of missingTaxa
	images = []
	missingTaxa = []
	for file_ in files:
		filename = os.path.join(root,file_)
		image = Image.open(filename)
		try:
			if image.text['Comment'] == "INVALID":
				missingTaxa.append(file_.split('.')[0])
				continue
		except KeyError:
			print filename, "has no metadata. Exiting."
			exit()
		verifyImage(image, filename)
		images.append(image.getdata())
	diversity = map(sum, zip(*images))
	print "Generating", root
	highestDiversity = max(diversity)
	colors = gradient(highestDiversity)
	land = Image.open('world/world.png').getdata()
	rangeMap = []
	for landPixel, numCritters in zip(land, diversity):
		if landPixel == WHITE:
			rangeMap.append(WHITE)
		elif numCritters == 0:
			rangeMap.append(landPixel)
		else:
			rangeMap.append(colors[numCritters - 1])
	saveMap(rangeMap, root)
	print "Data missing for the following taxa:",
	for taxon in missingTaxa:
		print taxon + ',',
	print

def saveMap(data, taxon):
	im = Image.open('world/world.png')
	if im.getbands() != ('R', 'G', 'B'):
		raise ValueError("world.png", im.getbands())
	image = im.load()

	pixels = iter(data)
	for y in range(625):
		for x in range(1480):
				temp = pixels.next()
				try:
					image[x, y] = tuple(temp)
				except TypeError, e:
					print x, y, e, temp, type(temp)
					exit(-1)
	im.save('output/' + taxon.split('/')[-1] + '.png')

if __name__ == "__main__":
	for root, dirs, files in os.walk('Animalia'):
		if len(files) > 0:
			try:
				produceMap(root, files)
			except ValueError, e:
				print e
