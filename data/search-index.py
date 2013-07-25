#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Christopher stoll, City of Barberton, 2013
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# <http://www.gnu.org/licenses/>.

import glob, re, html2text, nltk

# from NLTK book examples
# (actually a cascaded finite-state transducer)
def cfst(text_raw, text_parser_a):
	# TOKENIZATION: split into sentences
	text_sentences = nltk.sent_tokenize(text_raw)
	# TOKENIZATION: split into words
	text_words = [nltk.word_tokenize(sent) for sent in text_sentences]
	# TOKENIZATION: tag the words' part of speach
	text_posed = [nltk.pos_tag(sent) for sent in text_words]
	# BASIC-GROUP HANDLING: chunk the words at named entities
	text_chunked = nltk.batch_ne_chunk(text_posed)#[nltk.chunk.ne_chunk(sent) for sent in text_cleaned]
	# COMPLEX-PHRASE HANDLING: chunk the words
	text_chunked = [text_parser_a.parse(sent) for sent in text_chunked]
	# unwind the tree only keeping interesting parts
	text_done = []
	for sent in text_chunked:
		for x in xrange(0, len(sent)):
			tmp_string = str(sent[x])
			if tmp_string.startswith('(NP') or tmp_string.startswith('(VP'):
				text_frag = []
				for y in xrange(0, len(sent[x])):
					word = sent[x][y]
					if len(word) == 2:
						if len(word[0][0]) > 1:
							for sub_word in word:
								if len(sub_word[0]) > 0:
									text_frag.append(str(sub_word[0]).lower())
						else:
							if len(word[0]) > 0:
								text_frag.append(str(word[0]).lower())
					elif len(word) > 2:
						for sub_word in word:
							if len(sub_word[0]) > 0:
								text_frag.append(str(sub_word[0]).lower())
				if (len(text_frag) > 0):
					text_done.append(' '.join(text_frag))
	
	# remove duplicate phrases
	text_dictionary = {}
	for word in text_done:
		text_dictionary[word] = 1
	return ' '.join(text_dictionary)


def get_pagetext(file_name):
	parser_grammar_a = r"""
		NP: {<NN|NNS|PERSON><CC><NN|NNS|PERSON>}
		NP: {<JJ|ORGANIZATION|PERSON|NN.*>+}
		VP: {<RB|VB|VBD|VBG|VBN|VBP>+}
		"""
	text_parser_a = nltk.RegexpParser(parser_grammar_a, loop=1)

	with open(file_name, 'r') as file_source:
		# read the file
		file_contents = file_source.read().decode('utf8').strip()
		if file_contents:
			# convert html to markdown
			h = html2text.HTML2Text()
			h.ignore_links = True
			h.ignore_images = True
			file_contents = h.handle(file_contents).strip()
			if file_contents:
				# remove unicode troublemakers
				file_contents = re.sub(u'[’‘‹›™»]', '', file_contents)
				file_contents = re.sub(u'[“”]', '"', file_contents)
				file_contents = re.sub(u'[–—]', '-', file_contents)
				file_contents = re.sub(u'[é]', 'e', file_contents)
				file_contents = re.sub(u'[×]', 'x', file_contents)
				# remove markup
				file_contents = re.sub('(_){2,}', '', file_contents)
				file_contents = re.sub('\*+', '', file_contents)
				# parse the text using NLTK
				file_contents = cfst(file_contents, text_parser_a)
				file_contents = file_contents.strip()
				if file_contents:
					# remove cruft
					file_contents = ' ' + file_contents + ' '
					file_contents = re.sub('[%\(\)]', '', file_contents)
					file_contents = re.sub('( x){2,}', '', file_contents)
					file_contents = re.sub(' x ', ' ', file_contents)
					file_contents = re.sub(' am ', ' ', file_contents)
					file_contents = re.sub(' pm ', ' ', file_contents)
					file_contents = re.sub(' a.m. ', ' ', file_contents)
					file_contents = re.sub(' p.m. ', ' ', file_contents)
					file_contents = re.sub(' oh ', ' ', file_contents)
					file_contents = re.sub(' w ', ' ', file_contents)
					file_contents = re.sub(' rd ', ' ', file_contents)
					file_contents = re.sub(' ave ', ' ', file_contents)
					file_contents = re.sub(' tty ', ' ', file_contents)
					file_contents = re.sub(' m-f ', ' ', file_contents)
					file_contents = re.sub(' fax ', ' ', file_contents)
					file_contents = re.sub(' email ', ' ', file_contents)
					file_contents = re.sub('website ', '', file_contents)
					file_contents = re.sub('phone numbers ', '', file_contents)
					file_contents = re.sub('business hours ', '', file_contents)
					file_contents = re.sub(' & ', ' ', file_contents)
					file_contents = re.sub('["\']', '', file_contents)

		return file_contents.strip()


