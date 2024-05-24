from PIL import Image, ImageDraw, ImageColor, ImageFont, ImageStat
import subprocess
import time
import musicpd
import os
import os.path
from os import path
import RPi.GPIO as GPIO
from mediafile import MediaFile
from io import BytesIO
from numpy import mean 
from PIL import ImageFilter
from PIL import ImageColor
import yaml
import urllib.parse
import board
from digitalio import DigitalInOut, Direction
from adafruit_rgb_display import st7789
import subprocess
import re

# set default config for Adafruit 1.3" Color TFT Bonnet for Raspberry Pi

__version__ = "0.1.0"

# get the path of the script
script_path = os.path.dirname(os.path.abspath( __file__ ))
# set script path as current directory - 
os.chdir(script_path)

confile = 'config.yml'

# Read config.yml for user config
if path.exists(confile):
 
    with open(confile) as config_file:
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        displayConf = data['display']
        TIMEBAR = displayConf['timebar']
        BLANK_SCREEN = displayConf['blank']
        SHADE = displayConf['shadow']
        ICON_SHOW = displayConf['icoShow']
        COVER_SHOW = displayConf['covShow']
        ICON_FILL_COLOR = displayConf['icoFillCol']
        ICON_OUTLINE_COLOR = displayConf['icoOutCol']
        VOL_BAR_TOP = displayConf['volBarTop']
        VOL_BAR_COLOR = displayConf['volBarColor']  
        SONG_PROGBAR_COLOR = displayConf['sProgBarColor']
        FONT_COLOR = displayConf['fCol']
        FONT_SHADOW_COLOR = displayConf['sCol']  
        DISP_BACKGROUND_COLOR= displayConf['dispBgCol']  
        ARTIST_TOP = displayConf['artistTop']
        ALBUM_TOP = displayConf['albumTop']
        TITLE_TOP = displayConf['titleTop']
        moodeConf = data['moode']
        DEFAULT_PLAYLIST = moodeConf['defPlaylist'] 
     
# Standard SPI connections for ST7789
# Create ST7789 LCD display class.

        cs_pin = DigitalInOut(board.CE0)
        dc_pin = DigitalInOut(board.D25)
        reset_pin = DigitalInOut(board.D24)
        BAUDRATE = 24000000
        spi = board.SPI()
        disp = st7789.ST7789(
            spi,
            height=240,
            y_offset=80,
            rotation=180,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=BAUDRATE,
        )

# Input pins:
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT

# Initialize display.

WIDTH = 240
HEIGHT = 240
font_s = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',20)
font_m = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',24)
font_l = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',30)


img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0, 25))

