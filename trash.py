import requests
import json
import pandas as pd
import numpy as np
import json
from rdflib import Graph, URIRef, Literal
import spacy
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import itertools
import spotlight
import tagme
import inflect
import re
import sys
import requests
from nltk.stem.porter import *
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
import json
import networkx as nx
stemmer = PorterStemmer()
p = inflect.engine()
tagme.GCUBE_TOKEN = ""

def ttl_file_processing(filepath):
    graph = Graph()
    all_the_properties=[]
    properties={}

    with open(filepath, 'r') as file:
        turtle_entry = file.read()
# Parse the Turtle entry and add it to the graph

    graph.parse(data=turtle_entry, format='turtle')

    # Iterate over each triple in the graph and print the subject, predicate, and object
    for subject, predicate, obj in graph:
        properties["subject"] = subject
        properties["predicate"] = predicate
        #print(f"subject: {subject}")
        #print(f"Predicate: {predicate}")
        if isinstance(obj, URIRef):
            properties["object"] = obj.n3()
            #print(f"Object: {obj.n3()}")
        elif isinstance(obj, Literal):
            properties["object"] = obj.n3()
            #print(f'Object: "{obj.value}"')
        
        all_the_properties.append(properties)
        properties={}

    return all_the_properties


def spacy_parse(question,tokened_question, properties):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(question)
    entities = []
    relationships = []
    
    #print(properties)
    for token in doc:
        for key, values in properties.items():
            for value in values:
                #print(value)
                if value.lower() in token.text.lower():
                    entities.append((token.text, value, token.prob))
                    break
            if key.lower() in token.text.lower():
                for child in token.children:
                    for value in values:
                        if value != values[0]:
                            if value.lower() in child.text.lower():
                                relationships.append((values[0], value, child.prob))
                                break

    
    return entities,relationships
class PhraseMapping:
    def __init__(self):
        #the idea is to parse to get object, subject, predicate out of the ttl files

        self.dbpedia_c = ttl_file_processing('turtle/dbpedia_3Eng_class.ttl')
        self.dbpedia_p= ttl_file_processing('turtle/dbpedia_3Eng_property.ttl')
        self.knowledge_graph_p= ttl_file_processing('turtle/knowledge_graph.ttl')
        print(dbpedia_p)

        #TODO smash these into one thing, rn it is to big to work with. start small
        
    def phrasemap_question(self, question,tokened_question):
        print("fun")

