#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PROYECTO FINAL SISTEMAS OPERATIVOS
# 
# Equipo No. 3
# Daniel Alejandro David Sánchez A00824566
# Diego Alejandro del Valle Pimentel A01747310
# Juan Pablo Díaz López A00825316
# Santiago Díaz Guevara A01252554
#
# Fecha: 30 de noviembre de 2020

import socket
import sys
import time
import threading
import datetime
import queue
from tabulate import tabulate

global semEspacios
global countLibres
global countOcupados

class Entrada:	#Clase definida para manejar las entradas del estacionamiento
	def __init__(self, id):
		self.id = id
		self.requestQueue = queue.Queue(100)
		self.estado = "inicio"	#Variable que asegura que no se lleven a cabo instrucciones en la entrada fuera de orden

	def serveRequests(self):	#Manejo de inputs del cliente
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
			else:
				pint("Comando '" + tokens[1] + "' en Entrada " + self.id + " no es valido")
			self.requestQueue.task_done()

	def oprimeBoton(self, timestamp): #Indica que hay un auto queriendo ocupar un lugar en el estacionamiento
		if self.estado == "inicio":
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"oprimeBoton " + self.id,
				"",
				"",
				""
			])

			semEspacios.acquire()

			if countLibres > 0:
				outTable.append([	# Se ingresan los datos a la tabla de Output
					timestamp,
					"",
					"Se comienza a imprimir tarjeta por E" + self.id,
					"",
					""
				])

				semEspacios.release()

				time.sleep(5)	# Se simulan 5 segundos de espera en tiempo real
				outTable.append([	# Se ingresan los datos a la tabla de Output
					timestamp + 5,
					"",
					"Se imprimió tarjeta. Hora " + datetime.datetime.now().strftime("%X") + " E" + self.id,
					"",
					""
				])
				self.estado = "oprimido"
			else:
				semEspacios.release()

				outTable.append([	# Se ingresan los datos a la tabla de Output
					timestamp,
					"",
					"No hay cupo.",
					"",
					""
				])
				self.estado = "inicio"
			
		else:
			print("Llamada a oprimeBoton antes de inicializar Entrada " + self.id)
			

	def recogeTarjeta(self, timestamp):	#Indica que el auto recogió su correspondiente tarjeta
		if (self.estado == "oprimido"):
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"recogeTarjeta " + self.id,
				"",
				"",
				""
			])
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"",
				"Se empieza a levantar la barrera de E" + self.id,
				"",
				""
			])
			time.sleep(5)	# Se simulan 5 segundos de espera en tiempo real
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp + 5,
				"",
				"Se levantó la barrera de E" + self.id,
				"",
				""
			])
			self.estado = "recogido"
		else:
			print("Llamada a recogeTarjeta antes de oprimir boton en Entrada " + self.id)

	def laserOffE(self, timestamp): #El auto pasa por la entrada
		if self.estado == 'recogido':
			outTable.append([ # Se ingresan los datos a la tabla de Output
				timestamp,
				"laserOffE " + self.id,
				"",
				"",
				""
			])
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"",
				"El auto comienza a pasar por E" + self.id,
				"",
				""
			])
			self.estado = 'apagado'
		else:
			print("Llamada a laserOffE antes de recogeTarjeta en Entrada " + self.id)

	def laserOnE(self, timestamp): #El auto termina de pasar por la entrada y toma un lugar
		if self.estado == 'apagado':
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"laserOnE " + self.id,
				"",
				"",
				""
			])

			semEspacios.acquire()	#Se hace una operación de wait en el semaforo semEspacios para entrar a la Sección Crítica

			global countLibres
			global countOcupados
			
			countLibres -= 1	# Variable compartida entre varios procesos
			countOcupados += 1	# Variable compartida entre varios procesos

			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"",
				"El auto termina de pasar por E" + self.id,
				countLibres,
				countOcupados
			])

			semEspacios.release() #Se hace una operación de signal en el semaforo semEspacios para salir de la Sección Crítica
			
			time.sleep(5)	# Se simulan 5 segundos de espera en tiempo real
			
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp + 5,
				"",
				"Se bajo la barrera E" + self.id,
				"",
				""
			])
			self.estado = 'inicio'
		else:
			print("Llamada a laserOnE antes de laserOffE en Entrada " + self.id)

