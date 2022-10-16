
def NormalKeyframe(statetomodify,keyframe):
    if statetomodify:
        statetomodify[-1].param.active = False
    keyframe.param.active = True
    statetomodify.append(keyframe)
    return statetomodify
