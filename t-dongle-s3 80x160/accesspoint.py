import machine
import network
import ujson
import utime
import usocket as socket
# SPI DRIVERS ------------------------------------------------------------------
import cfg_tft
import st7735 as driver
# CUSTOM MODULES ---------------------------------------------------------------
import settings
import config
# FONTS ------------------------------------------------------------------------
import vga1_8x8 as font_tiny
import vga1_8x16 as font_small
import vga1_16x16 as font_medium
import vga1_16x32 as font_big 
# ------------------------------------------------------------------------------

ssid = 'GITHUB_TICKER'
password = '123'

FORM_FIELDS = ["ssid", "password", "username"]

def web_page():  
    html = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>GitHub Contributions Grid - Device Configuration</title>
                        <link rel="icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFwAAABcCAMAAADUMSJqAAAATlBMVEU501MmpkEAbTIORCkAAAAABgICDgYMPyY2y08AaC8DGAsjnDwurUMeiDUdcSwAWSkGOB4HJhInoD41xE0ljjgAZS4VXSQASSIJLhsMMhMZf/w/AAABMklEQVRo3u3XW46DMAyFYQO2A2mhQO/73+gQhZRhRkrOS1+Q/wV8sqK8HOIlnat8s/Iu6ep8nfBSwPuqXP/bvtTlLhE/VUinze5qpC7gfYXV43en20krNI221GhC6VHgh7nD+J0qvIjXeIYbbrjhhhtuuOGGG35A/AHbj4iPsD0S44evwTgTe9D2CVfQ1gXnCbIn/uQh28cdKnN5Dwm+cbeVSxzSIUsPyn+SZ5Z+Bjrg38nw4+J6o1y3/1/x1eR6yQeXlkq1srNdU8qt+JuQ3hutDZIG3BOWT7Y0WLLghJbwBo1pgPEh2hOMT0R46XA4ww033HDDDTfccMMNPyB+he1r2kNojhTGNa0WNCE+g/aZ10bQHpmYW8hu0aGYcnGHnvG7cd2lBa1t6WzlXeJKtPDSDyLJQch9E8q+AAAAAElFTkSuQmCC" type="image/x-icon">
                        <style>
                            body {
                                font-family: 'Roboto', sans-serif;
                                background-color: rgb(13, 17, 23);
                                color: white;
                                min-height: 100vh;
                                margin: 0;
                            }
                            
                            footer {
                                text-align: center;
                                bottom: 0;
                                position: absolute;
                                left: 0;
                                right: 0;
                            }
                            
                            footer a {
                                font-family: 'Roboto', sans-serif;
                                text-decoration: none;
                                color: #39D353;
                                min-height: 100vh;
                                margin: 0;
                            }
                            
                            .logo {
                                width: 10%;
                                display: block;
                                margin: auto;
                            }
                            
                            .title {
                                font-size: 24px;
                                text-align: center;
                                margin-top: 10px;
                                color: white !important;
                            }

                            .title a {
                                color: inherit;
                                text-decoration: none;
                            }
                            
                            .content-container {
                                top: 50%;
                                position: absolute;
                                transform: translateY(-50%);
                                width: 100%;
                            }

                            .form-container {
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                flex-direction: column;
                                width: 100%;
                            }
                                    
                            .form-container input[type="text"] {
                                background-color: #161B22;
                                border: 1px solid #DBE2E8;
                                color: white;
                                padding: 8px;
                                margin-right: 8px;
                                border-radius: 4px;
                                outline: none;
                            }

                            .form-container input[type="password"] {
                                background-color: #161B22;
                                border: 1px solid #DBE2E8;
                                color: white;
                                padding: 8px;
                                margin-right: 8px;
                                border-radius: 4px;
                                outline: none;
                            }
                            
                            .form-container button[type="submit"] {
                                background-color: #161B22;
                                border: 1px solid #39D353;
                                color: white;
                                padding: 8px 16px;
                                cursor: pointer;
                                border-radius: 4px;
                                outline: none;
                                transition: background-color 0.3s ease;
                                width: 50%;
                                margin: auto;
                                margin-top: 12px;
                            }

                            .form-container button[type="submit"]:hover {
                                background-color: #39D353;
                                color: black;
                            }
                            
                            #user-form {
                                display: flex;
                                flex-direction: column;
                                gap: 10px;
                                width: 100%;
                                max-width: 400px;
                            }

                            .heart {
                                color: #39D353; /* Heart color */
                            }
                        </style>
                    </head>
                    <body>
                        
                        <h1 class="title"><a href="#"></a></h1>
                        <div class="content-container">
                            <div class="form-container">
                                <form id="user-form" action="/" method="post">
                                    <input type="text" id="ssid" name="ssid" placeholder="Enter WiFi SSID" required>
                                    <input type="password" id="password" name="password" placeholder="Enter WiFi Password" required>
                                    <input type="text" id="username" name="username" placeholder="Enter Username" required>
                                    <button type="submit">Submit</button>
                                </form>
                            </div>
                        </div>
                        
                        <footer>
                            <p>Made with <span class="heart">♥</span> by <a href="https://x.com/pablogonmo">Pablo</a></p>
                        </footer>

                    </body>
                    </html>
                """
    return html

def success_page(data: str = None):  
    html = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>GitHub Contributions Grid - Device Configuration</title>
                        <link rel="icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFwAAABcCAMAAADUMSJqAAAATlBMVEU501MmpkEAbTIORCkAAAAABgICDgYMPyY2y08AaC8DGAsjnDwurUMeiDUdcSwAWSkGOB4HJhInoD41xE0ljjgAZS4VXSQASSIJLhsMMhMZf/w/AAABMklEQVRo3u3XW46DMAyFYQO2A2mhQO/73+gQhZRhRkrOS1+Q/wV8sqK8HOIlnat8s/Iu6ep8nfBSwPuqXP/bvtTlLhE/VUinze5qpC7gfYXV43en20krNI221GhC6VHgh7nD+J0qvIjXeIYbbrjhhhtuuOGGG35A/AHbj4iPsD0S44evwTgTe9D2CVfQ1gXnCbIn/uQh28cdKnN5Dwm+cbeVSxzSIUsPyn+SZ5Z+Bjrg38nw4+J6o1y3/1/x1eR6yQeXlkq1srNdU8qt+JuQ3hutDZIG3BOWT7Y0WLLghJbwBo1pgPEh2hOMT0R46XA4ww033HDDDTfccMMNPyB+he1r2kNojhTGNa0WNCE+g/aZ10bQHpmYW8hu0aGYcnGHnvG7cd2lBa1t6WzlXeJKtPDSDyLJQch9E8q+AAAAAElFTkSuQmCC" type="image/x-icon">
                        <style>
                            body {
                                font-family: 'Roboto', sans-serif;
                                background-color: rgb(13, 17, 23);
                                color: white;
                                min-height: 100vh;
                                margin: 0;
                            }
                            
                            footer {
                                text-align: center;
                                bottom: 0;
                                position: absolute;
                                left: 0;
                                right: 0;
                            }
                            
                            footer a {
                                font-family: 'Roboto', sans-serif;
                                text-decoration: none;
                                color: #39D353;
                                min-height: 100vh;
                                margin: 0;
                            }
                            
                            .logo {
                                width: 10%;
                                display: block;
                                margin: auto;
                            }
                            
                            .title {
                                font-size: 24px;
                                text-align: center;
                                margin-top: 10px;
                                color: white !important;
                            }

                            .title a {
                                color: inherit;
                                text-decoration: none;
                            }
                            
                            .content-container {
                                top: 50%;
                                position: absolute;
                                transform: translateY(-50%);
                                width: 100%;
                            }

                            .form-container {
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                flex-direction: column;
                                width: 100%;
                            }
                                    
                            .form-container input[type="text"] {
                                background-color: #161B22;
                                border: 1px solid #DBE2E8;
                                color: white;
                                padding: 8px;
                                margin-right: 8px;
                                border-radius: 4px;
                                outline: none;
                            }

                            .form-container input[type="password"] {
                                background-color: #161B22;
                                border: 1px solid #DBE2E8;
                                color: white;
                                padding: 8px;
                                margin-right: 8px;
                                border-radius: 4px;
                                outline: none;
                            }
                            
                            .form-container button[type="submit"] {
                                background-color: #161B22;
                                border: 1px solid #39D353;
                                color: white;
                                padding: 8px 16px;
                                cursor: pointer;
                                border-radius: 4px;
                                outline: none;
                                transition: background-color 0.3s ease;
                                width: 50%;
                                margin: auto;
                                margin-top: 12px;
                            }

                            .form-container button[type="submit"]:hover {
                                background-color: #39D353;
                                color: black;
                            }
                            
                            #user-form {
                                display: flex;
                                flex-direction: column;
                                gap: 10px;
                                width: 100%;
                                max-width: 400px;
                            }

                            .heart {
                                color: #39D353; /* Heart color */
                            }
                        </style>
                    </head>
                    <body>
                        
                        <h1 class="title"><a href="#"></a></h1>
                        <div class="content-container">
                            <div class="form-container">Success!</div></div>
                        
                        <footer>
                            <p>Made with <span class="heart">♥</span> by <a href="https://x.com/pablogonmo">Pablo</a></p>
                        </footer>

                    </body>
                    </html>
                """
    return html

