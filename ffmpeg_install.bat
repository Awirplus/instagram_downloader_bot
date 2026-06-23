@echo off
echo Installing ffmpeg...
curl -L https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip -o ffmpeg.zip
tar -xf ffmpeg.zip
move ffmpeg-* ffmpeg
setx PATH "%CD%\ffmpeg\bin;%PATH%"
echo ffmpeg installed successfully!
pause