bt_back = Image.open(script_path + '/images/bta.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
ap_back = Image.open(script_path + '/images/airplay.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
sp_back = Image.open(script_path + '/images/spotify.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")

draw = ImageDraw.Draw(img, 'RGBA')

def isServiceActive(service):

    waiting = True
    count = 0
    active = False

    while (waiting == True):
        
        process = subprocess.run(['systemctl','is-active',service], check=False, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        stat = output[:6]

        if stat == 'active':
            waiting = False
            active = True

        if count > 29:
            waiting = False

        count += 1
        time.sleep(1)

    return active


def getMoodeMetadata(filename):
    # Initalise dictionary
    metaDict = {}
    
    if path.exists(filename):
        # add each line fo a list removing newline
        nowplayingmeta = [line.rstrip('\n') for line in open(filename)]
        i = 0
        while i < len(nowplayingmeta):
            # traverse list converting to a dictionary
            (key, value) = nowplayingmeta[i].split('=', 1)
            metaDict[key] = value
            i += 1
        
        metaDict['coverurl'] = urllib.parse.unquote(metaDict['coverurl'])
        
        metaDict['source'] = 'library'
        if 'file' in metaDict:
            if (metaDict['file'].find('http://', 0) > -1) or (metaDict['file'].find('https://', 0) > -1):
                # set radio stream to true
                metaDict['source'] = 'radio'
                # if radio station has arist and title in one line separated by a hyphen, split into correct keys
                if metaDict['title'].find(' - ', 0) > -1:
                    (art,tit) = metaDict['title'].split(' - ', 1)
                    metaDict['artist'] = art
                    metaDict['title'] = tit
            elif metaDict['file'].find('Bluetooth Active', 0) > -1:
                metaDict['source'] = 'bluetooth'
            elif metaDict['file'].find('Airplay Active', 0) > -1:
                metaDict['source'] = 'airplay'
            elif metaDict['file'].find('Spotify Active', 0) > -1:
                metaDict['source'] = 'spotify'
            elif metaDict['file'].find('Squeezelite Active', 0) > -1:
                metaDict['source'] = 'squeeze'
            elif metaDict['file'].find('Input Active', 0) > -1:
                metaDict['source'] = 'input' 
            

    # return metadata
    return metaDict

def get_cover(metaDict):

    cover = None
    cover = Image.open(script_path + '/images/default-cover-v6.jpg')

    covers = ['Cover.jpg', 'cover.jpg', 'Cover.jpeg', 'cover.jpeg', 'Cover.png', 'cover.png', 'Cover.tif', 'cover.tif', 'Cover.tiff', 'cover.tiff',
		'Folder.jpg', 'folder.jpg', 'Folder.jpeg', 'folder.jpeg', 'Folder.png', 'folder.png', 'Folder.tif', 'folder.tif', 'Folder.tiff', 'folder.tiff']
    if metaDict['source'] == 'radio':
        if 'coverurl' in metaDict:
            rc = '/var/local/www/' + metaDict['coverurl']
            if path.exists(rc):
                if rc != '/var/local/www/images/default-cover-v6.svg':
                    cover = Image.open(rc)

    elif metaDict['source'] == 'airplay':
        cover = ap_back
    elif metaDict['source'] == 'bluetooth':
        cover = bt_back
    elif metaDict['source'] == 'spotify':
        cover = sp_back

    else:
        if 'file' in metaDict:
            if len(metaDict['file']) > 0:

                fp = '/var/lib/mpd/music/' + metaDict['file']   
                mf = MediaFile(fp)     
                if mf.art:
                    cover = Image.open(BytesIO(mf.art))
                    return cover
                else:
                    for it in covers:
                        cp = os.path.dirname(fp) + '/' + it
                        
                        if path.exists(cp):
                            cover = Image.open(cp)
                            return cover
    return cover


def main():

    # Turn on the Backlight
    backlight = DigitalInOut(board.D26)
    backlight.switch_to_output()
    backlight.value = True
    
    filename = '/var/local/www/currentsong.txt'
    BUTTON_A_AND_B_PRESSED_CYCLE = 0

    c = 0
    p = 0
    k=0
    ol=0
    ss = 0
    x1 = 20
    x2 = 20
    x3 = 20
    x_mem_info = 10
    x_ip_info = 10
    x_cpu_info = 10    
    time_top = 222
    pause_btn_top = 187
    act_mpd = isServiceActive('mpd')

    client = musicpd.MPDClient()   # create client object
    try:
        client.connect()           # use MPD_HOST/MPD_PORT
    except:
        pass
    playlists_data = client.listplaylists()
    playlists = []
    for playlist in playlists_data:
         playlists.append(playlist['playlist'])
    try:
        CURRENT_PLAYLIST_INDEX = playlists.index(DEFAULT_PLAYLIST)
    except:
        print("No playlist '"+DEFAULT_PLAYLIST+"' found.")
        CURRENT_PLAYLIST_INDEX = 0  
    if act_mpd == True:
        while True:                
             moode_meta = getMoodeMetadata(filename)

             mpd_current = client.currentsong()
             mpd_status = client.status()
                                
             cover = get_cover(moode_meta)

             if COVER_SHOW == 1:
                img.paste(cover.resize((WIDTH,HEIGHT), Image.LANCZOS).filter(ImageFilter.GaussianBlur).convert('RGB'))
                #img.paste(cover.resize((WIDTH,HEIGHT), Image.LANCZOS).convert('RGB'))
             else:
                draw.rectangle((0,0,WIDTH,HEIGHT),fill=DISP_BACKGROUND_COLOR)
                
             if 'state' in mpd_status:                 
                 if (mpd_status['state'] == 'play') and (ICON_SHOW == 1):
                    draw.polygon((108,pause_btn_top,108,pause_btn_top+30,133,pause_btn_top+15),outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                 if (mpd_status['state'] == 'pause') and (ICON_SHOW >= 1):
                     draw.rectangle((105, pause_btn_top, 115,  pause_btn_top+30), outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                     draw.rectangle((125, pause_btn_top, 135, pause_btn_top+30), outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                    
                 if (mpd_status['state'] == 'stop') and (BLANK_SCREEN != 0):
                     if ss < BLANK_SCREEN:
                         ss = ss + 1
                     else:
                         # Turn off the Backlight                            
                         backlight.value = False
                 else:
                     ss = 0
                     # Turn on the Backlight
                     backlight.value = True  
             if (moode_meta['source'] == 'library') or (moode_meta['source'] == 'radio'):                                          
                 if TIMEBAR == 1:
                     if 'elapsed' in  mpd_status:
                         el_time = int(float(mpd_status['elapsed']))
                     if 'duration' in mpd_status:
                         du_time = int(float(mpd_status['duration']))
                         dur_x = int((el_time/du_time)*(WIDTH-10))
                         draw.rectangle((5, time_top, WIDTH-5, time_top + 12), (ImageColor.getrgb(SONG_PROGBAR_COLOR)[0],ImageColor.getrgb(SONG_PROGBAR_COLOR)[1],ImageColor.getrgb(SONG_PROGBAR_COLOR)[2],145))
                         draw.rectangle((5, time_top, dur_x, time_top + 12), fill=SONG_PROGBAR_COLOR)
                                
                     if 'artist' in moode_meta:
                         w1, y1 = draw.textsize(moode_meta['artist'], font_m)
                         x1 = x1-20
                         if x1 < (WIDTH - w1 - 20):
                             x1 = 0
                         if w1 <= WIDTH:
                             x1 = (WIDTH - w1)//2
                         if SHADE != 0:
                             draw.text((x1+SHADE, ARTIST_TOP+SHADE), moode_meta['artist'], font=font_m, fill=FONT_SHADOW_COLOR)
                         draw.text((x1, ARTIST_TOP), moode_meta['artist'], font=font_m, fill=FONT_COLOR)
                                                                     
                     if 'album' in moode_meta:
                         w2, y2 = draw.textsize(moode_meta['album'], font_s)
                         x2 = x2-20
                         if x2 < (WIDTH - w2 - 20):
                             x2 = 0
                         if w2 <= WIDTH:
                             x2 = (WIDTH - w2)//2
                         if SHADE != 0:
                            draw.text((x2+SHADE, ALBUM_TOP+SHADE), moode_meta['album'], font=font_s, fill=FONT_SHADOW_COLOR)
                         draw.text((x2, ALBUM_TOP), moode_meta['album'], font=font_s, fill=FONT_COLOR)
                        
                     if 'title' in moode_meta:
                         w3, y3 = draw.textsize(moode_meta['title'], font_l)
                         x3 = x3-20
                         if x3 < (WIDTH - w3 - 20):
                             x3 = 0
                         if w3 <= WIDTH:
                             x3 = (WIDTH - w3)//2
                         if SHADE != 0:
                             draw.text((x3+SHADE, TITLE_TOP+SHADE), moode_meta['title'], font=font_l, fill=FONT_SHADOW_COLOR)
                         draw.text((x3, TITLE_TOP), moode_meta['title'], font=font_l, fill=FONT_COLOR)

                        #print("Test: ", round((float(mpd_status['elapsed'])/60),2), "/",round((float(mpd_status['duration'])/60),2))

                 else:
                    if 'file' in moode_meta:
                         txt = moode_meta['file'].replace(' ', '\n')
                         w3, h3 = draw.multiline_textsize(txt, font_l, spacing=6)
                         x3 = (WIDTH - w3)//2
                         y3 = (HEIGHT - h3)//2
                         if SHADE != 0:
                             draw.text((x3+SHADE, y3+SHADE), txt, font=font_l, fill=FONT_SHADOW_COLOR)
                         draw.text((x3, y3), txt, font=font_l, fill=FONT_COLOR, spacing=6, align="center")
                   
             #Button Actions
             if  button_U.value == False and button_C.value == True:  # up pressed
                 vol = int(mpd_status['volume'])
                 vol_x = int((vol/100)*(WIDTH - 33))
                 #Volumebar 
                 draw.rectangle((5, VOL_BAR_TOP, WIDTH-34, VOL_BAR_TOP+8), (ImageColor.getrgb(VOL_BAR_COLOR)[0],ImageColor.getrgb(VOL_BAR_COLOR)[1],ImageColor.getrgb(VOL_BAR_COLOR)[2],145))
                 draw.rectangle((5, VOL_BAR_TOP, vol_x, VOL_BAR_TOP+8), fill=VOL_BAR_COLOR)                
                 #Speaker icon
                 draw.polygon((WIDTH-2,VOL_BAR_TOP-11,WIDTH-2,VOL_BAR_TOP+19,WIDTH-12,VOL_BAR_TOP+12,WIDTH-24,VOL_BAR_TOP+12,WIDTH-24,VOL_BAR_TOP-4,WIDTH-12,VOL_BAR_TOP-4),outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                 #Increase volume
                 os.system('/var/www/vol.sh up 5')

             if button_D.value == False and button_C.value == True:  # down pressed
                 vol = int(mpd_status['volume'])
                 vol_x = int((vol/100)*(WIDTH - 33))            
                 #Volumebar 
                 draw.rectangle((5, VOL_BAR_TOP, WIDTH-34, VOL_BAR_TOP+8), (ImageColor.getrgb(VOL_BAR_COLOR)[0],ImageColor.getrgb(VOL_BAR_COLOR)[1],ImageColor.getrgb(VOL_BAR_COLOR)[2],145))
                 draw.rectangle((5, VOL_BAR_TOP, vol_x, VOL_BAR_TOP+8), fill=VOL_BAR_COLOR)
                 #Speaker Icon
                 draw.polygon((WIDTH-2,VOL_BAR_TOP-11,WIDTH-2,VOL_BAR_TOP+19,WIDTH-12,VOL_BAR_TOP+12,WIDTH-24,VOL_BAR_TOP+12,WIDTH-24,VOL_BAR_TOP-4,WIDTH-12,VOL_BAR_TOP-4),outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                 #Reduce volume
                 os.system('/var/www/vol.sh dn 5')

             if button_L.value == False and button_C.value == True:  # left pressed
                 draw.rectangle((10, pause_btn_top, 15, pause_btn_top+30), outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                 draw.polygon((35,pause_btn_top,35,pause_btn_top+30,15,pause_btn_top+15),outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)                
                 os.system('mpc prev')

             if button_R.value == False and button_C.value == True:  # right pressed              
                 draw.polygon((205,pause_btn_top,205,pause_btn_top+30,225,pause_btn_top+15),outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                 draw.rectangle((225, pause_btn_top, 230, pause_btn_top+30), outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                 os.system('mpc next')
                
             if button_A.value == False and button_B.value == True:  # A Button
                 if 'state' in mpd_status:
                     if mpd_status['state'] != 'play':
                         draw.polygon((10,pause_btn_top,10,pause_btn_top+30,35,pause_btn_top+15),outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                     else:
                         draw.rectangle((10, pause_btn_top, 20,  pause_btn_top+30), outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                         draw.rectangle((30, pause_btn_top, 40, pause_btn_top+30), outline=ICON_OUTLINE_COLOR, fill=ICON_FILL_COLOR)
                 os.system('mpc toggle')
            
             if button_B.value == False and button_A.value == True:  # B Button - Load default Playlist.                
                 draw.rectangle((0,0,WIDTH,HEIGHT),fill=DISP_BACKGROUND_COLOR)
                 draw.rectangle((0, 83, WIDTH, 158), (255,255,255,145))
                 
                 w_l_p, y_l_p = draw.textsize('Lade Playlist', font_l)
                 x_l_p = 10             
                 if w_l_p <= WIDTH:
                     w_l_p = (WIDTH - w_l_p)//2
                 if SHADE != 0:
                     draw.text((x_l_p , 88+SHADE), 'Lade Playlist', font=font_l, fill=FONT_SHADOW_COLOR)
                 draw.text((x_l_p , 88), 'Lade Playlist', font=font_l, fill=FONT_COLOR)
                
                 w_p_n, y_p_n = draw.textsize(playlists[CURRENT_PLAYLIST_INDEX], font_l)
                 font = "l"
                 if w_p_n > WIDTH:
                     w_p_n, y_p_n = draw.textsize(playlists[CURRENT_PLAYLIST_INDEX], font_m)
                     font = "m"
                 if w_p_n > WIDTH:
                     w_p_n, y_p_n = draw.textsize(playlists[CURRENT_PLAYLIST_INDEX], font_s)
                     font = "s"
                 
                 x_p_n = 10              
                                               
                 if font == "l":
                     if SHADE != 0: 
                        draw.text((x_p_n, 118+SHADE), playlists[CURRENT_PLAYLIST_INDEX], font=font_l, fill=FONT_SHADOW_COLOR)
                     draw.text((x_p_n, 118), playlists[CURRENT_PLAYLIST_INDEX], font=font_l, fill=FONT_COLOR)
                 
                 if font == "m":
                     if SHADE != 0: 
                        draw.text((x_p_n, 118+SHADE), playlists[CURRENT_PLAYLIST_INDEX], font=font_m, fill=FONT_SHADOW_COLOR)
                     draw.text((x_p_n, 118), playlists[CURRENT_PLAYLIST_INDEX], font=font_m, fill=FONT_COLOR)
                
                 if font == "s":
                     if SHADE != 0: 
                        draw.text((x_p_n, 118+SHADE), playlists[CURRENT_PLAYLIST_INDEX], font=font_s, fill=FONT_SHADOW_COLOR)
                     draw.text((x_p_n, 118), playlists[CURRENT_PLAYLIST_INDEX], font=font_s, fill=FONT_COLOR) 
                 
                 os.system('mpc clear')
                 os.system('mpc load "' + playlists[CURRENT_PLAYLIST_INDEX] + '"')
                 os.system('mpc play')

                 if CURRENT_PLAYLIST_INDEX < len(playlists)-1:
                     CURRENT_PLAYLIST_INDEX = CURRENT_PLAYLIST_INDEX +1
                 else:
                     CURRENT_PLAYLIST_INDEX = 0
                 disp.image(img)
                 time.sleep(1.5)            
                
             if button_B.value == True and button_A.value == True:
                 BUTTON_A_AND_B_PRESSED_CYCLE = 0
                
             if button_B.value == False and button_A.value == False and BUTTON_A_AND_B_PRESSED_CYCLE == 15:
                 draw.rectangle((0,0,WIDTH,HEIGHT),fill=DISP_BACKGROUND_COLOR)
                 draw.text((10, 45), "Herunterfahren", font=font_m, fill=FONT_COLOR)
                 os.system("poweroff")
             
             if button_B.value == False and button_A.value == False and BUTTON_A_AND_B_PRESSED_CYCLE < 15:  # Button A and B pressed > Sysinfo
                 BUTTON_A_AND_B_PRESSED_CYCLE = BUTTON_A_AND_B_PRESSED_CYCLE + 1
                 #Clear background
                 draw.rectangle((0,0,WIDTH,HEIGHT),fill=DISP_BACKGROUND_COLOR)
                 #IP Adress
                 cmd = "hostname -I | cut -d' ' -f1"
                 ip = subprocess.check_output(cmd, shell=True).decode("utf-8")
                 w_ip_info, h_ip_info = draw.textsize(ip, font_m)                 
                 x_ip_info = x_ip_info-10
                 if x_ip_info < (WIDTH - w_ip_info - 10):
                    x_ip_info = 10
                 if w_ip_info <= WIDTH:
                    x_ip_info = 10 
                 draw.text((x_ip_info, 20), 'IP: '+ip, font=font_m, fill=FONT_COLOR)
                 
                 #RAM usage
                 cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
                 mem = subprocess.check_output(cmd, shell=True).decode("utf-8")
                 w_mem_info, h_mem_info = draw.textsize(mem, font_m)                 
                 x_mem_info = x_mem_info-10
                 if x_mem_info < (WIDTH - w_mem_info - 10):
                    x_mem_info = 10
                 if w_mem_info <= WIDTH:
                    x_mem_info = 10                 
                 draw.text((x_mem_info, 45), mem, font=font_m, fill=FONT_COLOR)

                 #CPU temperature
                 cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"
                 cputemp = subprocess.check_output(cmd, shell=True).decode("utf-8")
                 w_cpu_info, h_cpu_info = draw.textsize(cputemp, font_m)                 
                 x_cpu_info = x_cpu_info-10
                 if x_cpu_info < (WIDTH - w_cpu_info - 10):
                    x_cpu_info = 10
                 if w_cpu_info <= WIDTH:
                    x_cpu_info = 10  
                 draw.text((x_cpu_info, 70), cputemp, font=font_m, fill=FONT_COLOR)

                 #disk usage
                 cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
                 disk = subprocess.check_output(cmd, shell=True).decode("utf-8") 
                 draw.text((10, 95), disk, font=font_m, fill=FONT_COLOR)             
                 
                 #Durchlauf
                 countdown = 15 - BUTTON_A_AND_B_PRESSED_CYCLE
                 text = "Shutdown in " + str(countdown)
                 draw.text((10, 145), text, font=font_m, fill=FONT_COLOR)

             disp.image(img)

             if c == 0:
                 im7 = img.save(script_path+'/tmpimg.png')
                 c += 1


             time.sleep(0.3)
             ol += 1
        client.disconnect()
        
    else:
        draw.rectangle((0,0,240,240), fill=(0,0,0))
        txt = 'MPD not Active!\nEnsure MPD is running\nThen restart script'
        mlw, mlh = draw.multiline_textsize(txt, font=font_m, spacing=4)
        draw.multiline_text(((WIDTH-mlw)//2, 20), txt, fill=(255,255,255), font=font_m, spacing=4, align="center")
        disp.display(img)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:        
        if (os.path.exists(script_path+'/tmpimg.png')):
            os.remove(script_path+'/tmpimg.png')
        disp.fill(0)
        backlight = DigitalInOut(board.D26)
        backlight.switch_to_output()
        backlight.value = False
        pass
