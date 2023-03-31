from http.server import BaseHTTPRequestHandler, HTTPServer
from DbHandler import test_connection
import urls, os

HOST_NAME = '127.0.0.1' 
PORT_NUMBER = 1234
DFA_PATH = ""

class RequestHandler(BaseHTTPRequestHandler):
	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()

	def do_GET(s):        
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()

		html = urls.route(s, HOST_NAME=HOST_NAME, PORT_NUMBER=PORT_NUMBER, DFA_PATH=DFA_PATH)
		s.wfile.write(bytes(html, "utf-8"))

	def do_POST(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()
		
		html = urls.route(s, DFA_PATH=DFA_PATH)
		s.wfile.write(bytes(html, "utf-8"))

if __name__ == '__main__':

	if not test_connection():
		print("ERROR: Could not connect to DB. Make sure it's running with correct arguments in DbHandler.py.")
		exit()

	while(True):
		path = str(input("Enter your DFA path: "))
		exits = os.path.exists(path)
		if exits:
			DFA_PATH = r'{}'.format(path)
			break

	print("Starting...")
	server_class = HTTPServer
	httpd = server_class((HOST_NAME, PORT_NUMBER), RequestHandler)
	
	try:
		print("Server running at: http://" + HOST_NAME + ':' + str(PORT_NUMBER))
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
