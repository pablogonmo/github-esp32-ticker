import os
import network
import urequests
import ujson
import utime
import ubinascii
import machine
from machine import Pin, SPI, RTC, reset
# SPI DRIVERS ------------------------------------------------------------------
import cfg_led
import cfg_tft
import cfg_buttons
import st7789 as driver
# CUSTOM MODULES ---------------------------------------------------------------
import settings
import config
import accesspoint
import miscellanea
# FONTS ------------------------------------------------------------------------
import vga1_8x8 as font_tiny
import vga1_8x16 as font_small
import vga1_16x16 as font_medium
import vga1_16x32 as font_big 
# ------------------------------------------------------------------------------


print("0. Initializing the device....")
# ------------ 1.0 Initialize the network
accesspoint.main()

unique_id = machine.unique_id()
DEVICE_ID = ubinascii.hexlify(unique_id).decode()

# ------------ 1.1 Initialize the led
led = cfg_led.config()

def write_apa102(led, red, green, blue, brightness=31):
    start_frame = b'\x00\x00\x00\x00'
    end_frame = b'\xff\xff\xff\xff'
    brightness = max(0, min(31, brightness))
    led_frame = bytes([0b11100000 | brightness, blue, green, red])
    led.write(start_frame + led_frame + end_frame)

led_color=settings.read_config('led_color')
r = led_color["r"]
b = led_color["g"]
g = led_color["b"]

led_status=settings.read_config('led_status')
if led_status == True:
    write_apa102(led, r, g, b) # Turn On
else:
    write_apa102(led, 0, 0, 0, 0) # Turn off
      
print(f' > Led status: {led_status}')
print(f' > Color: {led_color}')

# ------------ 1.2 Initialize the display
screen_rotation = settings.read_config('screen_rotation')
tft = cfg_tft.config(screen_rotation)

# ------------ 1.3 Initialize the configurations
config = config.Config()
initr=config.initr
square_size = config.square_size
spacing = config.spacing
font_size = config.font_size

screen_height = config.screen_height
screen_width = config.screen_width
stats_vertical_offset = config.stats_vertical_offset
menu_vertical_offset = config.menu_vertical_offset
avatar_size = config.avatar_size

if initr is None:
    tft.init()
else:
    tft.init(initr)

print(f' > Screen: {screen_height}x{screen_width}')
print(f' > Rotation: {screen_rotation}')

# GRAPH SETTINGS (do not change!) -----------------
grid_left_offset = int(screen_width/32) # fixed value
grid_vertical_offset = int(screen_height/16) # fixed value

background_color='violet'
grid_color='green'
print(f' > Background color: {background_color}')
print(f' > Grid color: {grid_color}')

bg_color1 = driver.color565(144,120,156)
bg_color2 = driver.color565(144,120,156)
bg_color3 = driver.color565(154,137,171)
bg_color4 = driver.color565(158,143,174)

boot_color1 = driver.color565(0,109,50)
boot_color2 = driver.color565(57,211,83)
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# ---------------------------- PROGRAM MODULES ---------------------------------
# ------------------------------------------------------------------------------

def no_op():
    pass

def reset():
    print(" > Rebooting device...")
    machine.reset()
    
def factory_reset():
    print (" > Erasing the device...")
    try:
        file_to_remove = 'wifi.json' 
        os.remove(file_to_remove)
        print(f" > File {file_to_remove} removed successfully.")
        
        file_to_remove = 'settings.json' 
        with open('settings.json', 'w') as f:
            config_str = '{"screen_rotation": 1, "led_status": true, "led_color": {"r": 0, "g": 0, "b": 255}, "last_refresh": 0}'
            f.write(config_str)
            f.close()
        print(f" > File {file_to_remove} removed successfully.")
        tft.deinit()
        accesspoint.main()
        main()
    
    except OSError as e:
        print(f"Error: {e.strerror}")

def sleep():
    print(" > Sleeping device...")
    
    led = cfg_led.config()
    write_apa102(led, 0, 0, 0, 0) # Turn off
    led_status = False
    
    tft = cfg_tft.config(screen_rotation)
    if initr is None:
        tft.init()
    else:
        tft.init(initr)
    tft.sleep_mode(True)
    
    machine.deepsleep()

