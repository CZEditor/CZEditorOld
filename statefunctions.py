
class NormalKeyframe():
    name = "Error"
    def state(statetomodify,keyframe):
        if statetomodify:
            statetomodify[-1].imageparams.params.active = False
        keyframe.imageparams.params.active = True
        statetomodify.append(keyframe)
        return statetomodify
