""" WordData DicoDeLaZone Parser module """

import re
import bs4

import ratpy

# ############################################################### #
# ############################################################### #


class Parser(ratpy.Linker):

    # ####################################################### #
    # ####################################################### #

    def parse_infos(self, url):
        return {
            'id': url.split('/')[-1],
            'url': url
        }

    # ####################################################### #

    def parse_content(self, content):
        return content.find('div', class_='row-definition').find('div', class_='panel-body')

    def parse_word_etymology(self, content):
        try:
            return self.parse_content(content).find('div', class_='etymology').getText().replace('étym.', '')
        except:
            pass
        return ''

    # ####################################################### #

    def parse_usages(self, _x):
        pass

    def parse_usage_word(self, usage):
        pass

    def parse_usage_type(self, usage):
        pass

    def parse_word(self, content):
        return self.parse_content(content).find('dl').findAll('dt')[-1].find('span').getText()

    # ####################################################### #

    def parse_meanings(self, content):
        res = self.parse_content(content).findAll('dd')
        tmp = content.find('html').findNextSibling('dd')
        if tmp:
            res.append(tmp)
        return res

    def parse_meaning_type(self, meaning):
        try:
            return meaning.findPreviousSibling('dt').findAll('span', class_=None)[1].getText().replace('.', '')
        except:
            pass
        try:
            return self.parse_content(meaning.findPreviousSibling()).findAll('dd')[-1].findNextSibling('span').getText().replace('.', '')
        except:
            pass
        return ''

    def parse_meaning_definition(self, meaning):
        res = meaning.find('p').getText()
        res = re.sub(r'[\t\n]', '', res)
        res = re.sub(r'^[1-9]\.', '', res)
        res = re.sub(r'Syn\.[-,\w]+\.$', '', res)
        return res.strip()

    def parse_meaning_synonyms(self, meaning):
        x = re.sub(r'[\t\n]', '', meaning.find('p').getText())
        search = re.search(r'Syn\.[-,\w]+\.$', x)
        if search:
            return x[search.start()+4:].replace('.', '').split(',')
        else:
            return []

    # ####################################################### #

    def parse_examples(self, meaning):
        return meaning.findAll('p', class_='example')

    def parse_example_citation(self, example):
        try:
            return re.sub(r'[\t\n]', '', example.find('span').getText()).strip()
        except:
            return ''

    def parse_example_author(self, example):
        try:
            search = example.find('span', class_='author-media').findAll('a')
            return search[0].getText() if search else None
        except:
            return None

    def parse_example_container1(self, example):
        try:
            tmp = example.find('span', class_='author-media')
            search = re.search(r'«.*»', tmp.getText())
            return tmp.getText()[search.start():search.end()] if search else None
        except:
            return None

    def parse_example_container2(self, example):
        try:
            search = example.find('span', class_='author-media').findAll('i')
            return search[-1].getText() if search else None
        except:
            return None

    def parse_example_date(self, example):
        try:
            tmp = example.find('span', class_='author-media')
            search = re.search(r'\d{4}\)$', tmp.getText())
            return tmp.getText()[search.start():search.end() - 1] if search else None
        except:
            return None

    # ####################################################### #
    # ####################################################### #

# ############################################################### #
# ############################################################### #

