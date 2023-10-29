import time, vlc
import os
import subprocess

# defining the method to play video
def vlc_video(src):
    # creating an instance of vlc
    vlc_obj = vlc.Instance()

    # creating a media player
    vlcplayer = vlc_obj.media_player_new()

    # creating a media
    vlcmedia = vlc_obj.media_new(src)

    # setting media to the player
    vlcplayer.set_media(vlcmedia)

    # playing the video
    vlcplayer.play()


    # waiting time
    time.sleep(0.5)

    # getting the duration of the video
    video_duration = vlcplayer.get_length()

    # printing the duration of the video
    print("Duration : " + str(video_duration))

os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
# creating the vlc media player object
vlc_video("")
time.sleep(60)
