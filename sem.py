#!/usr/bin/python

# by renateitor 
#SEM (Security Enhanced Messaging) is a collaborative PoC for implementing Cover Channels over ICMP protocol
#
# Dependencias: tcpdump, python-scapy
#

# importamos librerias
import os
import subprocess
import time
import sys
import getopt
import logging

# definimos que solamente se debe alertar ante un error
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

# Levanto los parametros necesarios para la comunicacion
name = raw_input('Name [test]: ')
target = raw_input('Target device [192.168.1.71]: ')
passwd = raw_input('Key for the communication [20121357]: ')
interface = raw_input('Interface for the communication (listening) [eth0]: ')

if name == '':
	name = 'test'
if target == '':
	target = '192.168.1.71'
if passwd == '':
	passwd = '20121357'
if interface == '':
	interface = 'eth0'
	
# Dejo monitoreando en background para la recepcion de mensajes
rec_p = subprocess.Popen(['python', 'recive.py','--name='+name,'--interface='+interface,'--password='+passwd,'&'])
rec_pid = rec_p.pid

# Loop para chatear
print 'To exit write: \':q!\''
txt=raw_input('>> ')
while txt.strip()!=':q!':
	txt=txt+'\n'
	# a partir de aca empieza el armado del paquete y el envio

	# construimos la capa 3 del paquete (IP)
	l3 = IP()
	l3.dst = target

	# construimos la capa 4 del paquete (ICMP)
	l4 = ICMP()

	# definimos el resto de las variables
	msgsize = 12 # como vamos a dividir el mensaje en partes, aca definimos el tamano de cada parte
	# las variables (first) (last) (count) las utilizamos para el proceso de corte y envio del paquete
	first = 0
	last = (msgsize)
	count = (len(txt)/msgsize)+1
	# entramos en un bucle en el cual vamos a enviar un paquete para cada parte de los datos
	print "							[ %s : " %(count),
	for a in range(0, count):
		print "%s " %(a + 1),
		if a == 0: #es la primer parte
			payload = passwd + name +'0'+ txt[first:last]
		else:
			payload = passwd + name +'1'+ txt[first:last]
		# ensamblamos el paquete
		# las capas que no definimos son definidas automaticamente por scapy
		pkt = l3/l4/payload
		# enviamos el paquete
		a = sr(pkt, verbose = 0, retry = 0, timeout = 1)
		first += msgsize
		last += msgsize
	print ']'
	
	
	txt=raw_input('>> ')

# Mato el proceso que escucha
os.system('kill -9 '+str(rec_pid))
print '\n\nGood Bye!\n\n'

