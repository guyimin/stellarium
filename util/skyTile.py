#!/usr/bin/python
# Fabien Chereau fchereau@eso.org

import sys
import os
import math
import gzip

def writePolys(pl, f):
	"""Write a list of polygons pl into the file f.
	The result is under the form [[[ra1, de1],[ra2, de2],[ra3, de3],[ra4, de4]], [[ra1, de1],[ra2, de2],[ra3, de3]]]"""
	f.write('[')
	for idx,poly in enumerate(pl):
		f.write('[')
		for iv,v in enumerate(poly):
			f.write('[%.8f, %.8f]' % (v[0], v[1]))
			if iv!=len(poly)-1:
				f.write(', ')
		f.write(']')
		if idx!=len(pl)-1:
			f.write(', ')
	f.write(']')

class StructCredits:
	def __init__(self):
		self.short = None;
		self.full = None;
		self.infoUrl = None;
		return


class SkyImageTile:
	"""Contains all the properties needed to describe a multiresolution image tile"""
	def __init__(self):
		self.subTiles = []
		self.imageCredits = StructCredits()
		self.serverCredits = StructCredits()
		self.imageInfo = StructCredits()
		self.imageUrl = None
		self.maxBrightness = None
		return
	
	def outputJSON(self, prefix='', qCompress=False, maxLevelPerFile=10, outDir=''):
		"""Output the tiles tree in the JSON format"""
		fName = outDir+prefix+"x%.2d_%.2d_%.2d.json" % (2**self.level, self.i, self.j)
		
		# Actually write the file with maxLevelPerFile level
		f = open(fName, 'w')
		self.__subOutJSON(prefix, qCompress, maxLevelPerFile, f, 0, outDir)
		f.close()
		
		if (qCompress):
			ff = open(fName)
			fout = gzip.GzipFile(fName+".gz", 'w')
			fout.write(ff.read())
			fout.close()
			os.remove(fName)

	def __subOutJSON(self, prefix, qCompress, maxLevelPerFile, f, curLev, outDir):
		"""Write the tile in the file f"""
		levTab = ""
		for i in range(0,curLev):
			levTab += '\t'
		
		f.write(levTab+'{\n')
		if self.imageInfo.short!=None or self.imageInfo.full!=None or self.imageInfo.infoUrl!=None:
			f.write(levTab+'\t"imageInfo": {\n')
			if self.imageInfo.short!=None:
				f.write(levTab+'\t\t"short": '+self.imageInfo.short+',\n')
			if self.imageInfo.full!=None:
				f.write(levTab+'\t\t"full": '+self.imageInfo.full+',\n')
			if self.imageInfo.infoUrl!=None:
				f.write(levTab+'\t\t"infoUrl": '+self.imageInfo.infoUrl+',\n')
			f.write(levTab+'\t}\n')
		if self.imageCredits.short!=None or self.imageCredits.full!=None or self.imageCredits.infoUrl!=None:
			f.write(levTab+'\t"imageCredits": {\n')
			if self.imageCredits.short!=None:
				f.write(levTab+'\t\t"short": '+self.imageCredits.short+',\n')
			if self.imageCredits.full!=None:
				f.write(levTab+'\t\t"full": '+self.imageCredits.full+',\n')
			if self.imageCredits.infoUrl!=None:
				f.write(levTab+'\t\t"infoUrl": '+self.imageCredits.infoUrl+',\n')
			f.write(levTab+'\t}\n')
		if self.serverCredits.short!=None or self.serverCredits.full!=None or self.serverCredits.infoUrl!=None:
			f.write(levTab+'\t"serverCredits": {\n')
			if self.serverCredits.short!=None:
				f.write(levTab+'\t\t"short": '+self.serverCredits.short+',\n')
			if self.serverCredits.full!=None:
				f.write(levTab+'\t\t"full": '+self.serverCredits.full+',\n')
			if self.serverCredits.infoUrl!=None:
				f.write(levTab+'\t\t"infoUrl": '+self.serverCredits.infoUrl+',\n')
			f.write(levTab+'\t}\n')
		if self.imageUrl:
			f.write(levTab+'\t"imageUrl": "'+self.imageUrl+'",\n')
		f.write(levTab+'\t"worldCoords": ')
		writePolys(self.skyConvexPolygons, f)
		f.write(',\n')
		f.write(levTab+'\t"textureCoords": ')
		writePolys(self.textureCoords, f)
		f.write(',\n')
		if self.maxBrightness:
			f.write(levTab+'\t"maxBrightness": %f,\n' % self.maxBrightness)
		f.write(levTab+'\t"minResolution": %f' % self.minResolution)
		if len(self.subTiles)==0:
			f.write('\n'+levTab+'}')
			return
		f.write(',\n')
		f.write(levTab+'\t"subTiles": [\n')
		
		if curLev+1<maxLevelPerFile:
			# Write the tiles in the same file
			for st in self.subTiles:
				assert isinstance(st, SkyImageTile)
				st.__subOutJSON(prefix, qCompress, maxLevelPerFile, f, curLev+1, outDir)
				f.write(',\n')
		else:
			# Write the tiles in a new file
			for st in self.subTiles:
				st.outputJSON(prefix, qCompress, maxLevelPerFile, outDir)
				f.write(levTab+'\t\t{"$ref": "'+prefix+"x%.2d_%.2d_%.2d.json" % (2**st.level, st.i, st.j))
				if qCompress:
					f.write(".gz")
				f.write('"},\n')
		f.seek(-2, os.SEEK_CUR)
		f.write('\n'+levTab+'\t]\n')
		f.write(levTab+'}')