def factory_reset():
    print (" > Erasing the device...")
    try:       
        file_to_remove = 'settings.json' 
        with open('settings.json', 'w') as f:
            config_str = '{"screen_rotation": 1, "led_status": true, "led_color": {"r": 0, "g": 0, "b": 255}, "last_refresh": 0}'
            f.write(config_str)
            f.close()
        print(f"File {file_to_remove} removed successfully.")

    except OSError as e:
        print(f"Error: {e.strerror}")

def read_data():
    try:
        with open('wifi.json', 'r', encoding = 'utf-8') as f:
            content = ujson.loads(f.read())
            f.close()
        return content
    except Exception as e:
        print(str(e))
        return False

def start_ap():
    tft = cfg_tft.config(1)
    if config.Config.initr == 6:
        tft.init(config.Config.initr)
    else:
        tft.init()

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password)

    while ap.active() == False:
        print('AP not active')
        utime.sleep(1)
        pass

    tft.text(font_small, 'Connect to WiFi: ', 0, 10)
    tft.text(font_small, f'{ssid}', 0, 25)
    tft.text(font_small, 'And access:', 0, 40)
    tft.text(font_small, 'http://192.168.4.1', 0, 55)
    print(' > Access http://192.168.4.1:80')
    print(ap.ifconfig())

    return ap

