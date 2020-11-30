#!/usr/bin/env python
# -*- coding: utf-8 -*-

#modified for python 3.x may 2020
#modified 14 may to convert/deconvert str to bytes

#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import time
import threading
import datetime
import queue
from tabulate import tabulate #pip install tabulate

global semEspacios
global countLibres
global countOcupados

semEspacios = threading.Semaphore(1)

class Entrada:
	def __init__(self, id):
		self.id = id
		self.requestQueue = queue.Queue(100)
		self.estado = "inicio"

	def serveRequests(self):
		while True:
			msg = self.requestQueue.get()
			if msg is None:
				break
			tokens = msg.split()
			timestamp = float(tokens[0])
			if tokens[1] == 'oprimeBoton':
				self.oprimeBoton(timestamp)
			elif tokens[1] == 'recogeTarjeta':
				self.recogeTarjeta(timestamp)
			elif tokens[1] == 'laserOnE':
				self.laserOnE(timestamp)
			elif tokens[1] == 'laserOffE':
				self.laserOffE(timestamp)
			self.requestQueue.task_done()

	def oprimeBoton(self, timestamp): #Indica que hay un auto queriendo ocupar un lugar en el estacionamiento
		if self.estado == "inicio":
			outTable.append([
				timestamp,
				"oprimeBoton " + self.id,
				"",
				"",
				""
			])

			semEspacios.acquire()

			if countLibres > 0:
				outTable.append([
					timestamp,
					"",
					"Se comienza a imprimir tarjeta por E" + self.id,
					"",
					""
				])

				semEspacios.release()

				time.sleep(5)
				outTable.append([
					timestamp + 5,
					"",
					"Se imprimió tarjeta. Hora " + datetime.datetime.now().strftime("%X") + " E" + self.id,
					"",
					""
				])
				self.estado = "oprimido"
			else:
				semEspacios.release()

				outTable.append([
					timestamp,
					"",
					"No hay cupo.",
					"",
					""
				])
				self.estado = "inicio"
		else:
			print("Llamada a oprimeBoton antes de inicializar Entrada", self.id)

	def recogeTarjeta(self, timestamp):
		if (self.estado == "oprimido"):
			outTable.append([
				timestamp,
				"recogeTarjeta " + self.id,
				"",
				"",
				""
			])
			outTable.append([
				timestamp,
				"",
				"Se empieza a levantar la barrera de E" + self.id,
				"",
				""
			])
			time.sleep(5)
			outTable.append([
				timestamp + 5,
				"",
				"Se levantó la barrera de E" + self.id,
				"",
				""
			])
			self.estado = "recogido"
		else:
			print("Llamada a recogeTarjeta antes de oprimir boton en Entrada", self.id)

	def laserOffE(self, timestamp): #El auto pasa por la entrada
		if self.estado == 'recogido':
			outTable.append([
				timestamp,
				"laserOffE " + self.id,
				"",
				"",
				""
			])
			outTable.append([
				timestamp,
				"",
				"El auto comienza a pasar por E" + self.id,
				"",
				""
			])
			self.estado = 'apagado'
		else:
			print("Llamada a laserOffE antes de recogeTarjeta en Entrada", self.id)

	def laserOnE(self, timestamp): #El auto termina de pasar por la entrada y toma un lugar
		if self.estado == 'apagado':
			outTable.append([
				timestamp,
				"laserOnE " + self.id,
				"",
				"",
				""
			])

			semEspacios.acquire()

			global countLibres
			global countOcupados
			
			countLibres -= 1
			countOcupados += 1

			outTable.append([
				timestamp,
				"",
				"El auto termina de pasar por E" + self.id,
				countLibres,
				countOcupados
			])

			semEspacios.release()
			
			time.sleep(5)
			
			outTable.append([
				timestamp + 5,
				"",
				"Se bajo la barrera E" + self.id,
				"",
				""
			])
			self.estado = 'inicio'
		else:
			print("Llamada a laserOnE antes de laserOffE en Entrada", self.id)

