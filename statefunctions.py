from util import Params
class NormalKeyframe():
    name = "Media"
    params = Params({})
    def state(statetomodify,keyframe,stateparam):
        statetomodify.append(keyframe)
        return statetomodify
    def __str__(self):
        return self.name
class ErrorKeyframe():
    name = "Windows Error"
    params = Params({})
    def state(statetomodify,keyframe,stateparam):
        if statetomodify:
            statetomodify[-1].imageparams.params.active = False
        keyframe.imageparams.params.active = True
        #statetomodify.append(keyframe)
        return statetomodify
    def __str__(self):
        return self.name
class CascadeKeyframe():
    name = "Cascade"
    params = Params(
        {
            "x":16,
            "y":16
        })
    def state(statetomodify,keyframe,stateparam):
        for lastkeyframe in statetomodify[-1].compositingparams:
            if lastkeyframe.function().name == "Normal Media":
                for currentkeyframe in keyframe.compositingparams:
                    if currentkeyframe.function().name == "Normal Media":
                        currentkeyframe.params.x = lastkeyframe.params.x+stateparam.params.x
                        currentkeyframe.params.y = lastkeyframe.params.y+stateparam.params.y
                        break
                break
        #statetomodify.append(keyframe)
        return statetomodify
    def __str__(self):
        return self.name
statefunctionsdropdown = [["Media",NormalKeyframe],["Windows Error",ErrorKeyframe],["Cascade",CascadeKeyframe]]