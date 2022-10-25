import nsfw_predict

# from urlparse import urlparse, parse_qs
from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image

import json

def checkImage(path, wfile):
    import os.path
    import tempfile
    if os.path.isfile(path):
        if path.endswith('.png'):
            # png files
            tmpFile = tempfile.NamedTemporaryFile(suffix='.jpg', delete = False)
            print('tmp file path: ' + tmpFile.name)
            img_png = Image.open(path)
            if img_png.mode in ("RGBA", "P"):
                img_png = img_png.convert("RGB")
            img_png.save(tmpFile, "JPEG")
            path = tmpFile.name
            print('converted jpg file path: ' + path)
        elif path.endswith('.gif'):
            data = {'msg': 'invalid file type(gif): ' + path}
            wfile.write(json.dumps(data).encode())
            return 
        
        data = nsfw_predict.predict(path)
        print(data)
        wfile.write(json.dumps(data).encode())
        if tmpFile is not None:
            # delete
            tmpFile.close()
            os.unlink(tmpFile.name)
            print('File deleted: ' + path)
    else:
        data = {'msg': 'invalid file path: ' + path}
        wfile.write(json.dumps(data).encode())
    
 
# data = {'result': 'this is a test'}
host = ('localhost', 8888)

class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        print( "path: " + str(self.path) )
        print( "headers: " + str(self.headers) )
        urlpath = parse.urlparse(self.path)
        query_components = parse.parse_qs(urlpath.query)
        print( "query_components: " + str(query_components) )
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        # self.wfile.write(json.dumps(data).encode())
        queryPath = urlpath.path
        if queryPath == '/quit':
            data = {'msg': 'bye bye'}
            self.wfile.write(json.dumps(data).encode())
            quit()
        elif queryPath == '/check':
            if "file" in query_components:
                print(query_components['file'][0])
                checkImage(query_components['file'][0], self.wfile)
            else:
                data = {'msg': 'need file paramter.'}
                self.wfile.write(json.dumps(data).encode())
        else:
            data = {'msg': 'invalid path: ' + queryPath}
            self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()