class Salida:
	def __init__(self, id):
		self.id = id
		self.estado = 'inicio'
		self.requestQueue = queue.Queue(100)

	def serveRequests(self):
		while True:
			msg = self.requestQueue.get()
			
			if msg is None:
				break

			tokens = msg.split()
			timestamp = float(tokens[0])
			
			if tokens[1] == 'meteTarjeta':
				if tokens[3] == '1':
					self.meteTarjeta(timestamp, int(tokens[3]), float(tokens[4]))
				else:
					self.meteTarjeta(timestamp)
			elif tokens[1] == 'laserOnS':
				self.laserOnS(timestamp)
			elif tokens[1] == 'laserOffS':
				self.laserOffS(timestamp)
			
			self.requestQueue.task_done()

	def meteTarjeta(self, timestamp, pago = None, timestampPago = None):
		# checar que haya pagado para hacer el acquire
		if self.estado == 'inicio':
			semEspacios.acquire()

			if countOcupados > 0:
				if pago == 1:
					outTable.append([
						timestamp,
						"meteTarjeta " + self.id + " " + str(pago) + " " + str(timestampPago),
						"",
						"",
						""
					])
					if (timestamp - timestampPago < 15):
						outTable.append([
							timestamp,
							"",
							"Se empieza a levantar la barrera de S" + self.id,
							"",
							""
						])

						time.sleep(5)

						outTable.append([
							timestamp + 5,
							"",
							"Se levantó la barrera de S" + self.id,
							"",
							""
						])
						self.estado = "metido"
					else:
						outTable.append([
							timestamp,
							"",
							"Pago realizado hace 15 segundos o mas. Vuelva a intentar",
							"",
							""
						])
						self.estado = 'inicio'
				else:
					outTable.append([
						timestamp,
						"meteTarjeta " + self.id,
						"",
						"",
						""
					])
					outTable.append([
						timestamp,
						"",
						"No se ha realizado el pago.",
						"",
						""
					])
					self.estado = 'inicio'
			else:
				print("No pueden salir autos sin que haya espacios ocupados.")
			semEspacios.release()
		else:
			print("Llamada a meteTarjeta antes de Inicio en Salida", self.id)

	def laserOffS(self, timestamp): #El auto comienza a pasar por la salida
		if self.estado == 'metido':
			outTable.append([
				timestamp,
				"laserOffS " + self.id,
				"",
				"",
				""
			])
			outTable.append([
				timestamp,
				"",
				"El auto comienza a salir por S" + self.id,
				"",
				""
			])
			self.estado = "apagado"
		else:
			print("Llamada a laserOffS antes de meteTarjera en Salida", self.id)

	def laserOnS(self, timestamp): #El auto libera un lugar y sale del estacionamiento
		if self.estado == "apagado":
			outTable.append([
				timestamp,
				"laserOnS " + self.id,
				"",
				"",
				""
			])

			semEspacios.acquire()

			global countLibres
			global countOcupados

			countLibres += 1
			countOcupados -= 1

			outTable.append([
				timestamp,
				"",
				"El auto termina de pasar por S" + self.id,
				countLibres,
				countOcupados
			])

			semEspacios.release()

			time.sleep(5)
			
			outTable.append([
				timestamp + 5,
				"",
				"Se bajo la barrera S" + self.id,
				"",
				""
			])
			self.estado = "inicio"
		else:
			print("Llamada a laserOnS antes de laserOffS en Salida", self.id)

