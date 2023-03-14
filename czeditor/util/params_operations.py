from czeditor.util import Params
# from czeditor.keyframes import Keyframe
import czeditor.shared


def paramsAssociateKeyframe(params: Params, keyframe):
    from czeditor.properties import Property
    def iterateoverlist(l: list):
        for i in l:
            if isinstance(i, Property):
                i.associateKeyframe(keyframe)
            elif isinstance(i, Params):
                paramsAssociateKeyframe(i, keyframe)
            elif isinstance(i, list):
                iterateoverlist(i)
    for k, v in vars(params).items():
        if isinstance(v, Property):
            v.associateKeyframe(keyframe)
        elif isinstance(v, Params):
            paramsAssociateKeyframe(v, keyframe)
        elif isinstance(v, list):
            iterateoverlist(v)


def deserializeParams(data: dict, startparams:Params = Params({})):
    returndict = startparams.copy()
    for k, v in data.items():
        print(k,v)
        if v["type"] in czeditor.shared.deserializable:
            returndict[k] = czeditor.shared.deserializable[v["type"]
                                                           ].deserialize(v["params"])
    print("return",returndict)
    return returndict