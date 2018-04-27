mkdir tmp
./lum.py
ffmpeg -start_number 1 -i tmp/Frame\ %d.jpg -vcodec mpeg4 out.avi
rm -r tmp
