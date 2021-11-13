#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jieba
import synonyms
import random
from random import shuffle

random.seed(2021)

#停用词列表
f = open('stopwords/baidu_stopwords.txt', 'r', encoding='utf-8')
stop_words = list()
for stop_word in f.readlines():
    stop_words.append(stop_word[:-1])

#生成实体和类型的映射字典
entity_type = dict()
f = open('data/entity_type.txt', 'r', encoding='utf-8')
for data in f.readlines():
    data_list = data.split("\t")
    entity_type[data_list[0]] = data_list[1][0:-1]

'''
同义词替换：替换一个语句中的n个单词为其同义词，如果替换的词出现在三元组中，那么三元组也需要替换
'''
def synonym_replacement(words, n, spo_list):
    try:
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
                        new_spo_list[new_spo_list.index(spo)] = [synonym, spo[1], spo[2], spo[3], spo[4]]
                    if random_word == spo[2]:
                        new_spo_list[new_spo_list.index(spo)] = [spo[0], spo[1], synonym, spo[3], spo[4]]

            if num_replaced >= n:
                break

        sentence = ' '.join(new_words)
        new_words = sentence.split(' ')

        return new_words, new_spo_list
    except:
        return [], []

def get_synonyms(word):
    return synonyms.nearby(word)[0]


'''
随机插入：随机在非实体语句中插入n个词
'''
def random_insertion(words, n, entity_list):
    try:
        new_words = words.copy()
        for _ in range(n):
            add_word(new_words, entity_list)
        return new_words
    except:
        return []

def add_word(new_words, entity_list):
    synonyms = []
    counter = 0
    while len(synonyms) < 1:
        random_word = new_words[random.randint(0, len(new_words)-1)]
        if (random_word in entity_list) or (random_word in stop_words):
            continue
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
def random_swap(words, n, entity_list):
    try:
        new_words = words.copy()
        for _ in range(n):
            new_words = swap_word(new_words, entity_list)
        return new_words
    except:
        return []

def swap_word(new_words, entity_list):
    print(new_words)
    global random_idx_1, random_idx_2
    counter = 0
    random_idx_1 = random.randint(0, len(new_words) - 1)
    random_idx_2 = random_idx_1
    while random_idx_1 != random_idx_2:
        random_idx_2 = random.randint(0, len(new_words) - 1)
        random_word_1 = new_words[random_idx_1]
        random_word_2 = new_words[random_idx_2]
        if (random_word_1 not in entity_list) and (random_word_2 not in entity_list):
            break
        counter += 1
        if counter > 3:
            return new_words
    new_words[random_idx_1], new_words[random_idx_2] = new_words[random_idx_2], new_words[random_idx_1]
    return new_words

'''
随机删除：以概率p删除语句中的词
'''
def random_deletion(words, p, entity_list):
    try:
        if len(words) == 1:
            return words

        new_words = []
        for word in words:
            r = random.uniform(0, 1)
            if r > p:
                new_words.append(word)
            else:
                if word in entity_list:
                    new_words.append(word)
        if len(new_words) == 0:
            rand_int = random.randint(0, len(words)-1)
            return [words[rand_int]]

        return new_words
    except:
        return []

'''
EDA函数
'''
def eda_ner(sentence, spo_list, alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1, p_rd=0.1, num_aug=4):
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

    entity_list = []
    for spo in spo_list:
        entity_list.append(spo[0])
        entity_list.append(spo[2])

    #同义词替换sr
    for _ in range(num_new_per_technique):
        a_words, spo_list_new = synonym_replacement(words, n_sr, spo_list)
        if len(a_words) > 0 and len(spo_list_new) > 0 :
            augmented_sentences.append(''.join(a_words))
            spo_lists.append(spo_list_new)


    #随机插入*ri
    for _ in range(num_new_per_technique):
        a_words = random_insertion(words, n_ri, entity_list)
        if len(a_words) > 0:
            augmented_sentences.append(''.join(a_words))
            spo_lists.append(spo_list)


    #随机交换rs
    for _ in range(num_new_per_technique):
        a_words = random_swap(words, n_rs, entity_list)
        if len(a_words) > 0:
            augmented_sentences.append(''.join(a_words))
            spo_lists.append(spo_list)

    # 随机删除rd
    for _ in range(num_new_per_technique):
        a_words = random_deletion(words, p_rd, entity_list)
        if len(a_words) > 0:
            augmented_sentences.append(''.join(a_words))
            spo_lists.append(spo_list)


    if num_aug >= 1:
        augmented_sentences = augmented_sentences[:num_aug]
    else:
        keep_prob = num_aug / len(augmented_sentences)
        augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]


    #对数据增强后的样本进行去重
    sentence_set = set()

    res_augmented = []
    res_spo_list = []
    for _ in range(len(augmented_sentences)):
        augmented_sentence = augmented_sentences[_]
        spo_list = spo_lists[_]
        if augmented_sentence not in sentence_set:
            res_augmented.append(augmented_sentence)
            res_spo_list.append(spo_list)
            sentence_set.add(augmented_sentence)

    print(res_augmented)
    print(res_spo_list)
    #返回增强的文本数据res_augmented和res_spo_list
    return res_augmented, res_spo_list