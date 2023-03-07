from czeditor.util import Params
from czeditor.properties import Property
from czeditor.keyframes import Keyframe


def paramsAssociateKeyframe(params: Params, keyframe: Keyframe):
    def iterateoverlist(self, l: list):
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
