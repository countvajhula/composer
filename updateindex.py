#!/usr/bin/env python
import os
import sys

""" TODO: need to improve this script to do regex matching on wiki page names,
and sort the pages by type and in chronological order + Misc/uncategorized """

WIKIDIR='..'
INDEXFILE='Pages.wiki'

def get_wiki_pages_among_files(fileslist):
	#wikipages = filter(lambda(thisfile): thisfile[-5:]=='.wiki', fileslist)
	return [thisfile[:-5] for thisfile in fileslist if thisfile[-5:]=='.wiki']

def update_index(plannerpath):
	fileslist = os.listdir(plannerpath)
	wikipages = get_wiki_pages_among_files(fileslist)
	#print "%d wiki pages found: %s" % (len(wikipages), str(wikipages))
	indexfilename = '%s/%s' % (plannerpath, INDEXFILE)
	wikiindex = open(indexfilename, 'w')
	wikiindex.write('= INDEX =\n')
	for page in wikipages:
		wikiindex.write('\t* [[' + page + ']]\n')
	wikiindex.close()

if __name__ == '__main__':
	update_index(WIKIDIR)
