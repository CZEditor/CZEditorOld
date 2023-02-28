from typing import overload


class AnimationKeyframe():
    def __init__(self, frame, params):
        self.params = params
        self.frame = frame

    def getValue(self, frame):
        return self.params.provider.function().getValue(self.params.provider.params, frame)

    def mix(self, frame, length, a, b):
        return self.params.mixer.function().getValue(self.params.mixer.params, frame, length, a, b)


class AnimationKeyframeList():
    def __init__(self, windowClass):
        self.windowClass = windowClass
        self.keyframes = []
        self.needssorting = False

    def add(self, keyframe: AnimationKeyframe) -> None:
        self.keyframes.append(keyframe)
        self.needssorting = True

    def append(self, keyframe: AnimationKeyframe) -> None:
        self.keyframes.append(keyframe)
        self.needssorting = True

    @overload
    def change(self, keyframe: AnimationKeyframe, change: AnimationKeyframe) -> None:
        ...

    @overload
    def change(self, i: int, change: AnimationKeyframe) -> None:
        ...

    def change(self, o, change: AnimationKeyframe) -> None:
        if isinstance(o, AnimationKeyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        prevframe = self.keyframes[i].frame
        self.keyframes[i] = change
        self.needssorting = True

    @overload
    def remove(self, keyframe: AnimationKeyframe) -> None:
        ...

    @overload
    def remove(self, i: int) -> None:
        ...

    def remove(self, o) -> None:
        if isinstance(o, AnimationKeyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        self.keyframes.pop(i)

    def pop(self, i: int) -> None:
        self.keyframes.pop(i)

    def len(self) -> int:
        return len(self.keyframes)

    def get(self, i) -> AnimationKeyframe:
        if self.needssorting:
            self.keyframes = sorted(self.keyframes, key=lambda k: k.frame)
            self.needssorting = False
        return self.keyframes[i]

    def __str__(self) -> str:
        if self.needssorting:
            self.keyframes = sorted(self.keyframes, key=lambda k: k.frame)
            self.needssorting = False
        return str(self.keyframes)

    def __getitem__(self, i: int) -> AnimationKeyframe:
        if self.needssorting:
            self.keyframes = sorted(self.keyframes, key=lambda k: k.frame)
            self.needssorting = False
        return self.keyframes[i]

    def __setitem__(self, i: int, change: AnimationKeyframe) -> None:
        prevframe = self.keyframes[i].frame
        self.keyframes[i] = change
        self.needssorting = True

    @overload
    def setframe(self, keyframe: AnimationKeyframe, frame: int):
        ...

    @overload
    def setframe(self, i: int, frame: int):
        ...

    def setframe(self, o, frame: int):
        if isinstance(o, AnimationKeyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        self.keyframes[i].frame = frame
        self.needssorting = True

    def getsafe(self, i):
        if len(self.keyframes) > i and i > 0:
            return self.keyframes[i]
        else:
            return None

    def isin(self, keyframe: AnimationKeyframe) -> bool:
        return keyframe in self.keyframes

    def getValueAt(self, frame: int):
        if len(self.keyframes) == 0:
            return None
        for keyframe in range(len(self.keyframes)-1):
            if self.keyframes[keyframe].frame < frame:
                return self.keyframes[keyframe].mix(
                    frame-self.keyframes[keyframe].frame,
                    self.keyframes[keyframe+1].frame -
                    self.keyframes[keyframe].frame,
                    self.keyframes[keyframe].getValue(
                        frame-self.keyframes[keyframe].frame),
                    self.keyframes[keyframe+1].getValue(frame-self.keyframes[keyframe+1].frame))
        return self.keyframes[keyframe].getValue(frame-self.keyframes[keyframe].frame)
