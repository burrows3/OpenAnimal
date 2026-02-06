Shorts asset bundle (AI text prediction)

Overview
- Format: 1080x1920 (9:16), ~34.9 seconds
- Voice: flite "slt" (female) with naturalizing filters
- Music: synthetic magical ambient bed (pad + sparkle)
- Style: minimal motion with safe-area captions

Files
- scripts/short_script.txt
- captions/short.srt
- audio/voice.wav
- music/bed.wav
- audio/mix.wav
- video/shorts_ai_text_1080x1920.mp4

Build steps (reference)
1) Voiceover
   ffmpeg -f lavfi -i "flite=textfile=assets/shorts/scripts/short_script.txt:voice=slt" \
     -af "aresample=48000,rubberband=pitch=0.98:formant=preserved:transients=mixed,highpass=f=80,lowpass=f=12000,acompressor=threshold=0.02:ratio=3:attack=20:release=200,dynaudnorm=f=250:g=31,alimiter=limit=0.95" \
     -ar 48000 -ac 1 assets/shorts/audio/voice.wav

2) Music bed
   ffmpeg -f lavfi -i "sine=frequency=261.63:duration=35" \
     -f lavfi -i "sine=frequency=329.63:duration=35" \
     -f lavfi -i "sine=frequency=392.00:duration=35" \
     -f lavfi -i "sine=frequency=523.25:duration=35" \
     -f lavfi -i "sine=frequency=1046.50:duration=35" \
     -f lavfi -i "sine=frequency=1318.51:duration=35" \
     -f lavfi -i "sine=frequency=1567.98:duration=35" \
     -filter_complex "[0:a][1:a][2:a][3:a]amix=inputs=4,lowpass=f=1800,highpass=f=120,volume=0.10,chorus=0.5:0.6:40|50|60|70:0.3|0.25|0.2|0.2:0.2|0.25|0.3|0.35:0.2|0.2|0.2|0.2,tremolo=f=0.5:d=0.3[a_pad];[4:a][5:a][6:a]amix=inputs=3,highpass=f=600,volume=0.03,tremolo=f=6:d=0.4,aecho=0.7:0.8:120|240:0.3|0.2,chorus=0.4:0.5:30|40|50:0.15|0.12|0.1:0.3|0.2|0.2:0.2|0.2|0.2[a_sparkle];[a_pad][a_sparkle]amix=inputs=2,afade=t=in:st=0:d=2,afade=t=out:st=33:d=2,volume=0.9,alimiter=limit=0.9" \
     -ar 48000 -ac 2 assets/shorts/music/bed.wav

3) Mix
   ffmpeg -i assets/shorts/audio/voice.wav -i assets/shorts/music/bed.wav \
     -filter_complex "[1:a]volume=0.14[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95" \
     -ar 48000 -ac 2 -shortest assets/shorts/audio/mix.wav

4) Render video
   ffmpeg -f lavfi -i "color=c=#0b0b0f:s=1080x1920:d=34.90" \
     -i assets/shorts/audio/mix.wav \
     -vf "subtitles=assets/shorts/captions/short.srt:force_style='FontName=DejaVu Sans,FontSize=40,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=3,Shadow=0,Alignment=2,MarginV=320,MarginL=140,MarginR=140'" \
     -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
     -c:a aac -b:a 192k -shortest assets/shorts/video/shorts_ai_text_1080x1920.mp4
