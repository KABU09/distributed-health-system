from pathlib import Path

def get_type_and_file(route:str):
    route = '/index.html' if route == '/' else route
    ext = route.split('.')[len(route.split('.')) - 1]
    ext = 'javascript' if ext == 'js' else ext
    ext = 'svg+xml' if ext == 'svg' else ext
    return {'file': route[1:], 'ext': ext}

def serve_file(conn, route:str):
    data = get_type_and_file(route)
    res = 'text' if data['ext'] != 'svg+xml' else 'image'
    file = Path('../WebClient/' + data['file'])
    if not file.is_file(): 
        print(f'error with file {data["file"]} in route {route}')
        handle_404(conn)
        return
    conn.send(b"HTTP/1.1 200 OK\n")
    conn.send(b"Content-Type: " + res.encode('utf-8') +b"/" + data['ext'].encode('utf-8') + b"\n\n")
    with open('../WebClient/' + data['file'], 'r') as f:
        l = f.read(1024)
        while l:
            conn.send(b"" + l.encode('utf-8') + b"")
            l = f.read(1024)

def handle_404(conn):
    conn.send(b"HTTP/1.1 404 Not Found\n")
    conn.send(b"Content-Type: text/html\n\n")
    with open('../WebClient/404.html', 'r') as f:
        l = f.read(1024)
        while l:
            conn.send(b"" + l.encode('utf-8') + b"")
            l = f.read(1024)

def handle_400(conn):
    conn.send(b"HTTP/1.1 400 Bad Request\n")
    conn.send(b"Content-Type: text/html\n\n")
    with open('../WebClient/400.html', 'r') as f:
        l = f.read(1024)
        while l:
            conn.send(b"" + l.encode('utf-8') + b"")
            l = f.read(1024)

def generate_search_result(name, cedula, info, title="Paciente"):
    response = f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Tinder Protocol</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous"><link rel="stylesheet" href="styles.css"><script src="https://code.jquery.com/jquery-3.6.0.min.js" deferintegrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script><script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script><link rel="shortcut icon" type="image/jpg" href="user.svg"/></head><body><br><h1 style="text-align: center;">{title}</h1><div class="card" style="max-width: 20rem; margin: 25px auto"><img src="user.svg" class="card-img-top" alt="patient-default-photo" height="140px"style="padding: 10px;">        <div class="card-body"><h4 class="card-title">{name}</h4><p>{cedula}<p><p class="card-text">{info}</p></div></div><a href="/" class="btn btn-primary"style="display: block; width: 200px; margin: 0 auto;">Volver a Inicio</a></body></html>'
    return response