def rotation():
    sr = settings.read_config('screen_rotation')
    
    if sr == 3:
        tft.rotation(1)
        sr = 1
    elif sr == 1:
        tft.rotation(3)
        sr = 3
    
    settings.save_config('screen_rotation',sr)
    print(f' > Changed screen rotation to: {sr}')
    main_screen()

def led_on_off():
    led = cfg_led.config()
    ls = settings.read_config('led_status')
    
    if ls == True:
        write_apa102(led, 0, 0, 0, 0) #Turn off
        ls = False
        settings.save_config('led_status',ls)
    else:
        write_apa102(led, r, g, b) # Purple
        ls = True
        settings.save_config('led_status',ls)
        
    print(f' > Changed led status to: {ls}')
    screen_rotation = settings.read_config('screen_rotation')
    tft = cfg_tft.config(screen_rotation)
    if initr is None:
        tft.init()
    else:
        tft.init(initr)
    main_screen()

def fetch_data(api_endpoint, filename):
    try:

        # Send GET request to download the image
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        headers = {"User-Agent": USER_AGENT}
        response = urequests.get(api_endpoint, headers=headers)

        if response.status_code == 200:
            # Parse JSON response
            json_data = response.json()

            # Save the JSON string to a file
            with open(filename, 'w') as file:
                ujson.dump(json_data, file)

        else:
            print(f"Error fetching {filename} data:", response.status_code)
            return

    except Exception as e:
        print("Exception:", e)
    finally:
        if response:
            response.close()

def load_data(filename, info):
    try:        
        # Open the JSON file and read its content
        with open(filename, 'r') as file:
            json_data = file.read()

        # Parse the JSON content to a dictionary
        dictionary = ujson.loads(json_data)

        return dictionary[info]
            
    except OSError as e:
        print(f'Failed to read file {filename}:', e)
        x = 0
        y = int(screen_height/3)
        tft.fill(driver.BLACK)
        tft.text(font_small, f'Failed to read file {filename}:', x, y, driver.WHITE, driver.BLACK)
    except ValueError as e:
        print(f'Failed to parse JSON {filename}:', e)
    
def fetch_and_save_avatar(api_endpoint, file_path):
    try:        
        # Make GET request
        response = urequests.get(api_endpoint)
        
        if response.status_code == 200:
            # Open a file in binary write mode
            with open(file_path, 'wb') as f:
                # Write the image data to the file
                f.write(response.content)
                
            print(" > Image saved successfully")
            return response.headers.get('Content-Type')
        else:
            print("Error fetching avatar image:", response.status_code)
            return
    except Exception as e:
        print("Exception:", e)
    finally:
        if response:
            response.close()

# ------------------------------------------------------------------------------
# ----------------------- STARTING THE MAIN PROGRAM ----------------------------
# ------------------------------------------------------------------------------
def main_screen():
    try:
        tft.fill(driver.BLACK)
        
        # ------------ 7. Display the avatar
        print("7. Displaying avatar....")
        x = 0
        y = 0
        tft.jpg(f'background-{screen_height}x{screen_width}-{background_color}.jpg', x, y, driver.SLOW)
              
        try:
            tft.jpg('avatar.jpg', x, y, driver.SLOW)
        except Exception as e:
            print('Error: '+str(e))
              
        print('Done')

        if screen_height == 80:              
            # ------------ 8. Create the sprites and background
            print("8. Generating layout....")
            y = int(screen_height/2)
            r = y-1
#             tft.circle(y, y, r, driver.WHITE)
            print("Done")

            # ------------ 10. Display the user info
            print("9. Displaying user info....")
            x = int(screen_width/2) + 7*grid_left_offset
            y = int(screen_height/5)
            user_repos = load_data('stats.json', 'public_repos')
            user_followers = load_data('stats.json','followers')
            user_stars = load_data('totalStars.json','totalStars')
            user_contributions = load_data('totalContributions.json','totalContributions')

            tft.text(font_small, f"{user_stars:,}", 			x, 3*y+4*stats_vertical_offset, driver.WHITE, bg_color4)
            tft.text(font_small, f"{user_followers:,}", 		x, 2*y+3*stats_vertical_offset, driver.WHITE, bg_color3)
            tft.text(font_small, f"{user_contributions:,}", 	x,   y+2*stats_vertical_offset, driver.WHITE, bg_color2)
            tft.text(font_small, f"{user_repos:,}", 			x,       stats_vertical_offset, driver.WHITE, bg_color1)
            
            print("Done")

            button = cfg_buttons.Buttons(
                                         pin_number=0,
                                         short_press_callback=grid_q1,
                                         long_press_callback=menu_option1,
                                         double_click_callback=no_op
                                         )

        else:
            # ------------ 8. Create the sprites and background
            print("8. Generating layout....")
            y = int(avatar_size/2)+x
            r = int(avatar_size/2)-1