def configure_with_ap():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(('', 80))
    s.listen(5)

    print(' > Started listening at 0.0.0.0:80')

    while True:
        try:
            exit_loop = False
            conn, addr = s.accept()
            print(' > Got a connection from %s' % str(addr))
            request = conn.recv(1024).decode()
            
            if 'POST' in request:
                headers = request.split('\r\n')
                data = headers[-1]
                
                params = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
                

                json_data = ujson.dumps(params)

                f = open('wifi.json', 'w')
                f.write(json_data)
                f.close()
                            
                return_message = f'Success: {json_data}'
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + success_page(return_message)
                
                print(return_message)
                print(' > Configuration saved sucessfully')
                exit_loop = True
                
            else:
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + web_page()
                        
            conn.send(response)
            conn.close()
            
            if exit_loop:
                break
    
        except Exception as e:
            print('Error: '+str(e))
            
def connect_wifi(ap = None):
    if ap is not None:
        ap.active(False)
        print(ap.ifconfig())
    
    # Initialize the network interface
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Connect to the Wi-Fi network
    if not wlan.isconnected():
        print(' > Connecting to network...')
        
    # Connect to the Wi-Fi network
    data = read_data()
    ssid = data['ssid']
    password = data['password']
    wlan.connect(ssid, password)
        
    # Wait for connection
    while not wlan.isconnected():
        print(".", end="")
        utime.sleep(1)

    # Connection successful
    print("\n > Connected to network")
    print(' > Network configuration:', wlan.ifconfig())
    
def main():
    try:
        print('0. Starting Wifi Config...')
        ap = None

        if not read_data():
            ap = start_ap()
            configure_with_ap()
            factory_reset()
            machine.reset()
            print(' > Reset setting')

        utime.sleep(1)
        print(' > Reading settings...')
        data = read_data()

        data_str = ujson.dumps(data)
        print(data_str)
        
        connect_wifi(ap)
        
        print(' > End Wifi Config')
        
    except OSError as e:
        print("OSError:", e)
    finally:
        pass
