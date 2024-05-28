import uvicorn
from dotenv import load_dotenv
if __name__ == '__main__':
    load_dotenv()
    uvicorn.run("http_router:vms",
                host="localhost",
                port=8432,
                reload=True,
                ssl_keyfile="./certificates/key.pem", 
                ssl_certfile="./certificates/cert.pem",
                workers=4 ,
                server_header= False ,
                )