#             tft.circle(y, y, r, driver.WHITE)
            print("Done")

            # ------------ 10. Display the user info
            print("9. Displaying user info....")
            x = int(screen_width/2) + 7*grid_left_offset
            y = int(screen_height/5)
            user_repos = load_data('stats.json', 'public_repos')
            user_followers = load_data('stats.json','followers')
            user_stars = load_data('totalStars.json','totalStars')
            user_contributions = load_data('totalContributions.json','totalContributions')

            tft.text(font_medium, f"{user_stars:,}", 		x, 130, driver.WHITE, bg_color4)
            tft.text(font_medium, f"{user_followers:,}", 	x, 94, driver.WHITE, bg_color3)
            tft.text(font_medium, f"{user_contributions:,}", x, 58, driver.WHITE, bg_color2)
            tft.text(font_medium, f"{user_repos:,}", 		x, 22, driver.WHITE, bg_color1)
            
            print("Done")

            button1 = cfg_buttons.Buttons(
                                          pin_number=0,
                                          short_press_callback=grid_q1,
                                          long_press_callback=menu_option1,
                                          double_click_callback=no_op
                                          )
              
            button2 = cfg_buttons.Buttons(
                                          pin_number=14,
                                          short_press_callback=grid_q4,
                                          long_press_callback=menu_option1,
                                          double_click_callback=no_op
                                          )
              
        print('All done!')
 
    except OSError as e:
        print("OSError:", e)
    finally:
        pass

