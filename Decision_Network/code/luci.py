import csv
import copy
import numpy
import scipy
from scipy.stats import entropy
from collections import Counter

# these are used in setProperties and in randomly choosing values for YNQs (only color and location)
objectProperties = {"EntityType":[], "Name":[],
"Color":["Yellow", "Green", "Blue", "Red", "Purple", "White", "Grey", "Black", "Brown"],
"Size":[],"Shape":[],"Symbol":[],"Pattern":[],"Texture":[],
"ContainedIn":[],
"Location":["Left", "Right", "Middle", "Top", "Bottom", "Top-left", "Top-right", "Bottom-left", "Bottom-right"],
"ObjectType":[], "Shape":[], "Size":[], "Texture":[]}

# list of dicts of commands (populated by parseCSV)
input_list = []

class Entity(object):
    def __init__(self):
        self.entityname = None
        self.id = None

    def setProperties(self, props):
        if "EntityID" in props:
            self.id = props["EntityID"]
        if "EntityType" in props:
            self.entityname = props["EntityType"]
        
    def getID(self):
        return self.id


class Object(Entity):
    def __init__(self):
        super(Object,self).__init__()
        self.properties = {}

    def setProperties(self, props):
        super(Object,self).setProperties(props)

        for key in props.keys():
            if key in objectProperties:
                self.properties[key] = props[key]
                
    def getProperties(self):
        return self.properties
    
    def __str__(self):
        retStr = str(self.id) + " with properties: " + str(self.properties)
        return retStr

    
class Container(Object):
    def __init__(self,props):
        super(Container,self).__init__()
        super(Container,self).setProperties(props)
        self.containedObjects = []

    def addObject(self, obj):
        self.containedObjects.append(obj)

    def removeObject(self, obj):
        self.containedObjects.remove(obj)

    def isInside(self, obj):
        return obj in self.containedObjects  

    def __str__(self):
        retStr = str(self.id) + " with contents: [" 
        for i in range(len(self.containedObjects)):
            obj = self.containedObjects[i]
            retStr += str(obj.id)
            if i < len(self.containedObjects)-1:
                retStr += ", "
        retStr += "]\n" + str(self.id) + " with properties: " + str(self.properties) + "\n"
        return retStr

class Agent:
    def __init__(self):
        self.beliefstate = None
        self.location = None
        self.inventory = []
    
    def getBeliefState(self):
        return self.beliefstate

    def setBeliefState(self, beliefstate):
        self.beliefstate = beliefstate

    def moveTo(self,newLoc):
        self.location = newLoc

    def pickupObject(self, obj):
        self.inventory = [obj]
    
    def putdownObject(self):
        if len(self.inventory==0):
            return None
        else:
            obj = self.inventory[0]
            self.inventory = []
            return obj

    def debugPrint(self):
        print ("Agent Location: " + str(self.location))
        print ("Agent Inventory: " + str(self.inventory))
        print ("Agent Belief State: \n\t" + str(self.beliefstate))

class Utterance(object):
    pass


# {[Referent: Temporal emitter][Type: Object]}
class Command(Utterance):
    def __init__(self, utt):
        self.input = utt
        #self.action = utt["Action"]
        self.referent = utt["Referent"]
        self.type = utt["Type"]

    def getInput(self):
        return self.input
        
    def getReferent(self):
        return self.referent
    
    def getType(self):
        return self.type
    
    def debugPrint(self):
        print ("Input command: " + str(self.input))
        print ("Command referent: " + self.referent)
        print ("Referent type: " + self.type)
    
    def __str__(self):
        retStr = str(self.input)
        return retStr
        
# {"QuestionType": "WHQ-Description", "Referent": "Temporal emitter", "Property": "ObjectType"}
class QnA(Utterance):
    def __init__(self, utt):
        self.input = utt
        self.questionType = utt["QuestionType"]
        self.referent = utt["Referent"]
        self.property = utt["Property"]

    def getInput(self):
        return self.input

    def getQuestionType(self):
        return self.questionType

    def getReferent(self):
        return self.referent
    
    def getProperty(self):
        return self.property
    
    def debugPrint(self):
        print ("Input: " + str(self.input))
        print ("Question Type: " + self.questionType)
        print ("Referent: " + self.referent)
        print ("Property: " + self.property)

# {"QuestionType": "WHQ-Description", "Referent": "Temporal emitter", "Property": "ObjectType"}
class WHQ(QnA):
    def __init__(self,input):
        super().__init__(input)

