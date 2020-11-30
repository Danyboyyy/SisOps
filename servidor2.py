#!/usr/bin/env python
# -*- coding: utf-8 -*-

#modified for python 3.x may 2020
#modified 14 may to convert/deconvert str to bytes

#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import time
import queue
import threading
import datetime
from tabulate import tabulate #pip install tabulate

class Entrada:
	def __init__(self, id):
		self.mutex = threading.Semaphore(1)
		self.id = id

  def analiza:
    item = self.requestQueue.get()
		if item is None:
			break
    

	def oprimeBoton(timestamp): #Indica que hay un auto queriendo ocupar un lugar en el estacionamiento
		espacios.acquire()
		self.mutex.acquire()
		outTable.append([
			timestamp,
			"oprimeBoton" + self.id,
			"",
			"",
			""
		])
		outTable.append([
			timestamp,
			"",
			"Se comienza a imprimir tarjeta por E" + self.id,
			"",
			""
		])
		time.sleep(5)
		outTable.append([
			timestamp,
			"",
			"Se imprimió tarjeta. Hora" + datetime.datetime(2018, 6, 1).strftime("%X") + " E" + self.id,
			"",
			""
		])
		
	def recogeTarjeta(timestamp):
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
			timestamp,
			"",
			"Se levantó la barrera de E" + self.id,
			"",
			""
		])

	def laserOffE(timestamp): #El auto pasa por la entrada
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

	def laserOnE(timestamp): #El auto termina de pasar por la entrada y toma un lugar
		global libres
		global disponibles

		outTable.append([
			timestamp,
			"laserOnE " + self.id,
			"",
			"",
			""
		])
		
		libres -= 1
		disponibles += 1

		outTable.append([
			timestamp,
			"",
			"El auto termina de pasar por E" + self.id,
			libres,
			disponibles
		])
		
		self.mutex.release()
		ocupados.release()
		
		time.sleep(5)
		
		outTable.append([
			timestamp,
			"",
			"Se bajo la barrera E" + self.id,
			"",
			""
		])

class Salida:
	def __init__(self, id):
		self.mutex = threading.Semaphore(1)
		self.id = id

	def meteTarjeta(timestamp):
		# checar que haya pagado para hacer el acquire
		outTable.append([
			timestamp,
			"meteTarjeta " + self.id,
			"",
			"",
			""
		])
		ocupados.acquire()
		self.mutex.acquire()
		outTable.append([
			timestamp,
			"",
			"Se empieza a levantar la barrera de S" + self.id,
			"",
			""
		])
		time.sleep(5)
		outTable.append([
			timestamp,
			"",
			"Se levantó la barrera de S" + self.id,
			"",
			""
		])
		self.mutex.acquire()
		 
	def laserOffS(timestamp): #El auto comienza a pasar por la salida
		outTable.append([
			timestamp,
			"",
			"El auto comienza a salir por S" + self.id,
			"",
			""
		])

	def laserOnS(timestamp): #El auto libera un lugar y sale del estacionamiento
		global libres
		global disponibles

		libres += 1
		disponibles -= 1
		
		outTable.append([
			timestamp,
			"",
			"El auto termina de salir por S" + self.id,
			"",
			""
		])
		
		self.mutex.release()
		espacios.release()

