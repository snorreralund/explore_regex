import networkx as nx
import re
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
def get_span_overlap(span,span2):
        return min([span[1],span2[1]])-max([span[0],span2[0]])

class ExploreRegex():
    """This module should allow you to compare the differences between different regular expressions.
    """
    def __init__(self,sample_string):
        self.string = sample_string
        self.pattern2span = [] # this container stores all the matches of each pattern.
        self.span_graph = nx.Graph() # defines network that
        self.span2span = nx.Graph()
        self.pattern2pattern = {}
        self.pattern2pattern_soft = {}
        self.pattern2n_match = {}
        self.pattern2chars_matched = {}
        self.pattern2idx = {}
        self.pattern_comparisons = set()
        self.similarity_matrix = []

    def get_spans(self,pattern):
        if not pattern in self.pattern2chars_matched:
            spans = list(enumerate([result.span() for result in re.finditer(pattern,self.string)]))
            print('------ Pattern: %s\t Matched %d patterns -----' %(pattern,len(spans)))
            self.pattern2span.append((pattern,spans))
            match_n = 0
            for num,span in spans:
                match_n+=span[1]-span[0]
            self.pattern2chars_matched[pattern] = match_n
            self.pattern2idx[pattern] = len(self.pattern2chars_matched) -1
            self.pattern2n_match[pattern] = len(spans)
    def has_overlap(span,span2):
        if span==span2:
            return True
        for val in span:
            if span2[0]<=val<=span2[1]:
                return True
        return False
    def make_overlap_network(self):
        patterns = self.pattern2span
        done = self.pattern_comparisons
        span_g = self.span2span
        pattern2pattern = self.pattern2pattern
        pattern2pattern_soft = self.pattern2pattern_soft
        for i in range(len(patterns)-1):
            pattern,spans = patterns[i]
            for j in range(i+1,len(patterns)):
                if (i,j) in done:
                    continue
                pattern2,spans2 = patterns[j]
                pattern_pair = (i,j)
                for num,span in spans:
                    size = span[1]-span[0]
                    for num2,span2 in spans2:
                        size2 = span2[1]-span2[0]
                        overlap = get_span_overlap(span,span2)
                        if overlap<=0:
                            continue

                        span_sum = size2+size - overlap
                        sim = overlap/span_sum
                        n,n2 = '%d_%d'%(i,num),'%d_%d'%(j,num2)
                        span_g.add_edge(n,n2)
                        span_g[n][n2]['similarity'] = sim
                        span_g.node[n]['pattern'] = i
                        span_g.node[n2]['pattern'] = j
                        if sim==1:
                            try:
                                pattern2pattern[pattern_pair].add(n)
                                pattern2pattern[pattern_pair].add(n2)
                            except:
                                pattern2pattern[pattern_pair] = set()
                                pattern2pattern[pattern_pair].add(n)
                                pattern2pattern[pattern_pair].add(n2)
                        try:
                            pattern2pattern_soft[pattern_pair].add(n)
                            pattern2pattern_soft[pattern_pair].add(n2)
                        except:
                            pattern2pattern_soft[pattern_pair] = set()
                            pattern2pattern_soft[pattern_pair].add(n)
                            pattern2pattern_soft[pattern_pair].add(n2)

                done.add((i,j))
    def explore_pattern(self,pattern,n_samples=10,context=10,shuffle=True):
        """prints examples of matches including context:
        """
        self.get_spans(pattern)
        idx = self.pattern2idx[pattern]
        spans = [i[1] for i in self.pattern2span[idx][1]]
        n_samples = min([n_samples,len(spans)])
        if shuffle:
            sample = random.sample(spans,n_samples)
        else:
            sample = spans[0:n_samples]
        for start,stop in sample:
            match = self.string[start:stop]
            start,stop = max([start-context,0]),min([stop+context,len(self.string)])
            context_string = self.string[start:stop]
            print('Match: %s\tContext:%s'%(match,context_string))

    def explore_difference(self,pattern,pattern2,context = 0):
        """returns all matches that are not matched by both patterns.
        and with overlap less than a specific threshold.
        Input:
            pattern: regular expression string
            pattern2: regular expression string
            context: defines how much context of the non matches you will see"""

        # check if patterns have been matched.
        self.get_spans(pattern)
        self.get_spans(pattern2)
        # add the spans to the overlap network.
        self.make_overlap_network()
        diff = []
        pat_idx,pat_idx2 = self.pattern2idx[pattern],self.pattern2idx[pattern2]
        pattern_pair = tuple(sorted([pat_idx,pat_idx2]))
        if pattern_pair in self.pattern2pattern:
            overlap = self.pattern2pattern[pattern_pair]
        else:
            overlap = set()
        for (num,span) in self.pattern2span[pat_idx][1]:
            n = '%d_%d'%(pat_idx,num)
            if not n in overlap:
                diff.append(self.string[span[0]:span[1]])
        for num,span in self.pattern2span[pat_idx2][1]:
            n = '%d_%d'%(pat_idx2,num)
            if not n in overlap:
                diff.append(self.string[max([span[0]-context,0]):min([span[1]+context,len(self.string)])])
        return diff
    def update_spans(self):
        self.pattern2span = []
        patterns = list(self.pattern2chars_matched)
        self.pattern2chars_matched = {}
        for pattern in self.patterns:
            self.get_spans(pattern)
    def define_string_sample(self,string):
        self.string = string
        self.update_spans()
    def create_similarity_matrix(self,method='hard'):
        pat2n = self.pattern2n_match
        patterns = [i[0] for i in self.pattern2span]
        #if len(self.similarity_matrix) == len(patterns): # check if it is already defined.
         #   return None
        if method =='soft':
            g = self.pattern2pattern_soft
        else:
            g = self.pattern2pattern
        mat = np.empty((len(patterns),len(patterns)))
        mat[:] = np.nan
        for i in range(len(patterns)-1):
            n = self.pattern2n_match[patterns[i]]

            for j in range(i+1,len(patterns)):
                n2 = self.pattern2n_match[patterns[j]]
                pattern_pair = (i,j)
                try:
                    overlap = len(g[pattern_pair])/2
                except:
                    overlap = 0
                #sum_ = n+n2 - overlap
                #try:
                #    sim = overlap/sum_
                #except:
                #    sim = np.nan
                if n>0:
                    sim = overlap/n
                else:
                    sim = np.nan
                mat[i][j] = sim
                if n2>0:
                    sim = overlap/n2
                else:
                    sim = np.nan
                mat[j][i] = sim
        if method=='soft':
            self.similarity_matrix_soft = mat
        if method=='hard':
            self.similarity_matrix = mat
    def plot_similarity(self,method='hard'):
        patterns = [i[0] for i in self.pattern2span]
        self.create_similarity_matrix(method)
        if method=='soft':

            mat = self.similarity_matrix_soft
        else:
            mat = self.similarity_matrix
        plt.figure(figsize=(12,8))
        sns.heatmap(mat,cmap='viridis')
        plt.xticks(np.arange(len(patterns))+.5,patterns,rotation=45)
        plt.yticks(np.arange(len(patterns))+.5,patterns,rotation=0)
        plt.title('Similarity Matrix')
    def report(self,method='hard'):
        for pattern,n in self.pattern2n_match.items():
            print('------ Pattern: %s\t Matched %d patterns -----' %(pattern,n))
        self.plot_similarity(method)
