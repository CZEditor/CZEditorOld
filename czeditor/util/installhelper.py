import os
import shutil
import subprocess
import sys
import zipfile

# Explicit import due to Nuitka's way of handling imports
from sys import exit

TIMEOUT = 15


def getPortAudioDLL(platform: str, compiled: bool):
    if platform == "win":
        if compiled:
            try:
                # Download the dll via powershell quietly
                res = subprocess.run(
                    ["powershell", "-Command", "Invoke-WebRequest",
                     "-OutFile", "libportaudio.dll", "-Uri",
                     "https://github.com/spatialaudio/portaudio-binaries/blob/master/libportaudio64bit.dll?raw=true"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=TIMEOUT)
                failed = res.returncode != 0
            except:
                failed = True
        if not compiled or failed:
            # If not compiled we have shell access
            # so we will just suggest the user to download it
            print("Missing PortAudio, consider getting it here:")
            print("https://github.com/spatialaudio/portaudio-binaries")
            exit(1)
    elif platform == "mac":
        hasBrew = shutil.which("brew") is not None
        if compiled:
            try:
                if hasBrew:
                    print("Running: brew install portaudio...")
                    res = subprocess.run(["brew", "install", "portaudio"],
                                         check=True, shell=True)
                else:
                    # Fallback to downloading the dylib via curl
                    res = subprocess.run(["curl", "-O", "-L",
                                          "https://github.com/spatialaudio/portaudio-binaries/blob/master/libportaudio.dylib?raw=true"],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=TIMEOUT)
                failed = res.returncode != 0
            except:
                failed = True
        if not compiled or failed:
            if hasBrew:
                print("Missing PortAudio, consider getting it via brew:")
                print("brew install portaudio")
            else:
                print("Missing PortAudio, consider getting it here:")
                print("https://github.com/spatialaudio/portaudio-binaries")
            exit(1)
    elif platform == "linux":
        hasApt = shutil.which("apt") is not None
        # We assume that a linux user runs the program via shell anyway
        if hasApt:
            print("Running: sudo apt install libportaudio2...")
            try:
                res = subprocess.run(
                    ["sudo", "apt", "install", "libportaudio2"])
                failed = res.returncode != 0
            except:
                failed = True
        if not hasApt or failed:
            print("Missing PortAudio, consider getting it via your package manager")
            exit(1)
    else:
        print("Missing PortAudio, consider getting it here:")
        print("http://www.portaudio.com/")
        exit(1)


def installFFmpeg(platform: str, compiled: bool):
    if platform == "win":
        if compiled:
            try:
                # Download the exe via powershell quietly
                res = subprocess.run(
                    ["powershell", "-Command", "Invoke-WebRequest",
                     "-OutFile", "ffmpeg.zip", "-Uri",
                     "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=TIMEOUT)
                failed = res.returncode != 0
                with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
                    zip_ref.extract(
                        "ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe")
                    zip_ref.extract(
                        "ffmpeg-master-latest-win64-gpl/bin/ffprobe.exe")
                os.remove("ffmpeg.zip")
            except:
                failed = True
        if not compiled or failed:
            # If not compiled we have shell access
            # so we will just suggest the user to download it
            print("Missing ffmpeg, consider getting it here:")
            print("https://ffmpeg.org/download.html")
            exit(1)
    elif platform == "mac":
        if compiled:
            hasBrew = shutil.which("brew") is not None
            if hasBrew:
                try:
                    res = subprocess.run(["brew", "install", "ffmpeg"])
                    failed = res.returncode != 0
                except:
                    failed = True
            else:
                try:
                    # Download via curl quietly
                    res = subprocess.run(
                        ["curl", "-o", "ffmpeg.zip" "-L",
                         "https://evermeet.cx/ffmpeg/getrelease/zip"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=TIMEOUT)
                    failed = res.returncode != 0
                    with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
                        zip_ref.extractall()
                    os.remove("ffmpeg.zip")
                except:
                    failed = True
        if not compiled or failed:
            if hasBrew:
                print("Missing ffmpeg, consider getting it via brew:")
                print("brew install ffmpeg")
            else:
                print("Missing ffmpeg, consider getting it here:")
                print("https://evermeet.cx/ffmpeg/")
            exit(1)
    elif platform == "linux":
        hasApt = shutil.which("apt") is not None
        if hasApt:
            print("Running: sudo apt install ffmpeg")
            try:
                res = subprocess.run(["sudo", "apt", "install", "ffmpeg"])
                failed = res.returncode != 0
            except:
                failed = True
        if not hasApt or failed:
            print("Missing ffmpeg, consider getting it via your package manager")
            exit(1)
    else:
        print("Missing ffmpeg, consider getting it here:")
        print("https://ffmpeg.org/download.html")
        exit(1)


def checkAndInstall():
    # detect if we're running from a frozen executable
    compiled = "__compiled__" in globals() or getattr(sys, "frozen", False)

    # detect platform
    if sys.platform.startswith("win") or sys.platform.startswith("cygwin") or sys.platform.startswith("msys"):
        platform = "win"
    elif sys.platform.startswith("darwin"):
        platform = "mac"
    elif sys.platform.startswith("linux"):
        platform = "linux"
    else:
        platform = "other"

    # check if we are missing the required DLLs for sounddevice
    try:
        import sounddevice
    except OSError:
        getPortAudioDLL(platform, compiled)
        exit(1)

    # check if we have ffmpeg installed
    try:
        import moviepy.video.VideoClip
    except RuntimeError:
        installFFmpeg(platform, compiled)
        exit(1)
