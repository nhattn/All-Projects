#!/bin/bash

IDS=("dN8Pj1WzX8s" "0-eFjYY3FlY" "K8gxoQWHcUg" "zOMSbq5bD-w")
NAMES=("Thuong-Em" "Tong-Phu" "Hen-Em-Kiep-Sau" "Con-Tim-Khong-Doi-Thay")

if [ ! -d "/tmp/youtu" ]; then
    mkdir -p /tmp/youtu
fi

rm -rf /tmp/youtu/*
cd /tmp/youtu/

# https://stackoverflow.com/a/6723516
for i in "${!IDS[@]}"; do 
    echo "$i -> ${a[$i]} + ${b[$i]}"
    ~/ytdl -f 251 "https://www.youtube.com/watch?v=${IDS[$i]}" -o "${NAMES[$i]}.%(ext)s"
done

FILES=($(ls . | grep *.webm))

#https://stackoverflow.com/a/19954510
timestamp=$(date +%s)

echo "[playlist]" > "youtu${timestamp}.pls"
echo "X-GNOME-Title=Youtobe Playlists $(date +%F %T)" >> "youtu${timestamp}.pls"
echo "NumberOfEntries=${#FILES[@]}" >> "youtu${timestamp}.pls"

i=1
# https://stackoverflow.com/a/67069688
for FILE in "${FILES[@]}"; do
    echo -e "Processing file '$FILE'";
    ffmpeg -i "${FILE}" -vn -ab 320k -ar 44100 -y "${FILE%.webm}.mp3";
    echo "File$i=${FILE%.webm}.mp3" >> "youtu${timestamp}.pls"
    i=$((i+1))
done;

mv *.mp3 ~/Music
mv "youtu${timestamp}.pls" ~/Music
rm -rf *.webm

exit
