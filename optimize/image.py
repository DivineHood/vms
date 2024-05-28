"""
This class handles all image optimizations
@Contributors 
`Divine T Ngonera , Tanaka G Teta`

@Copyright `2024 Vendezon Technologies`

"""
import uuid

from PIL import Image
from exc import FileNotSupportedError
from threading import Thread

class ImgThread(Thread):
    """
    Image thread class for parallel image processing
    """
    def __init__(self , images:list):
        super().__init__(daemon=True)
        self.images =images
        
    def run(self) :
        """
        starts image thread
        """
        for img in self.images:
            img.resize()

class Img:
    """
    Image processor class
    """
    def __init__(self , file:dict = None, sizes:list = None, remBg = False)->None:
        #put the files and resize formats in the class instance
        self.file = file
        self.forms = sizes
        
        #load the image into memory with PIL
        with Image.open(file.file) as img:
            img.load()
            extension = self.__checkFileFormat(file.filename) 
            self.extension = "gif" if extension == "gif" else "webp"
            self.img = img
            self.width , self.height = img.size
            #create file name
            self.name = str(uuid.uuid4()).replace("-","")
            #create fileID/ access key
            self.key = self.__createFileName(f"{self.name}.{self.extension}" , img.size)
        
    
    def resize(self):
        #treating each file accordingly
        results:set = set()
            
        for size in self.forms:
            result = self.__convert(self.file ,size , self.name)
        results.add(result)
        return results
            
    def __convert(self , file:dict , size:int , universalName:str) -> bool:
        """
        Handles all image conversion and optimization processes
        @access : private
        @parameters
        `file` (dict) : file metadata
        `size` (int) : file size specification
        `universalName` (str): file name
        """
        img = self.img
        img.load() #load image into memory
        width , height = img.size
        newWidth = size #default width for all small images
        newHeight = int( ( newWidth / width ) * height)
        newSize  = ( newWidth , newHeight )
        
        output = img.resize(
        newSize
        )
        try:
            extension = self.__checkFileFormat(file.filename)
            name = universalName +".webp"
            folder = f"{size}x/"
            match extension.lower():
                case "jpeg":
                    output.save(folder + name , "webp" , quality = 70)
                case "jpg":
                    output.save(folder + name , "webp" , quality = 70)
                case "png":
                    output.save(folder + name , "webp" , lossless=True)
                case "gif":
                    imageColor = ""
                    name = universalName +".gif"
                    output.save( folder + name, "gif" ,dpi=(72,72))
                    
        except FileNotSupportedError as exc:
            raise exc
        except Exception as exc:
            raise exc
        else:
            return self.__createFileName(name , img.size )
           
    
    def __createFileName(self , name:str , size:tuple)->str:  
        """
        creates file access key / fileID
        @access : private
        @parameters 
        `name` (str) : name of the file
        `size` (str) : file resolution
        @returns
        access key
        """
        extensionNO = {"mp4":1,"webp":2 , "gif":3}
        n , e = name.split(".")
        nameStr = f"{n}{extensionNO[e]}{str(size[0]).zfill(4)}{str(size[1]).zfill(4)}"
        return nameStr
        
            
    def __checkFileFormat(self , filename:str) -> str:
        """
        This method checks if the file has the correct accepted format
        @Parameters:
        `filename`(str) = the name of the uploaded file
        @Return :
        `fileFormat` (str) or return an error
        """
        acceptedFormats = {"jpeg" , "jpg" , "png" , "tiff" , "gif"}
        #get file extension from filename
        format = filename.split(".")[-1]
        if format in acceptedFormats:
            #file has the correct extension return True
            return format
        
        else:
            #The file is not accepted
            raise FileNotSupportedError()
    
            
        
            
        
         