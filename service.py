import json
import xbmcgui
import os
import xbmc
import xbmcaddon
import subprocess
import re
import platform
import xbmcvfs


ADDON = xbmcaddon.Addon(id="service.telerising")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temp = os.path.join(datapath, "temp")
addonpath = xbmc.translatePath(ADDON.getAddonInfo('path'))
binpath = os.path.join(addonpath, "bin")
runpath = os.path.join(datapath, "bin")
mute_notify = ADDON.getSetting('hide-osd-messages')
logfile = os.path.join(runpath, 'log.txt')
oldlogfile = os.path.join(runpath, 'oldlog.txt')

## Read Zattoo Basic Settings
provider = ADDON.getSetting('provider')
username = ADDON.getSetting('username')
password = ADDON.getSetting('password')
youth_protection_pin = ADDON.getSetting('youth_protection_pin')
ondemand = ADDON.getSetting('ondemand')

## Read Zattoo Advanced Settings
ssl_verify = ADDON.getSetting('ssl_verify')
server = ADDON.getSetting('server')
port = ADDON.getSetting('port')
network_device = ADDON.getSetting('network_device')


## Read Zattoo Debug Settings
restart_on_failure = ADDON.getSetting('restart_on_failure')

## Read Default Client Settings
ffmpeg_path = ADDON.getSetting('ffmpeg_path')
quality = ADDON.getSetting('quality')
audio_profile = ADDON.getSetting('audio_profile')
audio2 = ADDON.getSetting('audio2')
dolby = ADDON.getSetting('dolby')
ignore_maxrate = ADDON.getSetting('ignore_maxrate')
loglevel = ADDON.getSetting('loglevel')

# Translate Video Settings to Bandwidth

bandwidth = dict({'432p25': '1500',
                  '576p50': '2999',
                  '720p25': '3000',
                  '720p50': '5000',
                  '1080p25': '4999',
                  '1080p50': '8000'})
bw = bandwidth[quality]


## Translate SSL_VERIFY
if ssl_verify == 'true':
    ssl_mode = "1"
elif ssl_verify == 'false':
    ssl_mode = "0"

OSD = xbmcgui.Dialog()
machine = platform.machine()

## Make OSD Notify Messages
def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    if mute_notify == "false":
        OSD.notification(title, message, icon)

## Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[%s %s] %s' % (addon_name, addon_version, str(message)), loglevel)

def use_settings():
    ## read and write userfile.json
    filename = os.path.join(runpath, "userfile.json")
    with open(filename, 'r') as f:
        data = json.load(f)
        data['provider'] = provider
        data['login'] = username
        data['password'] = password
        data['youth_protection_pin'] = youth_protection_pin
        data['server'] = server
        data['ssl_mode'] = ssl_mode
        data['port'] = port
        data['interface'] = network_device
        data['ondemand'] = ondemand

        data['ffmpeg_lib'] = ffmpeg_path
        data['bw'] = bw
        data['audio2'] = audio2
        data['dolby'] = dolby
        data['profile'] = audio_profile
        data['ignore_maxrate'] = ignore_maxrate
        data['loglevel'] = loglevel

    ## create randomly named temporary file to avoid interference with other thread/asynchronous request
    tempfile = os.path.join(datapath, 'filename')
    with open(tempfile, 'w') as f:
        json.dump(data, f, indent=4)
    ## rename temporary file replacing old file
    os.rename(tempfile, filename)

def move_log():
    ##Move Logfile to OLDLOGFILE before API Starts
    if os.path.isfile(logfile):
        os.rename(logfile, oldlogfile)

def machine_type():
    ##Check under Whitch Machine Type this Addon is running
    if machine == 'x86_64':
        log("Machine is " + machine, xbmc.LOGNOTICE)
        return True
    elif machine == 'armv7l':
        log("Machine is " + machine, xbmc.LOGNOTICE)
        return True
    elif machine == 'armv8l':
        log("Machine is " + machine, xbmc.LOGNOTICE)
        return True
    else:
        log(machine + " is currently not supported", xbmc.LOGERROR)
        notify(addon_name, "No vaild Machine found", icon=xbmcgui.NOTIFICATION_ERROR)
        return False

