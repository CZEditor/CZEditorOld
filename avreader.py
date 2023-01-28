import av
import av.container
# PyAV video reader with intelligent seeking.
class PyAVSeekableVideoReader:

    def __init__(self,filename):
        self._filename = filename
        self._container:av.container.InputContainer = av.open(self._filename)
        self._stream = self._container.streams.video[0]
        self._currentFrame = 0
        self.frame_rate = float(self._stream.average_rate)
        self._cachedFrame = next(self._container.decode(self._stream)).to_ndarray(format="rgb24")
    def seek(self,frame:int) -> av.VideoFrame:
        if(self._currentFrame == frame):
            return self._cachedFrame
        self._currentFrame = frame
        self._container.seek(int(frame/self._stream.time_base/self.frame_rate),stream=self._stream)
        for decodedFrame in self._container.decode(self._stream):
            if(int(decodedFrame.pts*self._stream.time_base*self.frame_rate) < frame):
                continue
            
            return decodedFrame
        else:
            return decodedFrame

    def __getitem__(self,frame:int):
        if(frame != self._currentFrame):
            self._cachedFrame = self.seek(frame).to_ndarray(format="rgb24")
        
        return self._cachedFrame
    
    def __len__(self):
        return self._stream.frames
    
    def close(self):
        self._container.close()
