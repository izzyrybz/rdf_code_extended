import json
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable as Var
import sys
path = os.getcwd()
print('path: ', path)
sys.path.insert(0, path)
import learning.treelstm.Constants as Constants
# sys.path.insert(0,'/cluster/home/xlig/qg')


# module for childsumtreelstm
class ChildSumTreeLSTM(nn.Module):
    def __init__(self, in_dim, mem_dim):
        super(ChildSumTreeLSTM, self).__init__()
        self.in_dim = in_dim
        self.mem_dim = mem_dim
        self.ioux = nn.Linear(self.in_dim, 3 * self.mem_dim)
        self.iouh = nn.Linear(self.mem_dim, 3 * self.mem_dim)
        self.fx = nn.Linear(self.in_dim, self.mem_dim)
        self.fh = nn.Linear(self.mem_dim, self.mem_dim)

    def node_forward(self, inputs, child_c, child_h):
        child_h_sum = torch.sum(child_h, dim=0, keepdim=True)

        iou = self.ioux(inputs) + self.iouh(child_h_sum)
        i, o, u = torch.split(iou, iou.size(1) // 3, dim=1)
        # i = input gate
        # o = output gate 
        # u =gradient?
        i, o, u = torch.sigmoid(i), torch.sigmoid(o), torch.tanh(u)
        
        #f = forget gate

        f = torch.sigmoid(
            self.fh(child_h) +
            self.fx(inputs).repeat(len(child_h), 1)
        )
        fc = torch.mul(f, child_c)

        #c = memory cell
        c = torch.mul(i, u) + torch.sum(fc, dim=0, keepdim=True)
        h = torch.mul(o, torch.tanh(c))

        '''
        with open("trash.txt","w") as fp:
        json_str = json.dumps((i.detach().numpy().tolist()  ,"\n",":input gate",o.detach().numpy().tolist() ,"\n",":output gate",u.detach().numpy().tolist(),"\n",":gradient",f.detach().numpy().tolist() ,"\n", ":forget gate",c.detach().numpy().tolist()  ,"\n",":memorycell",h.detach().numpy().tolist()  ,"hidden state"))
        fp.write(json_str )
        '''        
        return c, h
    

    def forward(self, tree, inputs):
        #print("WE ARE IN ChildSumTreeLSTM")

        _ = [self.forward(tree.children[idx], inputs) for idx in range(tree.num_children)]
        

        if tree.num_children == 0:
            child_c = Var(inputs[0].data.new(1, self.mem_dim).fill_(0.))
            child_h = Var(inputs[0].data.new(1, self.mem_dim).fill_(0.))
        else:
            child_c, child_h = zip(*map(lambda x: x.state, tree.children))
            child_c, child_h = torch.cat(child_c, dim=0), torch.cat(child_h, dim=0)

        if tree.idx >= len(inputs):
            # handle the case where tree.idx is out of bounds
            tree.state = self.node_forward(torch.zeros_like(inputs[0]), child_c, child_h)
        else:
            tree.state = self.node_forward(inputs[tree.idx], child_c, child_h)

        #print("WE ARE IN ChildSumTreeLSTM and this out tree state",tree.state)
        return tree.state
    


# module for distance-angle similarity
class DASimilarity(nn.Module):
    def __init__(self, mem_dim, hidden_dim, num_classes):
        super(DASimilarity, self).__init__()
        self.mem_dim = mem_dim
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes
        self.wh = nn.Linear(2 * self.mem_dim, self.hidden_dim)
        self.wp = nn.Linear(self.hidden_dim, self.num_classes)

    def forward(self, lvec, rvec):
        mult_dist = torch.mul(lvec, rvec)
        #the two vectors are the same
        #print("WE ARE IN DASIMILARYI")
        abs_dist = torch.abs(torch.add(lvec, -rvec))
        vec_dist = torch.cat((mult_dist, abs_dist), 1)

        vec_dist = F.dropout(vec_dist, p=0.2, training=self.training)
        out = torch.sigmoid(self.wh(vec_dist))
        out = F.log_softmax(self.wp(out),dim=1)
        #print("WE ARE IN DASIMILARYI OUTOUT",out)
        
        return out


# module for cosine similarity
class CosSimilarity(nn.Module):
    def __init__(self, mem_dim):
        super(CosSimilarity, self).__init__()
        self.cos = nn.CosineSimilarity(dim=mem_dim)

    def forward(self, lvec, rvec):
        #print("CosSimilarity")
        out = self.cos(lvec, rvec)
        out = torch.autograd.Variable(torch.FloatTensor([[1 - out.data[0], out.data[0]]]), requires_grad=True)
        if torch.cuda.is_available():
            out = out.cuda()
        return F.log_softmax(out)


# putting the whole model together
class SimilarityTreeLSTM(nn.Module):
    def __init__(self, vocab_size, in_dim, mem_dim, similarity, sparsity):
        super(SimilarityTreeLSTM, self).__init__()
        self.emb = nn.Embedding(vocab_size, in_dim, padding_idx=Constants.PAD, sparse=sparsity)
        self.childsumtreelstm = ChildSumTreeLSTM(in_dim, mem_dim)
        self.similarity = similarity
    

    def forward(self, ltree, linputs, rtree, rinputs):
        #print("We are in SimilarityTreeLSTM")
        linputs = self.emb(linputs)
        rinputs = self.emb(rinputs)
        lstate, lhidden = self.childsumtreelstm(ltree, linputs)
        rstate, rhidden = self.childsumtreelstm(rtree, rinputs)
        #print(rstate, rhidden,lstate, lhidden)
        output = self.similarity(lstate, rstate)
        #print("this is We are in SimilarityTreeLSTM output",output)
        return output
