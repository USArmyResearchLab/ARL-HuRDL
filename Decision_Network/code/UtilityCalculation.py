import luci
import copy
from scipy.stats import entropy

def normalize(scores):
    tmp = 0.0
    retCopy = copy.deepcopy(scores)
    for s in scores:
        tmp += scores[s]
    for k in retCopy.keys():
        retCopy[k] = retCopy[k]/tmp*100.0
    return retCopy


def normalize_multivec(vec1, vec2):
    tmp = sum(vec1.values()) + sum(vec2.values()) 
    nvec1 = copy.deepcopy(vec1)
    nvec2 = copy.deepcopy(vec2)

    for k in nvec1.keys():
        nvec1[k] = nvec1[k]/tmp*100.0
    for k in nvec2.keys():
        nvec2[k] = nvec2[k]/tmp*100.0

    return nvec1, nvec2

def main(world):
    results = world.deriveFeatureEntropy(["Color","Size","Shape","Symbol","Pattern","Texture","ObjectType"])
    results2 = world.deriveFeatureYNEntropy(["Color","Size","Shape","Symbol","Pattern","Texture","ObjectType"])

    norm_whq, norm_ynq = normalize_multivec(results,results2)
    print("Normalized WHQ " + str(norm_whq))
    print("Normalized YNQ " + str(norm_ynq))
    
    return norm_whq, norm_ynq

if __name__ == "__main__":
    main()