def install_files():
    ##Check under Whitch Machine Type this Addon is running and copy needed files
    if machine == 'x86_64':
        src = os.path.join(binpath, "telerising_x86")
        dest = os.path.join(runpath, "telerising_x86")
        xbmcvfs.copy(src, dest)
    elif machine == 'armv7l':
        src = os.path.join(binpath, "telerising_arm32")
        dest = os.path.join(runpath, "telerising_arm32")
        xbmcvfs.copy(src, dest)
    elif machine == 'armv8l':
        src = os.path.join(binpath, "telerising_arm64")
        dest = os.path.join(runpath, "telerising_arm64")
        xbmcvfs.copy(src, dest)
    if machine_type() == True:
        userfile_src = os.path.join(binpath, "userfile.json")
        userfile_dest = os.path.join(runpath, "userfile.json")
        xbmcvfs.copy(userfile_src, userfile_dest)

def stop_telerising():
    ## First we need to Kill the "sh" Pid to Prevent Zombie Pids
    subprocess.Popen(['ps ax | grep "&& ./telerising_" | cut -c1-6 | sed "s/^/kill -9 /" | bash'], shell=True)
    ##Now we can Kill all *telerising_* Pid
    xbmc.sleep(1000)
    subprocess.Popen(['ps ax | grep "telerising_" | cut -c1-6 | sed "s/^/kill -9 /" | bash'], shell=True)

def run_telerising():
    rights = "chmod 777 -R " + runpath
    subprocess.Popen(rights, shell=True)
    if machine == 'x86_64':
        command = "cd " + runpath + " && sleep 1 && ./telerising_x86"
        subprocess.Popen(command, shell=True)
        log(addonpath, xbmc.LOGNOTICE)
    elif machine == 'armv7l':
        command = "cd " + runpath + " && sleep 1 && ./telerising_arm32"
        subprocess.Popen(command, shell=True)
    elif machine == 'armv8l':
        command = "cd " + runpath + " && sleep 1 && ./telerising_arm64"
        subprocess.Popen(command, shell=True)

    # Check Running State in logfile
    # wait for logfile creation max 30 seconds.
    retries = 30
    while retries > 0:
        try:
            f = open(logfile, 'r')
            xbmc.sleep(8000)
            file_contents = f.read()
            break
        except IOError as e:
            xbmc.sleep(1000)
            retries -= 1
    if retries == 0:
        notify(addon_name, "Could not open Logfile")
        log("Could not open Logfile", xbmc.LOGERROR)

    started_string = "API STARTED"
    login_success = "LOGIN OK"
    login_failed = "please re-check login data"
    interface_failed = "Custom interface can't be used"
    provider_failed = "Can't connect to"
    account_failed = "No Swiss IP address detected"
    binary_failed = "ERROR"
    webservice_failed = "UNABLE TO LOGIN TO WEBSERVICE"
    session_failed = "UNABLE TO CREATE SESSION FILE"
    interface_failed2 = "Broadcast interface can't be found"
    api_failed ="Please recheck your IP/domain/port"

    started_is = re.search(started_string, file_contents)
    if not started_is:
        retries = 30
        while retries > 0:
            f.close
            f = open(logfile, 'r')
            file_contents = f.read()

            ## Check if login is success
            if re.search(started_string, login_success):
                log("Login to Provider " + provider + ' OK, waiting for API to startup....', xbmc.LOGNOTICE)

            ## Check if API is Started
            if re.search(started_string, file_contents):
                notify(addon_name, "API Started")
                log("API Started", xbmc.LOGNOTICE)
                retries -= 30

            ##Check if Wrong Username / Password
            if re.search(login_failed, file_contents):
                notify(addon_name, "please re-check login data", icon=xbmcgui.NOTIFICATION_ERROR)
                log("please re-check login data", xbmc.LOGERROR)
                retries -= 30

            ##Check if Interface cant be used
            if re.search(interface_failed, file_contents):
                notify(addon_name, "Custom interface can't be used (unknown)", icon=xbmcgui.NOTIFICATION_ERROR)
                log("Custom interface can't be used", xbmc.LOGERROR)
                retries -= 30

            ##Check if Interface(2) cant be used
            if re.search(interface_failed2, file_contents):
                notify(addon_name, "Broadcast interface can't be found!", icon=xbmcgui.NOTIFICATION_ERROR)
                log("Broadcast interface can't be found!", xbmc.LOGERROR)
                retries -= 30

            ##Check if Provider cant be used
            if re.search(provider_failed, file_contents):
                notify(addon_name, "Can't connect to Provider, Please Check Provider Settings and or Internet Connection", icon=xbmcgui.NOTIFICATION_ERROR)
                log("Can't connect to Provider, Please Check Provider Settings and or Internet Connection" ,xbmc.LOGERROR)
                retries -= 30

            ##Check if CH Account cant be used
            if re.search(account_failed, file_contents):
                notify(addon_name, "No Swiss IP address detected, Zattoo services can't be used", icon=xbmcgui.NOTIFICATION_ERROR)
                log("No Swiss IP address detected, Zattoo services can't be used", xbmc.LOGERROR)
                retries -= 30

            ##Check Webservice
            if re.search(webservice_failed, file_contents):
                notify(addon_name, "UNABLE TO LOGIN TO WEBSERVICE", icon=xbmcgui.NOTIFICATION_ERROR)
                log("UNABLE TO LOGIN TO WEBSERVICE", xbmc.LOGERROR)
                retries -= 30

            ##Check Session
            if re.search(session_failed, file_contents):
                notify(addon_name, "UNABLE TO CREATE SESSION FILE", icon=xbmcgui.NOTIFICATION_ERROR)
                log("UNABLE TO CREATE SESSION FILE", xbmc.LOGERROR)
                retries -= 30

            ##Check API
            if re.search(api_failed, file_contents):
                notify(addon_name, "Please recheck your IP/domain/port configuration", icon=xbmcgui.NOTIFICATION_ERROR)
                log("Please recheck your IP/domain/port configuration", xbmc.LOGERROR)
                retries -= 30

            xbmc.sleep(5000)
            retries -= 1

    ##Check if any Error exist
    if re.search(binary_failed, file_contents):
        notify(addon_name, "ERROR, Please check Logfile for Details", icon=xbmcgui.NOTIFICATION_ERROR)
        log("Please check Telerising Logfile for Details", xbmc.LOGERROR)

    f.close

