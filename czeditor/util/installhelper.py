import os
import requests
import shutil
import subprocess
import sys
import zipfile

# Explicit import due to Nuitka's way of handling implicit imports
from sys import exit

TIMEOUT = 180

PORTAUDIO_WIN_URL = "https://github.com/spatialaudio/portaudio-binaries/blob/master/libportaudio64bit.dll?raw=true"
PORTAUDIO_WIN_PATH = "libportaudio.dll"
PORTAUDIO_MAC_URL = "https://github.com/spatialaudio/portaudio-binaries/blob/master/libportaudio.dylib?raw=true"
PORTAUDIO_MAC_PATH = "libportaudio.dylib"
FFMPEG_WIN_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_WIN_PATH = "ffmpeg.zip"
FFMPEG_MAC_URL = "https://evermeet.cx/ffmpeg/getrelease/zip"
FFMPEG_MAC_PATH = FFMPEG_WIN_PATH

MISSING_MSG = "Missing {lib}, consider getting it here:"
MISSING_MSG_BREW = "Missing {lib}, consider getting it via brew:"
MISSING_MSG_LINUX = "Missing {lib}, consider getting it via your package manager:"
FAIL_MSG = "Failed to download {lib}, consider getting it here:"
FAIL_MSG_BREW = "Failed to install {lib}, consider getting it via brew manually:"
FAIL_MSG_LINUX = "Failed to install {lib}, compile it yourself :) or use a package manager"

PORTAUDIO_MISSING_MSG = MISSING_MSG.format(lib="PortAudio")
PORTAUDIO_MISSING_MSG_BREW = MISSING_MSG_BREW.format(lib="PortAudio")
PORTAUDIO_MISSING_MSG_LINUX = MISSING_MSG_LINUX.format(lib="PortAudio")
PORTAUDIO_FAIL_MSG = FAIL_MSG.format(lib="PortAudio")
PORTAUDIO_FAIL_MSG_BREW = FAIL_MSG_BREW.format(lib="PortAudio")
PORTAUDIO_FAIL_MSG_LINUX = FAIL_MSG_LINUX.format(lib="PortAudio")
PORTAUDIO_BREW_CMD = ["brew", "install", "portaudio"]
PORTAUDIO_BREW_CMD_TO_PRINT = f"`{' '.join(PORTAUDIO_BREW_CMD)}`"
PORTAUDIO_APT_CMD = ["sudo", "apt", "install", "libportaudio2"]
PORTAUDIO_APT_CMD_TO_PRINT = f"`{' '.join(PORTAUDIO_APT_CMD)}`"
PORTUAUDIO_WEB_URL = "http://www.portaudio.com/"

FFMPEG_MISSING_MSG = MISSING_MSG.format(lib="FFmpeg")
FFMPEG_MISSING_MSG_BREW = MISSING_MSG_BREW.format(lib="FFmpeg")
FFMPEG_MISSING_MSG_LINUX = MISSING_MSG_LINUX.format(lib="FFmpeg")
FFMPEG_FAIL_MSG = FAIL_MSG.format(lib="FFmpeg")
FFMPEG_FAIL_MSG_BREW = FAIL_MSG_BREW.format(lib="FFmpeg")
FFMPEG_FAIL_MSG_LINUX = FAIL_MSG_LINUX.format(lib="FFmpeg")
FFMPEG_BREW_CMD = ["brew", "install", "ffmpeg"]
FFMPEG_BREW_CMD_TO_PRINT = f"`{' '.join(FFMPEG_BREW_CMD)}`"
FFMPEG_APT_CMD = ["sudo", "apt", "install", "ffmpeg"]
FFMPEG_APT_CMD_TO_PRINT = f"`{' '.join(FFMPEG_APT_CMD)}`"
FFMPEG_WEB_URL = "https://ffmpeg.org/download.html"

BREW_INSTALL_PROMPT = "Attempting brew install, root privileges may be required:"
APT_INSTALL_PROMPT = "Attempting apt install, may need too authenticate:"


def requestsGetFile(url: str, path: str) -> None:
    _r = requests.get(url=url, allow_redirects=True,
                      timeout=TIMEOUT, stream=True)
    _r.raise_for_status()
    with open(path, "wb") as _f:
        for chunk in _r.iter_content(chunk_size=None):
            if chunk:
                _f.write(chunk)
                _f.flush()


