#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jieba
import synonyms
import random
from random import shuffle

random.seed(2021)

#停用词列表，默认使用哈工大停用词表
f = open('stopwords/hit_stopwords.txt', 'r', encoding='utf-8')
stop_words = list()
for stop_word in f.readlines():
    stop_words.append(stop_word[:-1])


'''
同义词替换：替换一个语句中的n个单词为其同义词，如果替换的词出现在三元组中，那么三元组也需要替换
'''
def synonym_replacement(words, n, spo_list):
    new_words = words.copy()
    new_spo_list = spo_list.copy()
    random_word_list = list(set([word for word in words if word not in stop_words]))     
    random.shuffle(random_word_list)
    num_replaced = 0
    for random_word in random_word_list:          
        synonyms = get_synonyms(random_word)

        if len(synonyms) >= 1:
            num_replaced += 1

            synonym = random.choice(synonyms)   
            new_words = [synonym if word == random_word else word for word in new_words]

            for spo in new_spo_list:
                if spo[0] == random_word:
                    new_spo_list[new_spo_list.index(spo)] = [synonym, spo[1], spo[2]]
                if random_word == spo[2]:
                    new_spo_list[new_spo_list.index(spo)] = [spo[0], spo[1], synonym]

        if num_replaced >= n: 
            break

    sentence = ' '.join(new_words)
    new_words = sentence.split(' ')

    return new_words, new_spo_list


def get_synonyms(word):
    return synonyms.nearby(word)[0]


'''
EDA函数
'''
def eda_re(sentence, spo_list, alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1, p_rd=0.1, num_aug=4):
    seg_list = jieba.cut(sentence)
    seg_list = " ".join(seg_list)
    words = list(seg_list.split())
    num_words = len(words)

    augmented_sentences = []
    spo_lists = []
    num_new_per_technique = int(num_aug/4)+1
    n_sr = max(1, int(alpha_sr * num_words))
    n_ri = max(1, int(alpha_ri * num_words))
    n_rs = max(1, int(alpha_rs * num_words))


    print(num_new_per_technique)
    #同义词替换sr
    for _ in range(num_new_per_technique):
        a_words, spo_list_new = synonym_replacement(words, n_sr, spo_list)
        augmented_sentences.append(' '.join(a_words))
        spo_lists.append(spo_list_new)

    # #随机插入ri
    # for _ in range(num_new_per_technique):
    #     a_words = random_insertion(words, n_ri)
    #     augmented_sentences.append(' '.join(a_words))
    #
    # #随机交换rs
    # for _ in range(num_new_per_technique):
    #     a_words = random_swap(words, n_rs)
    #     augmented_sentences.append(' '.join(a_words))
    #
    #
    # #随机删除rd
    # for _ in range(num_new_per_technique):
    #     a_words = random_deletion(words, p_rd)
    #     augmented_sentences.append(' '.join(a_words))
    
    #print(augmented_sentences)
    # shuffle(augmented_sentences)

    if num_aug >= 1:
        augmented_sentences = augmented_sentences[:num_aug]
    else:
        keep_prob = num_aug / len(augmented_sentences)
        augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]

    augmented_sentences.append(seg_list)
    spo_lists.append(spo_list)

    return augmented_sentences, spo_lists

##
#测试用例
#eda(sentence="我们就像蒲公英，我也祈祷着能和你飞去同一片土地")














'''
随机插入：随机在语句中插入n个词
'''
def random_insertion(words, n):
    new_words = words.copy()
    for _ in range(n):
        add_word(new_words)
    return new_words

def add_word(new_words):
    synonyms = []
    counter = 0
    while len(synonyms) < 1:
        random_word = new_words[random.randint(0, len(new_words)-1)]
        synonyms = get_synonyms(random_word)
        counter += 1
        if counter >= 10:
            return
    random_synonym = random.choice(synonyms)
    random_idx = random.randint(0, len(new_words)-1)
    new_words.insert(random_idx, random_synonym)


'''
随机交换
'''
def random_swap(words, n):
    new_words = words.copy()
    for _ in range(n):
        new_words = swap_word(new_words)
    return new_words

def swap_word(new_words):
    random_idx_1 = random.randint(0, len(new_words)-1)
    random_idx_2 = random_idx_1
    counter = 0
    while random_idx_2 == random_idx_1:
        random_idx_2 = random.randint(0, len(new_words)-1)
        counter += 1
        if counter > 3:
            return new_words
    new_words[random_idx_1], new_words[random_idx_2] = new_words[random_idx_2], new_words[random_idx_1]
    return new_words

'''
随机删除：以概率p删除语句中的词
'''
def random_deletion(words, p):

    if len(words) == 1:
        return words

    new_words = []
    for word in words:
        r = random.uniform(0, 1)
        if r > p:
            new_words.append(word)

    if len(new_words) == 0:
        rand_int = random.randint(0, len(words)-1)
        return [words[rand_int]]

    return new_words