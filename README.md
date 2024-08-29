<h1 align = "center"> 🌟Github Contributions Ticker🌟</h1>

# 0️⃣ Introduction
This project contains all the necessary code to build an ESP32 based ticker, that downloads the github contributions and statistics from the github GraphQL API and displays them in an LCD screen.

<img src="img/ticker-black.png" align="center">


I have coded 2 versions:

1.- a 0.96" usb dongle version with no contgributions matrix, displays the stats and user avatar only

2.- a 1.9" battery powered version that displays a main screen (stats + user avatar) and the github contributions matrix in quarters


# 1️⃣  Requirements
You will need all the following to complete the installation and setup of the device:

- While all the data used is publicly available and can be checked for any github user you want, you'll need a github API KEY in order to fetch the data. This is detailed in section 2

- Either the T-Dongle-S3 or the T-Display-S3. You can purchase them using the links down below in section 3

- For the T-Display-S3 the battery is optional, as you an power it using any usb-c cable

- A backend server to retrieve all the data, and fetch it as json files. Configuration is described in section 4

- Flash the devices with the micropython firmware. Environment set up and flashing process is described in section 5

- Alternatively you can generate binary files to flash the device easily, or you can use the binaries provided in the files folder


# 2️⃣ Generating a Github personal access token
The back-end server fetched the source data from github directly by means of the graphQL API which is publicly available. The only required is a personal access token which can be generated following the steps:

1.- Go to your github account settings

2.- Under Developer Settings > Personal Access Tokens > Personal access tokens (classic) https://github.com/settings/tokens

3.- Click on generate new token, classic for general use

4.- Set a wide expiration date, and grant the minimum permissions, usually read, user and repo should be sufficient


# 3️⃣ Shopping List
If you want to support the project, you can use the below affiliate links to purchase the PCB's and batteries:

| Product                 | SOC        | Flash | Resolution | Size      | Driver    |
| ----------------------- | ---------- | ----- | ---------- | --------  | --------  |
| [T-Dongle-S3][1]        | ESP32-S3R8 | 16MB  | 80x160     | 0.96 Inch | ST7735    |
| [T-Display-S3][2]       | ESP32-S3R8 | 16MB  | 170x320    | 1.9 Inch  | ST7789    |

[1]: https://www.aliexpress.us/item/3256804673688886.html
[2]: https://www.aliexpress.us/item/3256804310228562.html


# 4️⃣  Back-End server installation



# 5️⃣  Micropython environment set up

* [Micropython](https://github.com/Xinyuan-LilyGO/lilygo-micropython)




# 6️⃣  Binaries compilation


# 7️⃣ FAQ

4. **Can't upload any sketch，Please enter the upload mode manually.**
   * Connect the board via the USB cable
   * Press and hold the **BOOT** button , While still pressing the **BOOT** button
   * Press **RST** button
   * Release the **RST** button
   * Release the **BOOT** button (If there is no **BOOT** button, disconnect IO0 from GND.)
   * Upload sketch
   * Press the **RST** button to exit download mode

6. **If all the above are invalid, please flash the factory firmware for quick verification, please check [here](https://github.com/Xinyuan-LilyGO/T-Display-S3/firmware/README.MD)**


# 8️⃣  Attributions

The following repositories have been used to build this project:
 
Lilygo hardware repos:
- https://github.com/Xinyuan-LilyGO/T-Dongle-S3/blob/main/image/Pins.png
- https://github.com/Xinyuan-LilyGO/T-Display-S3/blob/main/image/T-DISPLAY-S3.jpg

Drivers for the displays:
- russhughes (T-Display-S3): https://github.com/russhughes/st7789s3_mpy
- mmMicky(T-Dongle-S3): https://github.com/mmMicky/st7735_mpy