def getPortAudioDLL(platform: str, silent: bool) -> None:
    failed = False
    if platform == "win":
        if silent:
            try:
                # Download the dll quietly
                requestsGetFile(PORTAUDIO_WIN_URL, PORTAUDIO_WIN_PATH)
            except requests.exceptions.RequestException:
                os.remove(PORTAUDIO_WIN_PATH)
                failed = True
        else:
            # Prompt the user to download the dll manually
            print(PORTAUDIO_MISSING_MSG)
            print(PORTAUDIO_WIN_URL)
            exit(1)
        if failed:
            print(PORTAUDIO_FAIL_MSG)
            print(PORTAUDIO_WIN_URL)
            exit(1)
    elif platform == "mac":
        hasBrew = shutil.which("brew") is not None
        if silent:
            if hasBrew:
                print(BREW_INSTALL_PROMPT)
                print(PORTAUDIO_BREW_CMD_TO_PRINT)
                try:
                    subprocess.run(PORTAUDIO_BREW_CMD, check=True)
                except subprocess.CalledProcessError:
                    failed = True
            if not hasBrew or failed:
                failed = False
                # Fallback to downloading the dylib quietly
                try:
                    requestsGetFile(PORTAUDIO_MAC_URL, PORTAUDIO_MAC_PATH)
                except requests.exceptions.RequestException:
                    os.remove(PORTAUDIO_MAC_PATH)
                    failed = True
        else:
            if hasBrew:
                print(PORTAUDIO_MISSING_MSG_BREW)
                print(PORTAUDIO_BREW_CMD_TO_PRINT)
            else:
                print(PORTAUDIO_MISSING_MSG)
                print(PORTAUDIO_MAC_URL)
            exit(1)
        if failed:
            if hasBrew:
                print(PORTAUDIO_FAIL_MSG_BREW)
                print(PORTAUDIO_BREW_CMD_TO_PRINT)
            else:
                print(PORTAUDIO_FAIL_MSG)
                print(PORTAUDIO_MAC_URL)
            exit(1)
    elif platform == "linux":
        hasApt = shutil.which("apt") is not None
        # We assume that a linux user runs the program via shell anyway
        if hasApt:
            print(APT_INSTALL_PROMPT)
            print(PORTAUDIO_APT_CMD_TO_PRINT)
            try:
                subprocess.run(PORTAUDIO_APT_CMD, check=True)
            except subprocess.CalledProcessError:
                failed = True
        else:
            print(PORTAUDIO_MISSING_MSG_LINUX)
            exit(1)
        if failed:
            print(PORTAUDIO_FAIL_MSG_LINUX)
            exit(1)
    else:
        print(PORTAUDIO_MISSING_MSG)
        print(PORTUAUDIO_WEB_URL)
        exit(1)


def getFFmpeg(platform: str, silent: bool) -> None:
    failed = False
    if platform == "win":
        if silent:
            try:
                # Download quietly
                requestsGetFile(FFMPEG_WIN_URL, FFMPEG_WIN_PATH)
                with zipfile.ZipFile(FFMPEG_WIN_PATH, "r") as zip_ref:
                    zip_ref.extract(
                        "ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe")
                    zip_ref.extract(
                        "ffmpeg-master-latest-win64-gpl/bin/ffprobe.exe")
            except requests.exceptions.RequestException:
                failed = True
            except zipfile.BadZipFile:
                failed = True
            finally:
                os.remove(FFMPEG_WIN_PATH)
        else:
            # Suggest a manual download
            print(FFMPEG_MISSING_MSG)
            print(FFMPEG_WIN_URL)
            exit(1)
        if failed:
            print(FFMPEG_FAIL_MSG)
            print(FFMPEG_WIN_URL)
            exit(1)
    elif platform == "mac":
        hasBrew = shutil.which("brew") is not None
        if silent:
            if hasBrew:
                print(BREW_INSTALL_PROMPT)
                print(FFMPEG_BREW_CMD_TO_PRINT)
                try:
                    subprocess.run(FFMPEG_BREW_CMD, check=True)
                except subprocess.CalledProcessError:
                    failed = True
            if not hasBrew or failed:
                failed = False
                try:
                    # Download manualy quietly
                    requestsGetFile(FFMPEG_MAC_URL, FFMPEG_MAC_PATH)
                    with zipfile.ZipFile(FFMPEG_MAC_PATH, "r") as zip_ref:
                        zip_ref.extractall()
                except requests.exceptions.RequestException:
                    failed = True
                except zipfile.BadZipFile:
                    failed = True
                finally:
                    os.remove(FFMPEG_MAC_PATH)
        else:
            if hasBrew:
                print(FFMPEG_MISSING_MSG_BREW)
                print(FFMPEG_BREW_CMD_TO_PRINT)
            else:
                print(FFMPEG_MISSING_MSG)
                print(FFMPEG_MAC_URL)
            exit(1)
        if failed:
            if hasBrew:
                print(FFMPEG_FAIL_MSG_BREW)
                print(FFMPEG_BREW_CMD_TO_PRINT)
            else:
                print(FFMPEG_FAIL_MSG)
                print(FFMPEG_MAC_URL)
            exit(1)
    elif platform == "linux":
        hasApt = shutil.which("apt") is not None
        if hasApt:
            print(APT_INSTALL_PROMPT)
            print(FFMPEG_APT_CMD_TO_PRINT)
            try:
                subprocess.run(FFMPEG_APT_CMD, check=True)
            except subprocess.CalledProcessError:
                failed = True
        else:
            print(FFMPEG_MISSING_MSG_LINUX)
            exit(1)
        if failed:
            print(FFMPEG_FAIL_MSG_LINUX)
            exit(1)
    else:
        print(FFMPEG_MISSING_MSG)
        print(FFMPEG_WEB_URL)
        exit(1)


def checkAndInstall() -> bool:
    # detect if we're running from a frozen executable
    runSilently = "__compiled__" in globals() or getattr(sys, "frozen", False)

    if not runSilently:
        # Check `pip list` for package `czeditor` to see if
        # running from an installed package. If so, we install the
        # dependencies silently
        try:
            res = subprocess.run(
                ["pip", "list"], capture_output=True, check=True, text=True)
        except:  # Don't crash if pip is not installed or something
            pass
        else:
            if "czeditor" in res.stdout:
                runSilently = True

    # detect platform
    if sys.platform.startswith("win") or sys.platform.startswith("cygwin") or sys.platform.startswith("msys"):
        platform = "win"
    elif sys.platform.startswith("darwin"):
        platform = "mac"
    elif sys.platform.startswith("linux"):
        platform = "linux"
    else:
        platform = "other"

    ret = False
    # check if we are missing the required DLLs for sounddevice
    try:
        import sounddevice
    except OSError:
        getPortAudioDLL(platform, runSilently)
        ret = True

    # check if we have ffmpeg installed
    try:
        import moviepy.video.VideoClip
    except RuntimeError:
        getFFmpeg(platform, runSilently)
        ret = True

    return ret