class Estacionamiento:
	def __init__(self, timestamp, numEspacios, numEntradas, numSalidas):
		global libres
		global disponibles
		global espacios
		global ocupados

		outTable.append([
			timestamp,
			"apertura " + numEspacios + " " + numEntradas + " " + numSalidas,
			"Se abre un estacionamiento de " + numEspacios + "lugares, " + numEntradas + " puertas de entrada y " + numSalida + " de salida",
			libres,
			ocupados
		])
		self.crearEntradas(numEntradas)
		self.crearSalidas(numSalidas)
		
		libres = numEspacios
		disponibles = 0
		#Se crean los semaforos y se inicializan con los valores establecidos
		espacios = threading.Semaphore(numEspacios) # Inicializado en numEspacios lo cual es la cantidad dada en apertura, productor
		ocupados = threading.Semaphore(0) # Inicializado en 0, consumidor

	def serveRequests(self, msg):
		tokens = msg.split(' ')
		if (tokens[1] == 'apertura'):
			# validar tokens
			# Estacionamiento(tokens[2], tokens[3], tokens[4])
			### Intento de apertura en un estacionamiento ya existente ###
			print("")
		elif (tokens[1] == 'oprimeBoton'):
			#validar tokens
			threadEntradas[2].
			
			
			arregloEntradas[tokens[2]].oprimeBoton(tokens[3], tokens[4])

		elif (tokens[1] == 'recogeTarjeta'):
			# validar tokens
			recogeTarjeta(tokens[0], tokens[2])
		elif (tokens[1] == 'laserOnE'):
			# validar tokens
			laserOnE(tokens[0], tokens[2])
		elif (tokens[1] == 'laserOffE'):
			# validar tokens
			laserOffE(tokens[0], tokens[2])
		elif (tokens[1] == 'meteTarjeta'):
			# validar tokens
			if (len(tokens) == 5):
				meteTarjeta(tokens[0], tokens[2], tokens[3], tokens[4])
			else:
				meteTarjeta(tokens[0], tokens[2])
		elif (tokens[1] == 'laserOnS'):
			# validar tokens
			laserOnS(tokens[0], tokens[2])
		elif (tokens[1] == 'laserOffS'):
			# validar tokens
			laserOffS(tokens[0], tokens[2])
		elif (tokens[1] == 'cierre'):
			# validar tokens
			self.cierre(tokens[0])
		
	def cierre(self): #Se termina la ejecución
		print("")

	def crearEntradas(self, numEntradas):
		self.entradas = []
		for i in range(1, numEntradas + 1):
			self.entradas.append(Entrada(i))

	def crearSalidas(self, numSalidas):
		self.salidas = []
		for i in range(1, numSalidas + 1):
			self.salidas.append(Salida(i))

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000.

# Bind the socket to the port
server_address = ('localhost', 10000)
print ( 'starting up on %s port %s' % server_address)
sock.bind(server_address)

#Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.

# Listen for incoming connections
sock.listen(1)

# Wait for a connection
print ( 'waiting for a connection')
connection, client_address = sock.accept()

#accept() returns an open connection between the server and client, along with the address of the client. The connection is actually a different socket on another port (assigned by the kernel). Data is read from the connection with recv() and transmitted with sendall().

outTable = [['Timestamp', 'Comando', 'Mensaje del Servidor', 'Libres', 'Ocupados']]

try:
	print ( 'connection from', client_address)
	while (True):
    # Receive the data 
		data = connection.recv(256)
		msg = data.decode('utf-8')
		if (msg.split()[1] == 'apertura'):
      entradas = []
      numEntradas = msg.split()[3]
      for i in range numEntradas:
        entradas.append(Entrada(i))

      salidas = []
      numSalidas = msg.split()[4]
      for i in range numSalidas:
        salidas.append(numSalidas)

      threadsEntrada = []
      for i in range numEntradas:
        t = threading.Thread(target=entrada[i].analiza)
        t.start()
        threadsEntrada.append(t)

      threadsSalida =[]
      for i in range numSalidas:
        t = threading.Thread(target=salidas[i].analiza)
        t.start
        threadsSalida.append(t)
    elif msg.split()[1] == 'cierre':
      pass
    elif (msg.split()[1] == 'meteTarjeta' or msg.split()[1] == 'laserOnS' or msg.split()[1] == 'laserOffS'):
      salidas[msg.split()[2]].requestQueue.put(msg)
    else:
      entradas[msg.split()[2]].requestQueue.put(msg)

		print ( 'server received "%s"' % data.decode('utf-8')) # data bytes back to str
		if data:
			print ( 'sending answer back to the client')

			connection.sendall(b'va de regreso...' + data) # b converts str to bytes
		else:
			print ( 'no data from', client_address)
			connection.close()
			sys.exit()
			
finally:
  # Clean up the connection
	print ( 'se fue al finally')
	connection.close()

#When communication with a client is finished, the connection needs to be cleaned up using close(). This example uses a try:finally block to ensure that close() is always called, even in the event of an error.
