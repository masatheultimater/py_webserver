import socket

class TCPClient:
  """
  TCP通信クライアントのクラス
  """
  def request(self):
    
    print("=== start client ===")

    try:
      # create client socket
      client_socket = socket.socket()
      client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      print("=== connecting to server")
      client_socket.connect(("127.0.0.1", 80))
      print("=== connect to server has completed")

      # read client_send.txt & send it to the server
      with open ("client_send.txt", "rb") as f:
        request = f.read()
      
      client_socket.send(request)

      # receive the response
      response = client_socket.recv(4096)

      # read the response & write it down to client_recv.txt
      with open ("client_recv.txt", "wb") as f:
        f.write(response)

      # close the connect
      client_socket.close()

    finally:
      print("=== stop client ===")

if __name__ == '__main__':
  client = TCPClient()
  client.request()
