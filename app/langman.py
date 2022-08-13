# -*- coding: utf-8 -*-
import spacy_thai
import graphviz
import deplacy
from pythainlp.translate import EnThTranslator, ThEnTranslator

from pythainlp.tokenize import word_tokenize
from pythainlp.tag import pos_tag
from pythainlp.tag import chunk_parse
from nltk.chunk import conlltags2tree
import svgling



nlp=spacy_thai.load()


def test(txt):
    m = [(w,t) for w,t in pos_tag(word_tokenize(txt), engine= 'perceptron',corpus = 'orchid')]
    tag = chunk_parse(m)
    p = [(w,t,tag[i]) for i,(w,t) in enumerate(m)]
    return p


def test1(msg):
    doc = nlp(msg)
    print(dir(doc))
    graphviz.Source(deplacy.dot(doc))

if __name__ == "__main__":
    test1("ทุเรียนหมอนทองขายยังไง")
    print(ThEnTranslator().translate("ผมอยากเขียนโปรแกรมคอมพิวเตอร์"))

    t = svgling.draw_tree(conlltags2tree(test("หมอเล็กอยากกินทุเรียนหมอนทอง")))
    t.get_svg().saveas("test.svg")
