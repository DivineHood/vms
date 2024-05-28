"""
vms media upload
*responsile for handling uploading to the vms
@Authors
`Divine Ngonera`
`Tanaka Teta`
@copyright 2024 Vendezon Technologies
"""



from exc import FileNotSupportedError , FileTooLargeError
from fastapi import HTTPException
from media_index  import MediaIndex
from datetime import datetime

class Uploader:
    """
    media uploader class
    """
    MAX_VID_SIZE = 70 # MB
    MAX_PHOTO_SIZE = 5 #MB
    MAX_PHOTO_COUNT = 8
    MAX_VID_COUNT = 1
    ALLOWED_VID_FORMATS = ["mp4" , "mkv" , "avi"]
    ALLOWED_PHOTO_FORMATS = ["png","jpeg","jpg" ,"gif"]
    MIN_RESOLUTION = 700 #px
    
    def __init__(self ,files:list , attachFor:str) -> None:
        """
        constructor
        @parameters
        `files`(list) : list of the files to be uploaded
        `attachFor` (str) : media class of the file to be uploaded
        """
        
        #store the params in the class instance
        self.videos = []
        self.images = []
        self.numImages = 0
        self.numVideos = 0
        self.attachFor = attachFor
        self.keys = dict()
        
        for file in files:
            #get fine details from the file mime type
            details = file.content_type
            details = details.split("/")
            
            match details[0]:
                #file is image ? check photo count , photo size and photo extension
                case "image":
                    #image format valid ?
                    if details[1] in self.ALLOWED_PHOTO_FORMATS:
                        self.numImages +=1
                        #is photo count and photo size within range
                        if self.numImages <=  self.MAX_PHOTO_COUNT and file.size//1000000 <= self.MAX_PHOTO_SIZE:
                            self.images.append(file)
                        #not in range , display an error
                        else:
                            raise FileTooLargeError("Cannot handle your upload size")
                        
                    #extension invalid , display an error
                    else:
                        raise FileNotSupportedError(f"Uploaded Image with extension .{details[1]} is not allowed")
                #file is video ? check video size , video format and video count
                case "video":
                    #format is valid?
                    if details[1] in self.ALLOWED_VID_FORMATS:
                        self.numVideos +=1
                        #video count and video size is within range ?
                        if self.numVideos <=  self.MAX_VID_COUNT and file.size//1000000 <= self.MAX_VID_SIZE:
                            self.videos.append(file)
                            self.extension = details[1]
                        #not in range , display an error
                        else:
                            raise FileTooLargeError(f"Cannot handle your upload size {self.numVideos} {file.size//1000000}")
                    #format invalid , display an error
                    else:
                        raise FileNotSupportedError(f"video is not allowed")
                #file is neither a video or image , then VMS fails to recognize it and display an error
                case _:
                    raise FileNotSupportedError ()
    def process (self):
        """
        handles the upload process
        """
        
        #process videos
        if self.videos != []:
            #and file should only be for product
            if self.attachFor == "product":
                #import video processing packages
                from optimize.video import VideoThread , Video
                
                
                video = Video(self.videos[0]) #initialize video processor
                
                if video.width < self.MIN_RESOLUTION:
                    raise FileNotSupportedError(detail=f"Video should have width not less than {self.MIN_RESOLUTION}px")
                else:
                    #is video duration 1 mim or less ?
                    if video.duration <= 60 and video.duration >=12:
                        
                        #initialize vms media index
                        index = MediaIndex()
                        #get hash value for the video file
                        hashValue = index.getHash(self.videos[0].file , self.attachFor)
                        
                        returnedBucket = index.getIndex(hashValue)
                        
                        #does the file exist in the index ? If no , index and upload it
                        if returnedBucket is False:
                            index.createIndex(
                                {
                                "fileID" : video.key ,
                                "fileHash" : hashValue ,
                                "fileName" : f"{video.name}.{video.extension}",
                                "originalWidth" : video.width,
                                "originalHeight" : video.height, 
                                "originalSize" : self.videos[0].size ,
                                "uploadedAt" : str(datetime.now())
                                
                                }
                            )
                            
                            self.keys.update({self.videos[0].filename:video.key})
                            #processing and uploading the video
                            VideoThread(video).start()
                        else :
                            self.keys.update({self.videos[0].filename:returnedBucket["fileID"]})
                        #return video access keys/ fileID
                    
                    #video duration out of range , raise an error
                    else :
                        raise FileTooLargeError("Video should be not less than 12 seconds and more than a minute")
                    
                #not for product ? display an error
            else:
                    raise HTTPException(status_code=406) 
        #process image
        if self.images != []:
            #initialize image processor
            from optimize.image import Img , ImgThread
            match self.attachFor:
                
                #is it for profile ?
                case "profile":
                    #then the imagage should be the only one
                    if len(self.images) == 1:
                        
                        image = Img(self.images[0] , {196})
                        
                        #initialize vms media index
                        index = MediaIndex()
                        hashValue = index.getHash(self.images[0].file , self.attachFor)
                        
                        returnedBucket = index.getIndex(hashValue)
                        #does the file exist in vms index ? No process and upload it
                        if returnedBucket is False:
                            index.createIndex(
                                {
                                "fileID" : image.key ,
                                "fileHash" : hashValue ,
                                "fileName" : f"{image.name}.{image.extension}",
                                "originalWidth" : image.width,
                                "originalHeight" : image.height, 
                                "originalSize" : self.images[0].size ,
                                "uploadedAt" : str(datetime.now())
                                
                                }
                            )
                            
                            self.keys.update({self.images[0].filename:image.key})
                            #process and upload the image using parallel threading
                            ImgThread({image}).start()
                            
                        #yes ? just return its fileID or access key . This reduces duplication of the same file
                        else :
                            self.keys.update({self.images[0].filename:returnedBucket["fileID"]})
                        
                    
                    #not only one , display an error
                    else:
                        raise HTTPException(status_code=406)
                
                #is the image for a product ?
                case "product":
                    imgs = []
                    keys = []
                    for file in self.images:
                        
                        image = Img(file , {236 , 564})
                        
                        if image.width < self.MIN_RESOLUTION:
                            raise FileNotSupportedError(detail=f"Images should have width not less than {self.MIN_RESOLUTION}px")
                        else:
                            #initialize vms media index
                            index = MediaIndex()
                            #get file hash
                            hashValue = index.getHash(file.file , self.attachFor)
                            
                            returnedBucket = index.getIndex(hashValue)
                            
                            #is the file found in vms media index ? No process and upload it
                            if returnedBucket is False:
                                index.createIndex(
                                    {
                                    "fileID" : image.key ,
                                    "fileHash" : hashValue ,
                                    "fileName" : f"{image.name}.{image.extension}",
                                    "originalWidth" : image.width,
                                    "originalHeight" : image.height, 
                                    "originalSize" : file.size ,
                                    "uploadedAt" : str(datetime.now())
                                    
                                    }
                                )
                                imgs.append(image)
                                self.keys.update({file.filename:image.key})
                            #yes ? just return its fileID or access key . This reduces duplication of the same file    
                            else :
                                self.keys.update({file.filename:returnedBucket["fileID"]})
                    
                    if len(imgs) != 0:
                        ImgThread(imgs).start()
                        
                
                #not for profile , not for product ? display an error
                case _:
                    raise HTTPException(status_code=406)
        return self.keys