import os
from pylab import *
import matplotlib.pyplot as plt
from IPython.core.display import display,HTML

import math

import pyAgrum as gum
import pyAgrum.lib.notebook as gnb

luci=gum.InfluenceDiagram()
ie = gum.ShaferShenoyLIMIDInference(luci) 

def initializeNetwork(filename):
    global luci, ie
    #luci=gum.loadID("network_corpus_eval.bifxml")
    luci=gum.loadID(filename)
    ie=gum.ShaferShenoyLIMIDInference(luci) 

# gets a dictionary of evidence to populate nodes, makes inference, and returns question with MEU
def bestQuestion(evs):
    global luci, ie
    ie.setEvidence(evs)
    ie.makeInference()
    q = ie.optimalDecision("AskQuestion")
    bestQIndex = q.argmax()[0].get("AskQuestion")
    bestQuestion = luci.variable(0).label(bestQIndex)
    return bestQuestion

def updateKnowledge(command,response):
    luci.cpt(response.getInput()["Property"])[{"Command": str(command.getInput())}] = [1, 0]
    print("Update knowledge: " + str(response.getInput()["Property"]))
    #luci.cpt('Location')[{'Command': '{Referent: Cryo calibrator, Type: Object}'}] = [1, 0]

# TODO: unused; set to name of network
def resetDecisionNet():
    global luci, ie
    luci=gum.loadID("decNet1.bifxml")
    ie=gum.ShaferShenoyLIMIDInference(luci) 
