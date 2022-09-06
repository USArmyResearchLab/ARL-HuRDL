import luci
import copy
import numpy
import scipy
import random

def normalize(scores):
    print(scores)
    tmp = 0.0
    retCopy = copy.deepcopy(scores)
    for s in scores:
        tmp += s
    for i in range(len(retCopy)):
        retCopy[i] = retCopy[i]/tmp
    return retCopy

def check_duplicates(objs,props):
    for i in range(len(objs)-1):
        for j in range(i+1,len(objs)):
            same = True
            o1 = objs[i]
            o2 = objs[j]
            for key in props:
               o1prop = o1.properties[key]
               o2prop = o2.properties[key]
               same = same and (o1prop==o2prop)
            if same:
                #print(o1, o2)
                return True
    return False


def generate_random_object_uniform(values,idstr):
    obj = luci.Object()
    props = {}
    for key in values.keys():
        props[key] = random.choice(values[key])
    props["EntityID"] = idstr
    props["EntityType"] = "Object"
    props["EntityName"] = None
    obj.setProperties(props)
    return obj

def generate_random_object_weighted(values,weights, idstr):
    obj = luci.Object()
    props = {}
    for key in values.keys():
        props[key] = random.choices(values[key],weights=weights[key])[0]
    props["EntityID"] = idstr
    props["EntityType"] = "Object"
    props["EntityName"] = None
    obj.setProperties(props)
    return obj


def generate_random_weights(values,num_variable_props):
    weights = {}
    variable_props = random.sample(values.keys(),num_variable_props)
    invariant_props = []

    for prop in values.keys():
        if prop not in variable_props:
            invariant_props.append(prop)

    ## handle variable props
    for key in variable_props:
        vec = []
        #print(key,values[key])
        Max = len(values[key])
        N = random.randint(3,Max)
        for i in range(Max):
            prob = 0.0
            if i < N:
                prob = 1.0/N
            vec.append(prob)
        weights[key] = vec

    ## handle invariant props 
    for key in invariant_props:
        vec = [1.0]
        Max = len(values[key])-1
        for i in range(Max):
            vec.append(0.0)
        random.shuffle(vec)
        weights[key] = vec

    #print(weights)
    return weights

def generate_random_objects(values, num_variable_props, num_objects):
    MAX_ATTEMPTS = 10000
    attempts = 0
    objs = []
    weights = generate_random_weights(values, num_variable_props)
    for i in range(num_objects):
        duplicates = True
        while duplicates:
            newobj = generate_random_object_weighted(values,weights,"obj" + str(i))
            duplicates = check_duplicates(objs,values.keys())
            if not duplicates:
                    objs.append(newobj)
            attempts += 1
            if(attempts > MAX_ATTEMPTS):
                return generate_random_objects(values, num_variable_props, num_objects)
        #print(i, objs)
    return objs

def generate_random_objects_high(values, num_objects):
    return generate_random_objects(values, 7, num_objects)

def generate_random_objects_low(values, num_objects):
    return generate_random_objects(values, 3, num_objects)

def main(world,complexity):
    props = ["Color","Size","Shape","Symbol","Pattern","Texture","ObjectType"]
    results = world.getValueMap(props)

    duplicates = True
    while duplicates: # loop until no duplicates
        if complexity == "low":
            objects = generate_random_objects_low(results, 20)
        else: # complexity == "high"
            objects = generate_random_objects_high(results, 20)

        duplicates = check_duplicates(objects,props)
    
    for obj in objects:
        obj.properties["Location"] = "-"
    
    return objects

if __name__ == "__main__":
    main()
