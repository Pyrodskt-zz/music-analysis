from pytube import YouTube, Playlist
import librosa
import numpy as np
import pandas as pd
import json
import os

import warnings


def read_songs_list():
    df = pd.read_csv(r'./data.csv')
    cols = df.columns
    df = df.rename(columns={cols[0]: 'time', cols[1]: 'url' })
    urls = df.url

    return urls



def get_playlists():
    urls = read_songs_list()
    playlists = [u for u in urls if 'playlist' in u]
    urls = [i for i in urls if 'playlist' not in i]

    return urls, playlists


def split_playlists(playlists):
    urls = []
    for p in playlists:
        play = Playlist(p)
        for u in play.video_urls:
            urls.append(u)
    
    return urls


def rename(path):
    base, ext = os.path.split(path)
    filename, ext2= ext.split('.')
    newfile = base + "/" + filename + '.mp3'
    os.rename(path, newfile)


def download(url):
    l = YouTube(url).length
    if l < 700:
        yt = YouTube(url).streams.first().download('videos/')
        rename(yt)
        return True
    return False

def listFiles():
    ls = [f for f in os.listdir('./videos/') if os.path.isfile(os.path.join('./videos/', f))]
    return ls

def get_music_data(path, url, ind):
    y, sr = librosa.load(path)
    onset_env = librosa.onset.onset_detect(y=y, sr=sr, units='time')
    onset_frames = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=2048)
    times = librosa.times_like(onset_env, sr=sr)
    frames = len(librosa.frames_to_time(beats, sr=sr))
    time = librosa.get_duration(y)
    D = np.abs(librosa.stft(y))

    powtimes = librosa.times_like(D)

    tmp = librosa.amplitude_to_db(D, ref=1.0, top_db=120)
    pow_mini = 100
    pow_maxi = 0
    pow_std = 0
    stds = []
    for i in tmp:
        if i.min() < pow_mini:
            pow_mini = i.min()
        if i.max() > pow_maxi:
            pow_maxi = i.max()
        stds.append(i.std())
    pow_std = sum(stds) / len(stds)
    pow_std
    y_harm, y_perc = librosa.effects.hpss(y)
    y_harm_min = y_harm.min()
    y_harm_max = y_harm.max()
    y_harm_std = y_harm.std()
    y_perc_min = y_perc.min()
    y_perc_max = y_perc.max()
    y_perc_std = y_perc.std()
    title = path.split('/')[1]
    data = {'url': url,'path': path, 'time': float(time),'PercussionMoy': float(y_perc_std),'PercussionMax': float(y_perc_max),'PercussionMin': float(y_perc_min),'HarmonicMin': float(y_harm_min), 'HarmonicMoy': float(y_harm_std),'HarmonicMax': float(y_harm_max),'AmplitudeMin': float(pow_mini),'AmplitudeMoy': float(pow_std), 'AmplitudeMax': float(pow_maxi), 'Ratio': float(frames/time)}
    return data


def delete_file(path):
    os.remove(path)


def write_data_to_json(newdata):
    data = []
    with open('data.json') as _file:
        data = json.load(_file)
    
    data['data'].append(newdata)
    with open('data.json', 'w') as fp:
        json.dump(data, fp, indent=4, separators=(',',':'))


urls, playlists = get_playlists()
p_urls = split_playlists(playlists)

f_urls = urls + p_urls
print(len(f_urls), "songs to load in db")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


for ind, i in enumerate(f_urls):
    try:
        print('file',ind, ' on ',  len(f_urls))
        download(i)
        path = os.path.join('./videos/', listFiles()[0])
        data = get_music_data(path, i, ind)
        write_data_to_json(data)
        delete_file(path)
        
    except VideoUnavailable: 
        print("error in url")
        