class Estacionamiento:
	def __init__(self, timestamp, numEspacios, numEntradas, numSalidas):

		semEspacios.acquire()

		global countLibres
		global countOcupados

		countLibres = int(numEspacios)
		countOcupados = 0

		outTable.append([
			timestamp,
			"apertura " + numEspacios + " " + numEntradas + " " + numSalidas,
			"Se abre un estacionamiento de " + numEspacios + " lugares, " + numEntradas + " puertas de entrada y " + numSalidas + " de salida",
			countLibres,
			countOcupados
		])

		semEspacios.release()

		self.crearEntradas(int(numEntradas))
		self.crearSalidas(int(numSalidas))

	def serveRequests(self, msg):
		tokens = msg.split()
		if (tokens[1] == 'oprimeBoton' or tokens[1] == 'recogeTarjeta' or tokens[1] == 'laserOnE' or tokens[1] == 'laserOffE'):
			#validar tokens
			self.entradas[int(tokens[2]) - 1].requestQueue.put(msg)
		elif (tokens[1] == 'meteTarjeta' or tokens[1] == 'laserOnS' or tokens[1] == 'laserOffS'):
			# validar tokens
				self.salidas[int(tokens[2]) - 1].requestQueue.put(msg)
		elif (tokens[1] == 'cierre'):
			# validar tokens
			self.cierre(tokens[0])

	def cierre(self, timestamp): #Se cierra el estacionamiento y ya nadie puede entrar o salir
		outTable.append([
			timestamp,
			"cierre",
			"Se cierra el estacionamiento",
			"",
			""
		])

		print ( tabulate(outTable) )

		numEntradas = len(self.entradas)
		numSalidas = len(self.salidas)
		for e in self.entradas:
			e.requestQueue.join()
			e.requestQueue.put(None)
		for s in self.salidas:
			s.requestQueue.join()
			s.requestQueue.put(None)
		
		numThreadsEntrada = len(self.threadsEntrada)
		numThreadsSalida = len(self.threadsSalida)
		for i in range(numThreadsEntrada):
			self.threadsEntrada[i].join()
		for i in range(numThreadsSalida):
			self.threadsSalida[i].join()
		
		global connection
		global sys
		
		connection.close()
		sys.exit()
		

	def crearEntradas(self, numEntradas):
		self.entradas = []
		self.threadsEntrada = []
		for i in range(1, numEntradas + 1):
			self.entradas.append(Entrada(str(i)))
			t = threading.Thread(target=self.entradas[i - 1].serveRequests)
			t.start()
			self.threadsEntrada.append(t)
		

	def crearSalidas(self, numSalidas):
		self.salidas = []
		self.threadsSalida = []
		for i in range(1, numSalidas + 1):
			self.salidas.append(Salida(str(i)))
			t = threading.Thread(target=self.salidas[i - 1].serveRequests, )
			t.start()
			self.threadsSalida.append(t)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000.

# Bind the socket to the port
server_address = ('localhost', 10000)
print ( 'Starting up on %s port %s' % server_address)
sock.bind(server_address)

#Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.

# Listen for incoming connections
sock.listen(1)

# Wait for a connection
print ( 'Waiting for a connection...')
connection, client_address = sock.accept()

#accept() returns an open connection between the server and client, along with the address of the client. The connection is actually a different socket on another port (assigned by the kernel). Data is read from the connection with recv() and transmitted with sendall().

global outTable
outTable = [['Timestamp', 'Comando', 'Mensaje del Servidor', 'Libres', 'Ocupados']]

try:
	print ( 'Connection from', client_address)
	while (True):
    # Receive the data 
		data = connection.recv(256)
		msg = data.decode('utf-8')
		print ( '[ Cliente ]: "%s"' % data.decode('utf-8'))
		if (msg.split()[1] == 'apertura'):
			global estacionamiento
			estacionamiento = Estacionamiento(msg.split()[0], msg.split()[2], msg.split()[3], msg.split()[4])
		else:
			estacionamiento.serveRequests(msg)
		 # data bytes back to str
		
		if data:
			connection.sendall(b'va de regreso...' + data) # b converts str to bytes
			pass
		else:
			print ( 'no data from', client_address)
			connection.close()
			sys.exit()

			
finally:
  # Clean up the connection
	print ( 'se fue al finally')
	connection.close()
	sys.exit()

#When communication with a client is finished, the connection needs to be cleaned up using close(). This example uses a try:finally block to ensure that close() is always called, even in the event of an error.