def grid_q1():
    try:
        tft.fill(driver.BLACK)

        # Draw the edges of the grid
        x = 0
        y = int((screen_height - 7 * square_size - 6 * spacing) / 2)
        w = screen_width
        h = screen_height - y

        # Draw the grid of squares with colors corresponding to the weekdays
        print("9.2.1. Loading contributions from saved json file....")
        filename = '/contributions.json'
        with open(filename, 'r') as file:
            contributions = ujson.load(file)
        print("Done")

        print("9.2.2. Setting grid colors....")
        
        # Define color mapping
        color_mapping = {
#             '#ebedf0': (22, 27, 34),  # Light gray
            '#9be9a8': (14, 68, 41),  # Light green
            '#40c463': (0, 109, 50),  # Green
            '#30a14e': (38, 166, 65), # Dark green
            '#216e39': (57, 211, 83)  # Darker green
        }
        
        # Calculate the starting position for the grid
        grid_start_x = int((screen_width - 13*square_size - 12*spacing)/2) #spacing + 1  # 1px for the edge of the grid
        grid_start_y = int((screen_height - 7 * square_size - 6 * spacing) / 2)  # Center vertically
        
        start_week = 1
        # Iterate over the weeks and render the contributions
        for row in range(7):  # 7 rows for days of the week
            for col in range(13):  # 13 columns for weeks
                date_index = (start_week + col) * 7 + row  # Index of the date in the list
                if date_index < len(contributions):
                    date = contributions[date_index]['date']
                    color_key = contributions[date_index]['color']
                    if color_key in color_mapping:
                        color_rgb = color_mapping[color_key]
                    else:
                        # Default to black if color is not found in mapping
                        color_rgb = (0, 0, 0)

                    x = col * (square_size + spacing) + grid_start_x  # Align to the right
                    y = row * (square_size + spacing) + grid_start_y  # Align to the top

                    tft.fill_rect(x, y, square_size, square_size, driver.color565(*color_rgb))

        print("Done")

        # Draw the footer
        print("9.3. Drawing the footer....")
        x = int(screen_width/2-font_size*3/4)
        y = int(screen_height-font_size/2)
        tft.text(font_tiny, "1/4", x, y, driver.WHITE)
          
        print('All done!')
    
        if screen_height == 80:
            button = cfg_buttons.Buttons(
                                        pin_number=0,
                                        short_press_callback=grid_q2,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
        else:
            button1 = cfg_buttons.Buttons(
                                        pin_number=0,
                                        short_press_callback=grid_q2,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
            button2 = cfg_buttons.Buttons(
                                        pin_number=14,
                                        short_press_callback=main_screen,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
         
    except OSError as e:
        print("OSError:", e)
    finally:
        pass

def grid_q2():
    try:
        tft.fill(driver.BLACK)

        # Draw the edges of the grid
        x = 0
        y = int((screen_height - 7 * square_size - 6 * spacing) / 2)
        w = screen_width
        h = screen_height - y

        # Draw the grid of squares with colors corresponding to the weekdays
        print("9.2.1. Loading contributions from saved json file....")
        filename = '/contributions.json'
        with open(filename, 'r') as file:
            contributions = ujson.load(file)
        print("Done")

        print("9.2.2. Setting grid colors....")
        
        # Define color mapping
        color_mapping = {
#             '#ebedf0': (22, 27, 34),  # Light gray
            '#9be9a8': (14, 68, 41),  # Light green
            '#40c463': (0, 109, 50),  # Green
            '#30a14e': (38, 166, 65), # Dark green
            '#216e39': (57, 211, 83)  # Darker green
        }
        
        # Calculate the starting position for the grid
        grid_start_x = int((screen_width - 13*square_size - 12*spacing)/2) #spacing + 1  # 1px for the edge of the grid
        grid_start_y = int((screen_height - 7 * square_size - 6 * spacing) / 2)  # Center vertically
        
        start_week = 14
        # Iterate over the weeks and render the contributions
        for row in range(7):  # 7 rows for days of the week
            for col in range(13):  # 13 columns for weeks
                date_index = (start_week + col) * 7 + row  # Index of the date in the list
                if date_index < len(contributions):
                    date = contributions[date_index]['date']
                    color_key = contributions[date_index]['color']
                    if color_key in color_mapping:
                        color_rgb = color_mapping[color_key]
                    else:
                        # Default to black if color is not found in mapping
                        color_rgb = (0, 0, 0)

                    x = col * (square_size + spacing) + grid_start_x  # Align to the right
                    y = row * (square_size + spacing) + grid_start_y  # Align to the top

                    tft.fill_rect(x, y, square_size, square_size, driver.color565(*color_rgb))

        print("Done")
                  
        # Draw the footer
        print("9.3. Drawing the footer....")
        x = int(screen_width/2-font_size*3/4)
        y = int(screen_height-font_size/2)
        tft.text(font_tiny, "2/4", x, y, driver.WHITE)
          
        print('All done!')
    
        if screen_height == 80:
            button = cfg_buttons.Buttons(
                                        pin_number=0,
                                        short_press_callback=grid_q3,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
        else:
            button1 = cfg_buttons.Buttons(
                                        pin_number=0,
                                        short_press_callback=grid_q3,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
            button2 = cfg_buttons.Buttons(
                                        pin_number=14,
                                        short_press_callback=grid_q1,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
         
    except OSError as e:
        print("OSError:", e)
    finally:
        pass

def grid_q3():
    try:
        tft.fill(driver.BLACK)

        # Draw the edges of the grid
        x = 0
        y = int((screen_height - 7 * square_size - 6 * spacing) / 2)
        w = screen_width
        h = screen_height - y

        # Draw the grid of squares with colors corresponding to the weekdays
        print("9.2.1. Loading contributions from saved json file....")
        filename = '/contributions.json'
        with open(filename, 'r') as file:
            contributions = ujson.load(file)
        print("Done")

        print("9.2.2. Setting grid colors....")
        
        # Define color mapping
        color_mapping = {
#             '#ebedf0': (22, 27, 34),  # Light gray
            '#9be9a8': (14, 68, 41),  # Light green
            '#40c463': (0, 109, 50),  # Green
            '#30a14e': (38, 166, 65), # Dark green
            '#216e39': (57, 211, 83)  # Darker green
        }
        
        # Calculate the starting position for the grid
        grid_start_x = int((screen_width - 13*square_size - 12*spacing)/2) #spacing + 1  # 1px for the edge of the grid
        grid_start_y = int((screen_height - 7 * square_size - 6 * spacing) / 2)  # Center vertically
        
        start_week = 27
        # Iterate over the weeks and render the contributions
        for row in range(7):  # 7 rows for days of the week
            for col in range(13):  # 13 columns for weeks
                date_index = (start_week + col) * 7 + row  # Index of the date in the list
                if date_index < len(contributions):
                    date = contributions[date_index]['date']
                    color_key = contributions[date_index]['color']
                    if color_key in color_mapping:
                        color_rgb = color_mapping[color_key]
                    else:
                        # Default to black if color is not found in mapping
                        color_rgb = (0, 0, 0)

                    x = col * (square_size + spacing) + grid_start_x  # Align to the right
                    y = row * (square_size + spacing) + grid_start_y  # Align to the top

                    tft.fill_rect(x, y, square_size, square_size, driver.color565(*color_rgb))

        print("Done")

        # Draw the footer
        print("9.3. Drawing the footer....")
        x = int(screen_width/2-font_size*3/4)
        y = int(screen_height-font_size/2)
        tft.text(font_tiny, "3/4", x, y, driver.WHITE)
          
        print('All done!')
    
        if screen_height == 80:
            button = cfg_buttons.Buttons(
                                        pin_number=0,
                                        short_press_callback=grid_q4,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
        else:
            button1 = cfg_buttons.Buttons(
                                        pin_number=0,
                                        short_press_callback=grid_q4,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
            button2 = cfg_buttons.Buttons(
                                        pin_number=14,
                                        short_press_callback=grid_q2,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
         
    except OSError as e:
        print("OSError:", e)
    finally:
        pass

def grid_q4():
    try:
        tft.fill(driver.BLACK)

        # Draw the edges of the grid
        x = 0
        y = int((screen_height - 7 * square_size - 6 * spacing) / 2)
        w = screen_width
        h = screen_height - y

        # Draw the grid of squares with colors corresponding to the weekdays
        print("9.2.1. Loading contributions from saved json file....")
        filename = '/contributions.json'
        with open(filename, 'r') as file:
            contributions = ujson.load(file)
        print("Done")

        print("9.2.2. Setting grid colors....")
        
        # Define color mapping
        color_mapping = {
#             '#ebedf0': (22, 27, 34),  # Light gray
            '#9be9a8': (14, 68, 41),  # Light green
            '#40c463': (0, 109, 50),  # Green
            '#30a14e': (38, 166, 65), # Dark green
            '#216e39': (57, 211, 83)  # Darker green
        }
        
        # Calculate the starting position for the grid
        grid_start_x = int((screen_width - 13*square_size - 12*spacing)/2) #spacing + 1  # 1px for the edge of the grid
        grid_start_y = int((screen_height - 7 * square_size - 6 * spacing) / 2)  # Center vertically
        
        start_week = 40
        # Iterate over the weeks and render the contributions
        for row in range(7):  # 7 rows for days of the week
            for col in range(13):  # 13 columns for weeks
                date_index = (start_week + col) * 7 + row  # Index of the date in the list
                if date_index < len(contributions):
                    date = contributions[date_index]['date']
                    color_key = contributions[date_index]['color']
                    if color_key in color_mapping:
                        color_rgb = color_mapping[color_key]
                    else:
                        # Default to black if color is not found in mapping
                        color_rgb = (0, 0, 0)

                    x = col * (square_size + spacing) + grid_start_x  # Align to the right
                    y = row * (square_size + spacing) + grid_start_y  # Align to the top

                    tft.fill_rect(x, y, square_size, square_size, driver.color565(*color_rgb))

        print("Done")
                  
        # Draw the footer
        print("9.3. Drawing the footer....")
        x = int(screen_width/2-font_size*3/4)
        y = int(screen_height-font_size/2)
        tft.text(font_tiny, "4/4", x, y, driver.WHITE)
          
        print('All done!')
    
        if screen_height == 80:
            button = cfg_buttons.Buttons(
                                        pin_number=0,
                                        short_press_callback=main_screen,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
        else:
            button1 = cfg_buttons.Buttons(
                                        pin_number=0,
                                        short_press_callback=main_screen,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
            button2 = cfg_buttons.Buttons(
                                        pin_number=14,
                                        short_press_callback=grid_q3,
                                        long_press_callback=menu_option1,
                                        double_click_callback=no_op
                                        )
         
    except OSError as e:
        print("OSError:", e)
    finally:
        pass

def menu_option1():
    print("Menu > Rotation")
    tft.fill(bg_color1)
    x = spacing
    y = spacing
    h = screen_height-2*spacing
    w = screen_width-2*spacing
    tft.rect(x, y, w, h, driver.WHITE)
    tft.fill_rect(x+1, y+1, w-2, h-2, driver.BLACK)
    
    x = grid_left_offset+spacing
    y = 2*spacing
    
    if screen_height == 80:
        tft.text(font_small, " MENU ", x, 0, driver.WHITE)
        x = grid_left_offset+spacing
        y = 3*spacing+font_size
        tft.text(font_small, "  Rotation        ", x, y, driver.BLACK, driver.YELLOW)
        tft.text(font_small, " Led On/Off       ", x, y+font_size+spacing, driver.WHITE)
        tft.text(font_small, " Factory Reset    ", x, y+2*(font_size+spacing), driver.WHITE)

        button = cfg_buttons.Buttons(
                                    pin_number=0,
                                    short_press_callback=menu_option2,
                                    long_press_callback=main_screen,
                                    double_click_callback=rotation
                                    )
    else:
        tft.text(font_big, " MENU ", x, 0, driver.WHITE)
        x = grid_left_offset+spacing
        y = int(screen_height/8)
        tft.text(font_big, "  Rotation        ", x, 1*menu_vertical_offset, driver.BLACK, driver.YELLOW)
        tft.text(font_big, " Sleep Mode       ", x, 2*menu_vertical_offset, driver.WHITE)
        tft.text(font_big, " Factory Reset    ", x, 3*menu_vertical_offset, driver.WHITE)
        tft.text(font_big, " Exit             ", x, 4*menu_vertical_offset, driver.WHITE)

        button1 = cfg_buttons.Buttons(
                                    pin_number=0,
                                    short_press_callback=menu_option2,
                                    long_press_callback=main_screen,
                                    double_click_callback=rotation
                                    )

        button2 = cfg_buttons.Buttons(
                                    pin_number=14,
                                    short_press_callback=menu_option4,
                                    long_press_callback=main_screen,
                                    double_click_callback=rotation
                                    )

def menu_option2():
    print("Menu > Led On/Off")
    tft.fill(bg_color1)
    x = spacing
    y = spacing
    h = screen_height-2*spacing
    w = screen_width-2*spacing
    tft.rect(x, y, w, h, driver.WHITE)
    tft.fill_rect(x+1, y+1, w-2, h-2, driver.BLACK)
    
    x = grid_left_offset+spacing
    y = int(screen_height/5)

    if screen_height == 80:
        tft.text(font_small, " MENU ", x, 0, driver.WHITE)
        x = grid_left_offset+spacing
        y = 3*spacing+font_size
        tft.text(font_small, " Rotation         ", x, y, driver.WHITE)
        tft.text(font_small, "  Led On/Off      ", x, y+font_size+spacing, driver.BLACK, driver.YELLOW)
        tft.text(font_small, " Factory Reset    ", x, y+2*(font_size+spacing), driver.WHITE)
        
        button = cfg_buttons.Buttons(
                                pin_number=0,
                                short_press_callback=menu_option3,
                                long_press_callback=main_screen,
                                double_click_callback=led_on_off
                                )
    else:
        tft.text(font_big, " MENU ", x, 0, driver.WHITE)
        x = grid_left_offset+spacing
        y = int(screen_height/8)
        tft.text(font_big, " Rotation         ", x, 1*menu_vertical_offset, driver.WHITE)
        tft.text(font_big, "  Sleep Mode      ", x, 2*menu_vertical_offset, driver.BLACK, driver.YELLOW)
        tft.text(font_big, " Factory Reset    ", x, 3*menu_vertical_offset, driver.WHITE)
        tft.text(font_big, " Exit             ", x, 4*menu_vertical_offset, driver.WHITE)

        button1 = cfg_buttons.Buttons(
                                    pin_number=0,
                                    short_press_callback=menu_option3,
                                    long_press_callback=main_screen,
                                    double_click_callback=sleep
                                    )

        button2 = cfg_buttons.Buttons(
                                    pin_number=14,
                                    short_press_callback=menu_option1,
                                    long_press_callback=main_screen,
                                    double_click_callback=sleep
                                    )

def menu_option3():
    print("Menu > Factory Reset")
    tft.fill(bg_color1)
    x = spacing
    y = spacing
    h = screen_height-2*spacing
    w = screen_width-2*spacing
    tft.rect(x, y, w, h, driver.WHITE)
    tft.fill_rect(x+1, y+1, w-2, h-2, driver.BLACK)
    
    x = grid_left_offset+spacing
    y = int(screen_height/4)
    
    if screen_height == 80:
        tft.text(font_small, " MENU ", x, 0, driver.WHITE)
        x = grid_left_offset+spacing
        y = 3*spacing+font_size
        tft.text(font_small, " Rotation         ", x, y, driver.WHITE)
        tft.text(font_small, " Led On/Off       ", x, y+font_size+spacing, driver.WHITE)
        tft.text(font_small, "  Factory Reset   ", x, y+2*(font_size+spacing), driver.BLACK, driver.YELLOW)
        
        button = cfg_buttons.Buttons(
                                    pin_number=0,
                                    short_press_callback=menu_option4,
                                    long_press_callback=main_screen,
                                    double_click_callback=factory_reset
                                    )
    else:
        tft.text(font_big, " MENU ", x, 0, driver.WHITE)
        x = grid_left_offset+spacing
        y = int(screen_height/8)
        tft.text(font_big, " Rotation         ", x, 1*menu_vertical_offset, driver.WHITE)
        tft.text(font_big, " Sleep Mode       ", x, 2*menu_vertical_offset, driver.WHITE)
        tft.text(font_big, "  Factory Reset   ", x, 3*menu_vertical_offset, driver.BLACK, driver.YELLOW)
        tft.text(font_big, " Exit             ", x, 4*menu_vertical_offset, driver.WHITE)
        
        button1 = cfg_buttons.Buttons(
                                    pin_number=0,
                                    short_press_callback=menu_option4,
                                    long_press_callback=main_screen,
                                    double_click_callback=factory_reset
                                    )
        
        button2 = cfg_buttons.Buttons(
                                    pin_number=14,
                                    short_press_callback=menu_option2,
                                    long_press_callback=main_screen,
                                    double_click_callback=factory_reset
                                    )

def menu_option4():
    print("Menu > Exit")
    tft.fill(bg_color1)
    x = spacing
    y = spacing
    h = screen_height-2*spacing
    w = screen_width-2*spacing
    tft.rect(x, y, w, h, driver.WHITE)
    tft.fill_rect(x+1, y+1, w-2, h-2, driver.BLACK)
    
    x = grid_left_offset+spacing
    y = int(screen_height/5)
    
    if screen_height == 80:
        tft.text(font_small, " MENU ", x, 0, driver.WHITE)
        x = grid_left_offset+spacing
        y = 3*spacing+font_size
        tft.text(font_small, " Led On/Off       ", x, y, driver.WHITE)
        tft.text(font_small, " Factory Reset    ", x, y+font_size+spacing, driver.WHITE)
        tft.text(font_small, "  Exit            ", x, y+2*(font_size+spacing), driver.BLACK, driver.YELLOW)
    
        button = cfg_buttons.Buttons(
                                    pin_number=0,
                                    short_press_callback=menu_option1,
                                    long_press_callback=main_screen,
                                    double_click_callback=main_screen
                                    )
    else:
        tft.text(font_big, " MENU ", x, 0, driver.WHITE)
        x = grid_left_offset+spacing
        y = int(screen_height/8)
        tft.text(font_big, " Rotation         ", x, 1*menu_vertical_offset, driver.WHITE)
        tft.text(font_big, " Sleep Mode       ", x, 2*menu_vertical_offset, driver.WHITE)
        tft.text(font_big, " Factory Reset    ", x, 3*menu_vertical_offset, driver.WHITE)
        tft.text(font_big, "  Exit            ", x, 4*menu_vertical_offset, driver.BLACK, driver.YELLOW)
    
        button1 = cfg_buttons.Buttons(
                                    pin_number=0,
                                    short_press_callback=menu_option1,
                                    long_press_callback=main_screen,
                                    double_click_callback=main_screen
                                    )
    
        button2 = cfg_buttons.Buttons(
                                    pin_number=14,
                                    short_press_callback=menu_option3,
                                    long_press_callback=main_screen,
                                    double_click_callback=main_screen
                                    )

def main():
    try:
        x = grid_left_offset
        y = screen_height - grid_vertical_offset
        h = 0
        w = screen_width - 2*grid_left_offset
        bar = int(screen_width/6)

        # APP SETTINGS (do not change!) ------------------------------------------------
        content = accesspoint.read_data()
        GITHUB_USER_NAME = content['username']
        # ------------------------------------------------------------------------------
        
        # ------------ 1. Download the backgrounds
        last_refresh = settings.read_config('last_refresh')
        now = miscellanea.get_current_timestamp()

        if last_refresh == 0:
            print("1. Downloading the backgrounds....")
            
            filename = f'background-{screen_height}x{screen_width}-{background_color}.jpg'
            api_endpoint = f'https://github-esp32-ticker.vercel.app/img/{filename}'
            content_type = fetch_and_save_avatar(api_endpoint, filename)
            print(f" > {filename}: Done")
                
            filename = f'init-{screen_height}x{screen_width}-{background_color}.jpg'
            api_endpoint = f'https://github-esp32-ticker.vercel.app/img/{filename}'
            content_type = fetch_and_save_avatar(api_endpoint, filename)
            print(f" > {filename}: Done")

                
        if now - last_refresh > 86400:
            # ------------ 2. Initialize the bootloader
            print("2. Initializing the bootloader....")
            tft.jpg(f'init-{screen_height}x{screen_width}-{background_color}.jpg', 0, 0, driver.SLOW)
            tft.hline(x, y, w, boot_color1)
            
            # ------------ 4. Download the avatar
            print("4. Downloading GitHub avatar....")
            filename = 'avatar.jpg'
            GITHUB_DATA = 'githubAvatar'
            api_endpoint = f'https://github-esp32-ticker.vercel.app/api/{GITHUB_DATA}?username={GITHUB_USER_NAME}&size={avatar_size}&color={background_color}'
            content_type = fetch_and_save_avatar(api_endpoint, filename)
            tft.hline(x, y, 2*bar, boot_color2)
            print("Done")
                
            # ------------ 5. Fetch user info
            print("5. Fetching user info....")
               
            filename = 'stats.json'
            api_endpoint = f'https://api.github.com/users/{GITHUB_USER_NAME}'
            fetch_data(api_endpoint, filename)
            print(' > '+filename+': ok')
            tft.hline(x, y, 3*bar, boot_color2)
               
            filename = 'totalContributions.json'
            GITHUB_DATA = 'githubYearData'
            api_endpoint = f'https://github-esp32-ticker.vercel.app/api/{GITHUB_DATA}?username={GITHUB_USER_NAME}'
            fetch_data(api_endpoint, filename)
            print(' > '+filename+': ok')
            tft.hline(x, y, 4*bar, boot_color2)
               
            filename = 'totalStars.json'
            GITHUB_DATA = 'githubStars'
            api_endpoint = f'https://github-esp32-ticker.vercel.app/api/{GITHUB_DATA}?username={GITHUB_USER_NAME}'
            fetch_data(api_endpoint, filename)
            print(' > '+filename+': ok')
            tft.hline(x, y, 5*bar, boot_color2)

            filename = 'contributions.json'
            GITHUB_DATA = 'githubData'
            api_endpoint = f'https://github-esp32-ticker.vercel.app/api/{GITHUB_DATA}?username={GITHUB_USER_NAME}'
            fetch_data(api_endpoint, filename)
            print(' > '+filename+': ok')
            tft.hline(x, y, 6*bar, boot_color2)
            
            settings.save_config('last_refresh',now)
                   
        print("Done")
 
        # ------------ 6. Rendering main screen
        print("6. Rendering main screen....")
        main_screen()
    
    except OSError as e:
        print("OSError:", e)
    finally:
        pass

main()
