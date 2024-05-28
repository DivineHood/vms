"""
vms media index 
*responsile for indexing all media to the vms
@Authors
`Divine Ngonera`
`Tanaka Teta`
@copyright 2024 Vendezon Technologies
"""

import hashlib
import os

from pymongo import MongoClient
from fastapi import HTTPException

class MediaIndex:
    """
    Media Index Class which handles all media metadata indexing and retrievals
    """
    
    def __init__(self) -> None:
        #load the enviroment variables
        #try connecting to mongo
        try:
            mongoServer = MongoClient(os.getenv("MONGO_DB_HOST"), int(os.getenv("MONGO_DB_PORT")))
            #mongoServer = MongoClient("localhost" , 27017)
            
        #failed ? display a server busy error
        except:
            raise HTTPException(status_code=503 , detail="Server Busy. Please try again")
        
        #succeeded ? retrieve VMSIndices DB and respective collection
        else:
            db = mongoServer["vssIndices"]
            self.collection = db.get_collection("vssIndex")
        
    
    def createIndex(self , metadata:dict):
        """
        creates media index by creating mongo DB records
        @parameters
        `metadata` (dict) : information of the media file to be indexed
        """
        collection = self.collection
        
        try:
            #insert into Mongo DB
            return collection.insert_one(metadata)
        except :
            raise HTTPException(status_code=503 , detail="Server Busy. Please try again")
        else :
            return True
        
        
    
    def getIndex(self , fileHash:str , fileSize:int = None):
        
        """
        Get File metadata using the file hash value
        @Parameters
        `fileHash` (str) : Hashed value of the file
        `fileSize` (int) : file size
        
        @returns
        If found returns a dict of results else None
        """
        
        
        
        collection = self.collection
        try:
            #query for the results
            query = {"fileHash":fileHash , "fileSize":fileSize} if fileSize is not None else {"fileHash":fileHash}
            results = collection.find_one(query)
        except:
            raise HTTPException(status_code=503 , detail="Server Busy. Please try again")
        else:
            #return results when there is a match else return None
            if results is None:
                return False
            return results
    

    def getHash(self, file , attachFor:str):
        """Hashes the entire content of a media file with unbuffered reading."""
        file.seek(0)  # Reset file pointer to beginning
        hash = hashlib.sha256()
        txt = attachFor.encode('utf-8')
        while True:
            chunk = file.read()  # Adjust chunk size as needed
            if not chunk:
                break
            hash.update(chunk)
        hash.update(txt)
        return hash.hexdigest()
    
    def getFile(self , key:str):
        """
        Gets file from the index by fileID
        @parameters
        `fileID` (str) : unique id of the file
        
        @returns
        returns file name if there is a match else raise an error
        """
        try :
            key = key.lower()
            index = self.collection.find_one({"fileID":key})
        except :
            raise HTTPException(status_code=503 , detail="Server Busy. Please try again")
        else:
            if index is not None:
                return index["fileName"]
            else :
                raise HTTPException(status_code=404)

    
    


        
        