#!/usr/bin/env python
import os
import sys

""" TODO: need to improve this script to do regex matching on wiki page names,
and sort the pages by type and in chronological order + Misc/uncategorized """

INDEXFILE = 'Pages.wiki'
INDEXTITLE = '= INDEX ='

def get_wiki_pages_among_files(fileslist):
	#wikipages = filter(lambda(thisfile): thisfile[-5:]=='.wiki', fileslist)
	return [thisfile[:-5] for thisfile in fileslist if thisfile[-5:]=='.wiki']

def update_index(plannerpath, indexfile=None, indextitle=None):
	if not indexfile:
		indexfile = INDEXFILE
	if not indextitle:
		indextitle = INDEXTITLE
	fileslist = os.listdir(plannerpath)
	wikipages = get_wiki_pages_among_files(fileslist)
	#print "%d wiki pages found: %s" % (len(wikipages), str(wikipages))
	indexfilename = '%s/%s' % (plannerpath, indexfile)
	wikiindex = open(indexfilename, 'w')
	wikiindex.write(indextitle + '\n')
	for page in wikipages:
		wikiindex.write('\t* [[' + page + ']]\n')
	wikiindex.close()

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print '\nUsage: "./updateindex.py <WIKI/PATH> <-f Index filename> <-t Index title>"\n'
		exit(0)
	else:
		args = [sys.argv[1]]
		wikidir = args[0]
		wikidir = wikidir.rstrip('/')
		if len(sys.argv) > 2: args.append(sys.argv[2:4])
		if len(sys.argv) > 3: args.append(sys.argv[4:6])
		(indexfile, indextitle) = (None, None)
		for arg in args[1:]:
			if arg[0] == '-f': indexfile = arg[1]
			if arg[0] == '-t': indextitle = arg[1]
	print
	print ">>> Operating on wiki at location: %s <<<" % wikidir
	print

	update_index(wikidir, indexfile, indextitle)