class Salida:  # Clase definida para manejar las salidas del estacionamiento
	def __init__(self, id):
		self.id = id
		self.estado = 'inicio' #Variable que asegura que no se ejecuten instrucciones de salida fuera de orden
		self.requestQueue = queue.Queue(100)

	def serveRequests(self): #Manejo de inputs del cliente, los cuales fueron ingresados a un Queue
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
			else:
				print("Comando '" + tokens[1] + "' en Salida " + self.id + " no es valido")
			
			self.requestQueue.task_done()

	def meteTarjeta(self, timestamp, pago = None, timestampPago = None):
		# checar que haya pagado para hacer el acquire
		if self.estado == 'inicio':
			semEspacios.acquire() #Se hace una operación de wait en el semaforo semEspacios para entrar a la Sección Crítica
			
			if countOcupados > 0:	#Se verifica que si existan carros dentro del estacionamiento
				if pago == 1:
					outTable.append([	# Se ingresan los datos a la tabla de Output
						timestamp,
						"meteTarjeta " + self.id + " " + str(pago) + " " + str(timestampPago),
						"",
						"",
						""
					])
					if (timestamp - timestampPago < 15):
						outTable.append([	# Se ingresan los datos a la tabla de Output
							timestamp,
							"",
							"Se empieza a levantar la barrera de S" + self.id,
							"",
							""
						])

						time.sleep(5)	# Se simulan 5 segundos de espera en tiempo real

						outTable.append([	# Se ingresan los datos a la tabla de Output
							timestamp + 5,
							"",
							"Se levantó la barrera de S" + self.id,
							"",
							""
						])
						self.estado = "metido"
					else:
						outTable.append([	# Se ingresan los datos a la tabla de Output
							timestamp,
							"",
							"Pago realizado hace 15 segundos o mas. Vuelva a intentar",
							"",
							""
						])
						self.estado = 'inicio'
				else:
					outTable.append([	# Se ingresan los datos a la tabla de Output
						timestamp,
						"meteTarjeta " + self.id,
						"",
						"",
						""
					])
					outTable.append([	# Se ingresan los datos a la tabla de Output
						timestamp,
						"",
						"No se ha realizado el pago.",
						"",
						""
					])
					self.estado = 'inicio'
			else:
				print("No pueden salir autos sin que haya espacios ocupados.") # Se levanta una excepción para controlar que no salga un carro cuando no hay ningun carro dentro
			semEspacios.release()	#Se hace una operación de signal en el semaforo semEspacios para salir de la Sección Crítica
		else:
			print("Llamada a meteTarjeta antes de Inicio en Salida " + self.id)

	def laserOffS(self, timestamp): #El auto comienza a pasar por la salida
		if self.estado == 'metido':
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"laserOffS " + self.id,
				"",
				"",
				""
			])
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"",
				"El auto comienza a salir por S" + self.id,
				"",
				""
			])
			self.estado = "apagado"
		else:
			print("Llamada a laserOffS antes de meteTarjera en Salida " + self.id)

	def laserOnS(self, timestamp): #El auto libera un lugar y sale del estacionamiento
		if self.estado == "apagado":
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"laserOnS " + self.id,
				"",
				"",
				""
			])

			semEspacios.acquire()	#Se hace una operación de wait en el semaforo semEspacios para entrar a la Sección Crítica

			global countLibres
			global countOcupados

			countLibres += 1	# Variable compartida entre varios procesos
			countOcupados -= 1	# Variable compartida entre varios procesos

			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp,
				"",
				"El auto termina de pasar por S" + self.id,
				countLibres,
				countOcupados
			])

			semEspacios.release()	#Se hace una operación de signal en el semaforo semEspacios para salir de la Sección Crítica

			time.sleep(5)	# Se simulan 5 segundos de espera en tiempo real
			
			outTable.append([	# Se ingresan los datos a la tabla de Output
				timestamp + 5,
				"",
				"Se bajo la barrera S" + self.id,
				"",
				""
			])
			self.estado = "inicio"
		else:
			print("Llamada a laserOnS antes de laserOffS en Salida " + self.id)

