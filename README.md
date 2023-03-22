# Sistema de Salud Distribuido

Este proyecto universitario es una implementación de un sistema de salud distribuido, con énfasis en los protocoles de comunicación, donde es posible leer y guardar datos de un paciente.

Se basa en protocolos como TCP, UDP y HTTP.

Consta de 3 partes:

- Cliente de Consola: donde se puede leer y guardar datos de un paciente desde una consola.
- Cliente Web: donde se puede leer y guardar datos de un paciente desde un navegador web.
- Servidor: donde se almacenan los datos de los pacientes. Este es compuesto por varios nodos, donde cada uno tiene la misma información, gracias a la replicación.
- Interfaz: es la capa de comunicación entre el cliente y el servidor. Es la encargada de enviar y recibir los datos de los pacientes. Esta capa es la que se comunica con los nodos del servidor. 

# Distributed Health System

This university project is a distributed health system implementation, with emphasis on communication protocols, where it is possible to read and save patient data.

It is based on protocols such as TCP, UDP and HTTP.

It consists of 3 parts:

- Console Client: where you can read and save patient data from a console.
- Web Client: where you can read and save patient data from a web browser.
- Server: where patient data is stored. This is composed of several nodes, where each one has the same information, thanks to replication.
- Interface: it is the communication layer between the client and the server. It is in charge of sending and receiving patient data. This layer communicates with the server nodes.
