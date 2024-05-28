"""
This class handles all image optimizations
@Contributors 
`Divine T Ngonera , Tanaka G Teta`

@Copyright `2024 Vendezon Technologies`
"""
import uuid
import os
import threading

from moviepy.editor import VideoFileClip


class VideoThread(threading.Thread):
    """
    video thread class for parallel threading
    """
    def __init__(self , video:object):
        super().__init__(daemon=True)
        self.video = video
        
    def run(self) :
       vid = self.video
       vid.generateThumbClip() # generate sub clip
       vid.generateMainClip() # generate main clip
       #remove the created temp file after processing completion
       os.remove(vid.videoFile)
        
class Video():
    """
    video class for video batch processing
    """
    def __init__(self , videoFile) -> None:
        
        details = videoFile.content_type
        details = details.split("/")
        self.extension = details[1]
        self.videoFile = self._createTempFile(videoFile.file)
        self._clip = VideoFileClip( self.videoFile , verbose= True)
        self.width , self.height = self._clip.size
        self.duration = int(self._clip.duration)
        self.name = str(uuid.uuid4()).replace("-","")
        self.key = self.__createFileName(f"{self.name}.{self.extension}" , self._clip.size)
        
        
    def generateThumbClip(self):
        """
        creates a video thumb for home feed
        """
        folder = "236x/"
        newWidth = 236
        newHeight = int(( 236 / self.width) * self.height )
        clip = self._clip 
        final = clip.resize(( newWidth , newHeight ))
        final.audio = None
        final = final.subclip(0,12) if clip.duration >= 12 else final
        final.write_videofile(f"{folder}{self.name}.mp4", fps=24)
        
        final.close()
        print(self.__createFileName(f"{self.name}.mp4", (self._clip.size)))
        
    def generateMainClip (self):
        """
        processes videos for main purposes
        """
        folder = "564x/"
        newWidth = 564
        newHeight = int(( 564 / self.width) * self.height )
        final =self._clip.resize(( newWidth , newHeight ))
        final.write_videofile(f"{folder}{self.name}.mp4", fps=24)
        
        final.close()
        print(self.__createFileName(f"{self.name}.mp4", (self._clip.size)))
        
    def __createFileName(self , name:str , size:tuple)->str:  
        """
        creates video access key
        """
        extensionNO = {"mp4":1,"webp":2 , "gif":3}
        n , e = name.split(".")
        nameStr = f"{n}{extensionNO[e]}{str(size[0]).zfill(4)}{str(size[1]).zfill(4)}"
        return nameStr
        
    def _createTempFile(self , file ):
        """
        creates video temporary file for processing
        """
        path = f"temp/{str(uuid.uuid4())}.{self.extension}"
        source = open (path , "wb")
        if source.write(file.read()):
            source.close()
            return path
        else:
            return False
    

    
    
        
        
        
        

        
        
        
