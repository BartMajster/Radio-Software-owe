import vlc
import os
class RadioPlayer:
    def __init__(self):
        self._setup_vlc_path()
        self.instance = vlc.Instance('--no-video')
        self.player = self.instance.media_player_new()
    def _setup_vlc_path(self):
        if os.name == 'nt':
            try:
                os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
            except Exception:
                pass
    def play(self, stream_url):
        self.player.stop()
        media = self.instance.media_new(stream_url)
        self.player.set_media(media)
        self.player.play()
    def stop(self):
        self.player.stop()
    def set_volume(self, value):
        self.player.audio_set_volume(value)
    def get_now_playing(self):
        if not self.player.is_playing():
            return None
        media = self.player.get_media()
        if media:
            return media.get_meta(vlc.Meta.NowPlaying)
        return None