class Estacionamiento: #Clase definida para manejar los lugares del estacionamiento
	def __init__(self, timestamp, numEspacios, numEntradas, numSalidas):	#Se inicializan los atributos del estacionamiento
		self.numEntradas = numEntradas
		self.numSalidas = numSalidas

		global semEspacios
		semEspacios = threading.Semaphore(1) #Creación e inicialización de semaforo semEspacios

		semEspacios.acquire()	#Se hace una operación de wait en el semaforo semEspacios para entrar a la Sección Crítica
		
		global countLibres	#Contador de los espacios libres del estacionamiento 
		global countOcupados #Contador de los espacios ocupados en el estacionamiento

		countLibres = numEspacios	
		countOcupados = 0

		outTable.append([ #Se ingresan los datos iniciales del estacionamiento a la tabla de Output
			str(timestamp),
			"apertura " + str(numEspacios) + " " + str(numEntradas) + " " + str(numSalidas),
			"Se abre un estacionamiento de " + str(numEspacios) + " lugares, " + str(numEntradas) + " puertas de entrada y " + str(numSalidas) + " de salida",
			str(countLibres),
			str(countOcupados)
		])

		semEspacios.release()	#Se hace una operación de signal en el semaforo semEspacios para salir de la Sección Crítica
		
		self.crearEntradas(numEntradas)
		self.crearSalidas(numSalidas)
		
	def serveRequests(self, msg):
		tokens = msg.split()
		if (tokens[1] == 'oprimeBoton' or tokens[1] == 'recogeTarjeta' or tokens[1] == 'laserOnE' or tokens[1] == 'laserOffE'):
			if 1 <= int(tokens[2]) and int(tokens[2]) <= self.numEntradas:  #Verifica si el numero de la entrada no sobrepasa los limites permitidos
				self.entradas[int(tokens[2]) - 1].requestQueue.put(msg)
			else:
				print("Numero (" + tokens[2] + ") de entrada fuera del rango valido.")
		elif (tokens[1] == 'meteTarjeta' or tokens[1] == 'laserOnS' or tokens[1] == 'laserOffS'):
			if int(tokens[2]) > 0 and int(tokens[2]) <= self.numSalidas:	#Verifica si el numero de la salida no sobrepasa los limites permitidos
				self.salidas[int(tokens[2]) - 1].requestQueue.put(msg)
			else:
				print("Numero (" + tokens[2] + ") de salida fuera del rango valido.")
		elif (tokens[1] == 'cierre'):
			self.cierre(tokens[0])
		else:
			print("Comando '" + tokens[1] + "' no valido.")

	def cierre(self, timestamp): #Se cierra el estacionamiento, ya nadie puede entrar o salir
		outTable.append([ #Se introducen los datos y mensajes a la tabla de Output
			timestamp,
			"cierre",
			"Se cierra el estacionamiento",
			"",
			""
		])

		print ( tabulate(outTable) )
		
		for e in self.entradas:
			e.requestQueue.join()
			e.requestQueue.put(None)
		for s in self.salidas:
			s.requestQueue.join()
			s.requestQueue.put(None)
		
		numThreadsEntrada = len(self.threadsEntrada)
		numThreadsSalida = len(self.threadsSalida)
		for i in range(numThreadsEntrada):
			self.threadsEntrada[i].join() #Se unen los threads de entrada para cerrar ejecución
		for i in range(numThreadsSalida):
			self.threadsSalida[i].join() #Se unen los threads de salida para cerrar ejecución
		
		global connection
		global sys
		
		connection.close()
		sys.exit()
		

	def crearEntradas(self, numEntradas):	# Función para comenzar a crear los Threads de las llamadas a una entrada
		self.entradas = []
		self.threadsEntrada = []
		for i in range(1, numEntradas + 1):
			self.entradas.append(Entrada(str(i)))
			t = threading.Thread(target=self.entradas[i - 1].serveRequests)	#Creación de Thread
			t.start()	#inicialización de Thread
			self.threadsEntrada.append(t)	#inicialización de Thread
		

	def crearSalidas(self, numSalidas):	# Función para comenzar a crear los Threads de las llamadas a una salida
		self.salidas = []
		self.threadsSalida = []
		for i in range(1, numSalidas + 1):
			self.salidas.append(Salida(str(i)))
			t = threading.Thread(target=self.salidas[i - 1].serveRequests, )	#Creación de Thread
			t.start()
			self.threadsSalida.append(t)	#inicialización de Thread

# Se crea un Socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


#Luego, bind() es usado para asociar el socket con la dirección del servidor. En este caso, la dirección es localhost, refiriendose al servidor actual, y el número de puerto es 10000
# Enlaza el socket con el puerto
server_address = ('localhost', 10000)
print ( 'Starting up on %s port %s' % server_address)
sock.bind(server_address)

#Llamar listen() pone al socket en modo servidor, y accept() espera por una conexión entrante.

# Escucha conexiónes entrantes
sock.listen(1)

# Espera una conexión
print ( 'Waiting for a connection...')
connection, client_address = sock.accept()


#accept() devuelve una conexión abierta entre cliente y servidor, de la mano de la dirección del cliente. La conexión en realidad es un socket diferente en otro puerto (asignado por el kernel). 
#Los datos son leidos desde la conexión con la función recv() y transmitidos con la función sendall() 
global outTable
outTable = [['Timestamp', 'Comando', 'Mensaje del Servidor', 'Libres', 'Ocupados']]

try:
	print ( 'Connection from', client_address)
	while (True):
	# Recibe los datos
		data = connection.recv(256)
		msg = data.decode('utf-8')
		print ( '[ Cliente ]: "%s"' % data.decode('utf-8'))
		if (msg.split()[1] == 'apertura'):
			global estacionamiento
			estacionamiento = Estacionamiento(float(msg.split()[0]), int(msg.split()[2]), int(msg.split()[3]), int(msg.split()[4]))
		else:
			estacionamiento.serveRequests(msg)
		# bytes de entrada de vuelta a str
		if data:
			connection.sendall(b'va de regreso...' + data) # b convierte str a bytes
			pass
		else:
			print ( 'no data from', client_address)
			connection.close()
			sys.exit()
			
finally:
  # Limpia la conexión
	print ( 'Fin de la conexion')
	connection.close()
	sys.exit()

#Cuando la comunicación con el cliente se ha acabado, la conexión necesita ser limpiada con la función close(). 
#Este código utiliza un bloque try:finally para asegurar que close() siempre sea ejecutado, aún en el caso de que se de un error