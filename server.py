from http.server import BaseHTTPRequestHandler, HTTPServer
import urls

HOST_NAME = '127.0.0.1' 
PORT_NUMBER = 1234
DFA_PATH = r"M:\DFAs\gen"

class RequestHandler(BaseHTTPRequestHandler):
	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()

	def do_GET(s):        
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()

		html = urls.route(s, HOST_NAME=HOST_NAME, PORT_NUMBER=PORT_NUMBER)
		print("get")
		s.wfile.write(bytes(html, "utf-8"))

	def do_POST(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()
		
		html = urls.route(s, HOST_NAME=HOST_NAME, PORT_NUMBER=PORT_NUMBER)
		print("post")
		s.wfile.write(bytes(html, "utf-8"))

if __name__ == '__main__':
	server_class = HTTPServer
	httpd = server_class((HOST_NAME, PORT_NUMBER), RequestHandler)
	
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
