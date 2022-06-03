from pytube import YouTube


yt = YouTube("https://music.youtube.com/watch?v=73S2Pdz2S0U&feature=share").streams.first().download('videos/')
l = YouTube("https://music.youtube.com/watch?v=73S2Pdz2S0U&feature=share").length
print(yt, l)
