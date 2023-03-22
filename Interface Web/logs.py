import logging

class log:
    def __init__(self):
        logging.basicConfig(filename='logs.log', level=logging.DEBUG, format="%(asctime)s %(lineno)d %(levelname)s: %(message)s")

    def log_solicitud_lectura(self, data, ip_nodo):
        logging.info(f'Solicitud de lectura: {data} hacia nodo con ip {ip_nodo}')

    def log_solicitud_escritura(self, data, ip_nodo):
        logging.info(f'Solicitud de escritura: {data} hacia nodo con ip {ip_nodo}')

    def log_respuesta_lectura(self, data, ip_nodo, estado):
        logging.info(f'Respuesta de lectura: EXITO sobre solicitud {data} desde el nodo con ip {ip_nodo}') if estado == '0' else logging.error(f'Respuesta de lectura: ERROR sobre solicitud {data} desde el nodo con ip {ip_nodo}')
        
    def log_respuesta_escritura(self, data, ip_nodo, estado):
        logging.info(f'Respuesta de escritura: EXITO sobre solicitud {data} desde el nodo con ip {ip_nodo}') if estado == '0' else logging.error(f'Respuesta de escritura: ERROR sobre solicitud {data} desde el nodo con ip {ip_nodo}')
    
    def log_solicitud(self, op, route, content = None, length =  None):
        logging.info(f'Solicitud con operacion {op} hacia ruta {route}, con Content-Type: {content} y Content-Length: {length}')
