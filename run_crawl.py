# -*- coding: utf-8 -*-
from crawl_util import *
import sys, getopt

def main(argv):

	if len(argv) != 2:
		print 'python run_crawl.py  -i <nameInputFile> '
	inputfile = str(argv[1])
	words = open(inputfile,'r').readlines()
	for w in words:
		w = w.strip()

		username = w
		main_file_name = "result/main_page_info_"+username+".json"
		detail_file_name = "result/detail_page_info_"+username+".json"
		mainPageOutput = open(main_file_name, "w")
		detailPageOutput = open(detail_file_name, "w")
		crawler_exe(username,mainPageOutput,detailPageOutput)

		mainPageOutput.close()
		detailPageOutput.close()

		print "crawling complete"

if __name__ == '__main__':
    main(sys.argv[1:])