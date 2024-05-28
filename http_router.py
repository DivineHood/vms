"""
vms http router 
*responsile for handling all http requests to the vms
@Authors
`Divine Ngonera`
`Tanaka Teta`
@copyright 2024 Vendezon Technologies
"""
import re


from fastapi import FastAPI , HTTPException, UploadFile, Form, Response, Request, templating
from fastapi.responses import FileResponse , PlainTextResponse , JSONResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from media_upload import Uploader
from media_index import MediaIndex
from fastapi.middleware.gzip import GZipMiddleware



#initialize the Vendezon Media Service (vms)
vms = FastAPI(version="1.00")
vms.add_middleware(GZipMiddleware, minimum_size=400)

def vms404(request: Request, exc: HTTPException):
    """
    Renders 404 error HTML Page
    """
    template = templating.Jinja2Templates(directory="./templates/")
    #format the datetime object to time string
    date =datetime.now().strftime("%m/%d/%Y, %H:%M")
    return template.TemplateResponse(status_code=404,request=request, name="404.html" ,context={"current_url":str(request.url), "current_timestamp": date})


def vms503(request: Request, exc: HTTPException):
    """
    Displays a server busy error as plain text
    
    """
    return PlainTextResponse(status_code=503,content="Unable to handle your request. Please try again")

#mount exceptions and static files directories
vms.add_exception_handler(404 , vms404)
vms.add_exception_handler(503,vms503)
vms.mount("/static", StaticFiles(directory="static"), name="static")



@vms.get("/" , include_in_schema=False)
async def root():
    """
    Default page
    """
    
    content = {
        "Product": "Vendezon Media Service",
        "Developer" : "Vendezon Technologies (Pvt) Ltd"
        
    }
    return JSONResponse(status_code=200 , content=content)




@vms.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """
    Display a favicon
    """
    
    
    return FileResponse('./static/favicon.ico')


@vms.post("/bucket/new" , name="Upload New Files")
async def upload_file(
    header_request: Request,
    files: list[UploadFile],
    attach_for:str = Form(...)

):
    
    """
    Handles all new media uploads
    @parameters
    `files`(List): The media files to be uploaded
    `attach_for` (str) : The media class
    
    @returns
    dict results or render an error
    
    
    """
    result = Uploader(files , attach_for).process()
    data = {
        "uploaded":"OK",
        "access_keys": result
    }
    return data

 
 
    
@vms.get("/w/{size}/{file_name}" , name="Access Files" , include_in_schema=False)
async def file(size:str, file_name:str ,request:Request):
    """
    Handles all media fetch requests
    @Access
    GET
    
    @parameters
    `size` (str) : the size class of the media being requested
    `file_name` (str) : The name of the media file being requested
    
    @returns
    the media file being requested
    
    """
    
    #allows only letters and numbers
    regex = r"^[a-zA-Z0-9]*$"
    
    #are the parameters safe ? Yes , go ahead and fetch the file
    if bool (re.match(regex , file_name)) and bool (re.match(regex , size)):
        #get indexed media file
        name = MediaIndex().getFile(file_name)
        path = Path(f"{size}x/"+ name )
        #does the file exist in the file system ? Yes , render the file
        if path.exists() :
            return FileResponse(path)
        #No , display an error
        else :
            raise HTTPException(status_code=404)
    #No , raise an error for defense    
    else:
        raise HTTPException(status_code=404)

 