# {"QuestionType": "YNQ-Color", "Referent": "Temporal emitter", "Property": "Color", "Value": "Red"}
class YNQ(QnA):
    def __init__(self,input):
        super().__init__(input)
        self.value = input["Value"]

# {"QuestionType": "WHQ-Description", "Referent": "Temporal emitter", "Property": "ObjectType", "Value": "Emitter"}
class WHQresponse(QnA):
    def __init__(self,input):
        super().__init__(input)
        self.value = input["Value"]

# {"QuestionType": "YNQ-Description", "Referent": "Temporal emitter", "Property": "ObjectType", "Value": "Emitter", "Response": "Yes"}
class YNQresponse(QnA):
    def __init__(self,input):
        super().__init__(input)
        self.value = input["Value"]
        self.response = input["Response"]

class ScenarioWorld:

    def __init__(self):
        self.entities = []
        self.agent = None

    def addRandomEntity(self, obj):
        etype = obj.properties["EntityType"]
        if(etype == "Object"):
            newObj = Object()
            newObj.id = obj.id
            newObj.setProperties(obj.properties)
            self.entities.append(newObj)
        if(etype == "Container"):
            newCont = Container(obj.properties)
            self.entities.append(newCont)

    def addEntity(self, props):
        etype = props["EntityType"]
        if(etype == "Object"):
            newObj = Object()
            newObj.setProperties(props)
            self.entities.append(newObj)
        if(etype == "Container"):
            newCont = Container(props)
            self.entities.append(newCont)
        
    def getEntityByType(self, etype):
        return filter(lambda x: x.entityname == etype, self.entities)

    def getEntityByID(self, eid):
        for e in self.entities:
            if e.id == eid:
                return e
        return None 
    
    def getEntityByName(self, ename):
        for e in self.entities:
            if e.properties["Name"] == ename:
                return e
        return None 

    def getValuesByFeature(self, feature):
        retList = []
        print("getValuesByFeature", feature)
        for e in self.entities:
            if feature in e.properties.keys():
                retList.append(e.properties[feature])
        print(retList)
        return retList

    def initAgent(self):
        agent = Agent()
        self.agent = agent

    def parseFromCSV(self, csvfilename):
        with open(csvfilename) as csvfile: # open(csvfilename,"r", encoding='utf-8-sig')
            reader = csv.DictReader(csvfile)
            for row in reader:
                #print row
                self.addEntity(row)
                self.initAgent()

            objs = self.getEntityByType("Object")

            for e in self.entities:
                input_list.append({"Referent": e.properties["Name"], "Type": e.properties["EntityType"]})

    def deriveBeliefState(self, unknownprops):
        beliefstate = copy.deepcopy(self)
        for ent in beliefstate.entities:
            # clear container contents
            if ent.entityname == "Container": 
                if not len(ent.containedObjects) == 0:
                    ent.containedObjects.pop()
            # clear object properties
            for unkprop in unknownprops:
                ent.properties[unkprop] = "-"    
        return beliefstate

    def deriveFeatureEntropy(self, askable_props):
        results = {}
        for prop in askable_props:
            tmpList = self.getValuesByFeature(prop)
            counts = Counter(tmpList)
            probs = []
            for feature in counts.keys():
                probs.append(counts[feature]/float(len(tmpList)))
            ent = entropy(probs)
            results[prop] = ent

        return results

    def deriveFeatureYNEntropy(self, askable_props):
        results = {}
        for prop in askable_props:
            tmpList = self.getValuesByFeature(prop)
            counts = Counter(tmpList)
            ents = []
            numObjs = len(tmpList)
            for feature in counts.keys():
                p = counts[feature]/float(numObjs)
                probs = [p, 1.0-p]
                print(prop, feature, p)
                ents.append(entropy(probs)*p)
            results[prop + "YN"] = numpy.sum(ents)
        return results 

    def getValueMap(self, askable_props):
        results = {}
        for prop in askable_props:
            tmpList = self.getValuesByFeature(prop)
            results[prop] = list(set(tmpList))
        return results

    def debugPrint(self):
        
        print ("############# CONTAINERS & CONTENTS ##################")
        for x in self.getEntityByType("Container"):
            print (x)
        print ("######################################################\n")
        print ("############# OBJECT DESCRIPTIONS ####################")
        for x in self.getEntityByType("Object"):
            print (x)
        print ("######################################################\n")
        print ("############# AGENT DESCRIPTION ######################")
        if self.agent != None:
            self.agent.debugPrint()
        else:
            print ("!! No Agent Initialized !!")
        print ("######################################################\n")