def get_pagetitle(file_name):
	page_title = ''
	f = open(file_name, 'r')
	for line in f:
		if re.search('<div class="page-header">', line):
			page_title = re.sub('<.+?(>)', '', line)
			page_title = re.sub('^[ \t]+', '', page_title)
			page_title = re.sub('[\n]', '', page_title)
			break
	f.close()

	if not page_title:
		page_title = re.sub('_', ' ', re.sub('\.shtml$', '', re.sub('^\.\./', '', file_name))).title()

	return page_title


def get_phonenumbers(file_name):
	page_phones = []
	page_phonedesc = ''
	page_phonenumb = ''
	f = open(file_name, 'r')
	for line in f:
		if re.search('<td>.+</td>', line):
			#if re.search('[0-9]', line):
			if not re.search('911', line):
				page_phonedesc = re.sub('<td.*?>', '', line)
				page_phonedesc = re.sub('</td>.*', '', page_phonedesc)
				page_phonedesc = re.sub('<.*?>', ' ', page_phonedesc)
				#print line.strip()
				
				page_phonenumb = re.sub('.*</td><td.*?>', '', line)
				page_phonenumb = re.sub('<.*?>', '', page_phonenumb)
				#print page_phonenumb.strip()
				#print
				page_phones.append(str(page_phonedesc.strip() + '<br>&nbsp; ' + page_phonenumb.strip() + ' '))
	f.close()
	return page_phones


if __name__ == "__main__":
	contact_source = '../lib/includes/contact_*.html'
	pages_source = '../*.shtml'
	file_pages = 'search-pages.json'
	file_keywords = 'search-keywords.json'
	
	tempnumbers = []
	phonenumbers = []
	page_text = ''
	pagesjson = []
	keywordsjson = []

	filenames = list(glob.glob(contact_source))
	for i, filename in enumerate(filenames):
		print filename,
		phonenumbers = get_phonenumbers(filename)
		for number in phonenumbers:
			jsonline  = '"%s":["0"]' % (number)
			keywordsjson.append(jsonline)
		print(' ... \033[0;32mOK\033[0m')

	jsonline  = '"0":{"name":"PHONENUMBER","path":"PHONENUMBER"}'
	pagesjson.append(jsonline)

	filenames = list(glob.glob(pages_source))
	for i, filename in enumerate(filenames):
		if filename != '../404.shtml':
			print(filename),
			page_text = get_pagetext(filename)
			if page_text:
				if len(page_text) > 16 and len(page_text) < 2400:
					jsonline  = '"%d":{' % (i+1)
					jsonline += '"name":"%s",' % (get_pagetitle(filename))
					jsonline += '"path":"%s"' % (re.sub('^\.\./', '', filename))
					jsonline += '}'
					pagesjson.append(jsonline)

					jsonline  = '"%s":["%d"]' % (page_text, i+1)
					keywordsjson.append(jsonline)

					print(' ... \033[0;32mOK (%d)\033[0m') % (len(page_text))
				else:
					print(' ... \033[0;31mSKIP (%d)\033[0m') % (len(page_text))
			else:
				print(' ... \033[0;31mBLANK\033[0m')
	
	f = open(file_pages, 'w')
	f.write('{')
	f.write(','.join(str(jsonline) for jsonline in pagesjson))
	f.write('}')
	f.close()

	f = open(file_keywords, 'w')
	f.write('{')
	f.write(','.join(str(jsonline) for jsonline in keywordsjson))
	f.write('}')
	f.close()