def startup():
    machine_type()
    if  machine_type() == True:
        # deal with bug that happens if the datapath and/or temp doesn't exist
        if not os.path.exists(temp):
            os.makedirs(temp)
        if not os.path.exists(runpath):
            os.makedirs(runpath)
        install_files()
        use_settings()
        move_log()
        stop_telerising()
        xbmc.sleep(2000)
        notify(addon_name, "Starting API....")
        log("Starting API....", xbmc.LOGNOTICE)
        run_telerising()
    elif  machine_type() == False:
        exit()

## Read Logfile and check Runningstate, restart if restart_on_failure == 1
def check_runningstate():
    retries = 30
    while retries > 0:
        try:
            f = open(logfile, 'r')
            xbmc.sleep(8000)
            file_contents = f.read()
            break
        except IOError as e:
            xbmc.sleep(1000)
            retries -= 1
    if retries == 0:
        notify(addon_name, "Could not open Logfile")
        log("Could not open Logfile", xbmc.LOGERROR)
    binary_failed = "ERROR"
    started_string = "API STARTED"

    if re.search(binary_failed, file_contents):
        notify(addon_name, "ERROR, API STOPPED Please check Logfile for Details", icon=xbmcgui.NOTIFICATION_ERROR)
        log("API STOPPED, Please check Telerising Logfile for Details", xbmc.LOGERROR)
        stop_telerising()
        xbmc.sleep(5000)
        notify(addon_name, "Restarting API after Error....")
        log("Restarting API after Error....", xbmc.LOGNOTICE)
        f.close
        startup()

    api_started = re.search(started_string, file_contents)
    if api_started:
        log("API-CHECK API seems to be running... OK", xbmc.LOGNOTICE)

    f.close


if __name__ == '__main__':
    monitor = xbmc.Monitor()

    startup()

    # Wait for Binary to Stop
    while not monitor.abortRequested():
        while not monitor.waitForAbort(10):
            if restart_on_failure == 'true':
                check_runningstate()
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort(10):
            # Abort was requested while waiting. We should exit
            notify(addon_name, "API Stopped")
            log('API Stopped', xbmc.LOGNOTICE)
            stop_telerising()
            break


