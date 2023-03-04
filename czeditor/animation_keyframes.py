from typing import overload, List


class AnimationKeyframe():
    def __init__(self, frame, tracks, params):
        self.params = params
        self.frame = frame
        self.tracks = tracks

    def getValue(self, trackValues, frame):
        return self.params.provider.function().getValue(self.params.provider.params, trackValues, self, frame)

    def output(self, trackValues, frame, nextKeyframes):
        return self.params.outputter.function().getValue(self.params.outputter.params, trackValues, self, frame, nextKeyframes)


class AnimationKeyframeList():
    def __init__(self, tracks: dict, windowClass):
        self.windowClass = windowClass
        self.keyframes: List[AnimationKeyframe] = []
        self.needssorting = False
        self.tracks = tracks
        self.originaltracks = tracks

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

    @overload
    def moveToTrack(self, keyframe: AnimationKeyframe, track: int, index: int):
        ...

    @overload
    def moveToTrack(self, i: int, track: int, index: int):
        ...

    def moveToTrack(self, o, track: int, index: int):
        if isinstance(o, AnimationKeyframe):
            i = self.keyframes.index(o)
        else:
            i = o
        self.keyframes[i].tracks[index] = track

    def getsafe(self, i):
        if len(self.keyframes) > i and i > 0:
            return self.keyframes[i]
        else:
            return None

    def isin(self, keyframe: AnimationKeyframe) -> bool:
        return keyframe in self.keyframes

    def getKeyframeTracks(self, keyframe: AnimationKeyframe):
        # Puts all the tracks of the keyframe in a list in order
        # They dont have their original indexes because they are not needed.
        # if the timeline tracks are {0:track0, 1:track1, ...} and the keyframe tracks are [0,2],
        # then the result of this function will be [track0,track2],[0,2]
        tracks = [self.tracks[i] for i in keyframe.tracks]
        return tracks, keyframe.tracks

    def getNextKeyframes(self, trackIds, keyframe: AnimationKeyframe):
        startIndex = self.keyframes.index(keyframe)
        if startIndex+1 >= len(self.keyframes):
            return []
        nextKeyframes = []
        for trackId in trackIds:
            # We can start from the keyframe in question.
            for index in range(startIndex+1, len(self.keyframes)):
                # Is the keyframe in the current wanted track?
                if trackId in self.keyframes[index].tracks:
                    nextKeyframes.append(self.keyframes[index])
                    break
        return nextKeyframes

    def getValueAt(self, frame: int):

        if len(self.keyframes) == 0:
            return None

        if self.needssorting:
            self.keyframes = sorted(self.keyframes, key=lambda k: k.frame)

        self.tracks = {k: v.copy() for k, v in self.originaltracks.items()}

        for keyframe in self.keyframes:
            if keyframe.frame > frame:
                return self.tracks  # Stop when reached the last keyframe before the cursor
            # tracks is a list of tracks which have their corresponding index in trackIds
            tracks, trackIds = self.getKeyframeTracks(keyframe)
            tracks = keyframe.output(
                tracks, frame-keyframe.frame, self.getNextKeyframes(trackIds, keyframe))  # Get the new tracks
            i = 0
            for track in trackIds:
                # Set corresponding tracks to the new tracks
                self.tracks[track] = tracks[i]
                i += 1
        return self.tracks
