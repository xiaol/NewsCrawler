# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/29
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import re
import math
import operator
from jieba.analyse import extract_tags

# from Process import analyse
from TextRank4ZH.textrank4zh import TextRank4Keyword, TextRank4Sentence

# analyse.initialize()
# analyse.load_stopdict()

class Extractor(object):

    filter_words = [
        u'\u4eca\u5929', u'\u660e\u5929', u'\u540e\u5929',          # 今天、明天、后天
        u'\u4e2d\u56fd', u'\u5168\u56fd', u'\u7f8e\u56fd',          # 中国、全国、美国
        u'\u5c0f\u65f6', u'\u539f\u8c05', u'\u6807\u9898',          # 小时、原谅、标题
    ]

    @staticmethod
    def get_tag_rule(txt, regex):
        p_tag = re.compile(regex)
        tag = p_tag.search(txt)
        tag = tag.group('tag') if tag else ''
        return tag

    @classmethod
    def extract_keywords(cls, sentence, top_k=20, with_weight=False):
        tags = []
        for eng in re.findall(r'[A-Za-z ]+', sentence):
            if len(eng) > 2:
                tags.append(eng)
        tag_rule = cls.get_tag_rule(sentence, r'.*《(?P<tag>.*)》.*')
        tag_rule_1 = cls.get_tag_rule(sentence, r'.*"(?P<tag>.*)".*')
        tags.extend(extract_tags(sentence, top_k, with_weight, allowPOS=('ns', 'n', 'nr', 'nt', 'nz')))
        tags = [x for x in tags if not x.isdigit()]
        tags = [x for x in tags if x not in cls.filter_words]
        tags = [x for x in tags if x not in tag_rule and x not in tag_rule_1]
        if len(tag_rule) > 1:
            tags.append(tag_rule)
        if len(tag_rule_1) > 1:
            tags.append(tag_rule_1)
        return tags

    @classmethod
    def extract_abstract(cls, doc, use_tf=True):
        tf_map = {}
        sorted_word = []
        word_itertor = analyse.cut_with_stop(doc)
        for word in word_itertor:
            if word in tf_map:
                tf_map[word] += 1
            else:
                tf_map[word] = 1
        if use_tf:
            sorted_word = sorted(tf_map.items(), key=operator.itemgetter(1), reverse=True)

        keywords = sorted_word[0:10]
        sentences = cls.extract_sentence_block(doc)
        sentence_score_pairs = []
        for sentence in sentences:
            sentence_score_pairs.append([sentence, cls.score_sentence(keywords, sentence)])
        sorted_sentence = sorted(sentence_score_pairs, key=operator.itemgetter(1), reverse=True)

        return sorted_sentence[0][0]

    @staticmethod
    def extract_sentence_block(doc):
        sentence_sep = re.compile(ur'[。\n!.！]')
        result = []
        doc_array = re.split(sentence_sep, doc.encode('utf8').decode("utf8"))
        for elem in doc_array:
            result.append(elem.strip())
        return result

    @staticmethod
    def score_sentence(keywords, sentence):
        word_itertor = analyse.cut_with_stop(sentence)
        score = 0.0
        count = 0
        scale = 0.5
        length_para = 0.00002
        sen_length = 0
        for word in word_itertor:
            sen_length += 1
            for keyWord in keywords:
                if word == keyWord[0]:
                    score += scale*keyWord[1]
                    count += 1
                    break
        score += count*count
        score /= (math.log(sen_length+1)+1)
        score += length_para*sen_length
        return score

class Gist(object):

    def __init__(self, stop_words_file='/work/pro/NewsCrawler/Process/TextRank4ZH/stopword.data'):
        self.stop_words_file = stop_words_file
        self.tr4w = TextRank4Keyword(self.stop_words_file)  # 导入停止词

    def get_keyword(self, text):
        self.tr4w = TextRank4Keyword(self.stop_words_file)  # Import stopwords
        # Use word class filtering，decapitalization of text，window is 2.
        self.tr4w.train(text=text, speech_tag_filter=True, lower=True, window=2)
        # 20 keywords The min length of each word is 1.
        wresult = ' '.join(self.tr4w.get_keywords(20, word_min_len=1))
        print wresult
        return wresult

    def get_keyphrase(self, text):
        self.tr4w = TextRank4Keyword(self.stop_words_file)  # Import stopwords
        # Use word class filtering，decapitalization of text，window is 2.
        self.tr4w.train(text=text, speech_tag_filter=True, lower=True, window=2)
        # Use 20 keywords for contructing phrase, the phrase occurrence in original text is at least 2.
        presult = ' '.join(self.tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2))
        print presult
        return presult

    def get_gist(self, txt=''):
        # for key, value in text_dict.iteritems():
        # # self.tr4w = TextRank4Keyword(self.stop_words_file)  # 导入停止词
        # #使用词性过滤，文本小写，窗口为2
        # self.tr4w.train(text=value, speech_tag_filter=True, lower=True, window=2)
        # # 20个关键词且每个的长度最小为1
        # self.wresult = ' '.join(self.tr4w.get_keywords(20, word_min_len=1))
        # # 20个关键词去构造短语，短语在原文本中出现次数最少为2
        # self.presult = ' '.join(self.tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2))
        tr4s = TextRank4Sentence(self.stop_words_file)
        # 使用词性过滤，文本小写，使用words_all_filters生成句子之间的相似性
        tr4s.train(text=txt, speech_tag_filter=True, lower=True, source='all_filters')
        gresult = ' '.join(tr4s.get_key_sentences(num=1))
        print gresult

        return gresult or None
