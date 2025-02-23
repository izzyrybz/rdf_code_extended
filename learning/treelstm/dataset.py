import os
import json
from tqdm import tqdm
from copy import deepcopy

import torch
import torch.utils.data as data

import learning.treelstm.Constants as Constants
from learning.treelstm.tree import Tree
from learning.treelstm.vocab import Vocab


class QGDataset(data.Dataset):
    def __init__(self, path, vocab, num_classes):
        super(QGDataset, self).__init__()
        self.vocab = vocab
        self.num_classes = num_classes

        #a.toks is the sentence with entities with ent b.toks is the representing items in the sparql query
        self.lsentences = self.read_sentences(os.path.join(path, 'a.toks'))
        self.rsentences = self.read_sentences(os.path.join(path, 'b.toks'))

        #a/b.parents is the tree noted with 0 as root and then i belive it is the layers
        #okay so if I self.rtrees = self.read_trees(os.path.join('learning/treelstm/data/lc_quad/train/', 'a.parents'))
        self.ltrees = self.read_trees(os.path.join(path, 'a.parents'))
        self.rtrees = self.read_trees(os.path.join(path, 'b.parents'))

        self.labels = self.read_labels(os.path.join(path, 'sim.txt'))

        
            

        self.size = len(self.lsentences)

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        ltree = deepcopy(self.ltrees[index])
        rtree = deepcopy(self.rtrees[index])
        lsent = deepcopy(self.lsentences[index])
        rsent = deepcopy(self.rsentences[index])
        label = deepcopy(self.labels[index])
        return (ltree, lsent, rtree, rsent, label)

    def read_sentences(self, filename):
        with open(filename, 'r') as f:
            sentences = [self.read_sentence(line) for line in tqdm(f.readlines())]
        return sentences

    def read_sentence(self, line):
        new_line=''

        for word in line.split():
            #print("this is word",word)
            if('http://example.org/ontology/' in word):
                word= word.replace('http://example.org/ontology/','')
                word=word.replace('<','')
                word=word.replace('>','')
            elif('http://example.org/action/' in word):
                word=word.replace('http://example.org/action/','')
                word=word.replace('<','')
                word=word.replace('>','')
            elif('http://example.org/entity/' in word):
                word=word.replace('http://example.org/entity/','')
                word=word.replace('<','')
                word=word.replace('>','')
            
            
   
            new_line += word + " "
        new_line = new_line.strip()
       
        #print("this is new line",new_line.split())
   

        indices=self.vocab.convertToIdx(new_line.split(), Constants.UNK_WORD)
        #print("this is indices",indices)
        #print("we are taking this line:", new_line,"and tunring it into this tensor",torch.LongTensor(indices))
        with open('trash.txt', 'a') as f:
                f.write(f"\nread_sentence in dataset LINE: {new_line}\n")
                f.write(f"turning it into this tensor: {torch.LongTensor(indices)}\n")
        return torch.LongTensor(indices)

    def read_trees(self, filename):
        with open(filename, 'r') as f:
            trees = [self.read_tree(line) for line in tqdm(f.readlines())]
        return trees

    def read_tree(self, line):
        #print("LINE",line)
        parents = list(map(int, line.split()))
        trees = dict()
        root = None
        for i in range(1, len(parents) + 1):
            if i - 1 not in trees.keys() and parents[i - 1] != -1:
                #print("THIS IS TREE KEYS",trees.keys())
                idx = i
                prev = None
                while True:
                    parent = parents[idx - 1]
                    #print("this is parent",parent)
                    if parent == -1:
                        break
                    tree = Tree()
                    if prev is not None:
                        tree.add_child(prev)
                    trees[idx - 1] = tree
                    tree.idx = idx - 1
                    if parent - 1 in trees.keys():
                        trees[parent - 1].add_child(tree)
                        break
                    elif parent == 0:
                        root = tree
                        break
                    else:
                        prev = tree
                        idx = parent
        return root

    def read_labels(self, filename):
        with open(filename, 'r') as f:
            labels = list(map(lambda x: float(x), f.readlines()))
            labels = torch.Tensor(labels)
        return labels
