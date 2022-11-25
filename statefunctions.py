from util import Params
class NormalKeyframe():
    name = "Media"
    params = Params({})
    def state(statetomodify,keyframe):
        statetomodify.append(keyframe)
        return statetomodify
    def __str__(self):
        return self.name
class ErrorKeyframe():
    name = "Windows Error"
    params = Params({})
    def state(statetomodify,keyframe):
        if statetomodify:
            statetomodify[-1].imageparams.params.active = False
        keyframe.imageparams.params.active = True
        statetomodify.append(keyframe)
        return statetomodify
    def __str__(self):
        return self.name
statefunctionsdropdown = [["Media",NormalKeyframe],["Windows Error",ErrorKeyframe]]