Shorts asset bundle (AI text prediction)

Overview
- Format: 1080x1920 (9:16), ~34.9 seconds
- Voice: flite "slt" (female)
- Music: synthetic ambient bed (major chord pad)
- Style: minimal motion with captions

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
     -ar 48000 -ac 1 assets/shorts/audio/voice.wav

2) Music bed
   ffmpeg -f lavfi -i "sine=frequency=261.63:duration=35" \
     -f lavfi -i "sine=frequency=329.63:duration=35" \
     -f lavfi -i "sine=frequency=392.00:duration=35" \
     -filter_complex "[0:a][1:a][2:a]amix=inputs=3,lowpass=f=1200,volume=0.12,tremolo=f=4:d=0.4,aecho=0.8:0.9:400|600:0.2|0.15,afade=t=in:st=0:d=2,afade=t=out:st=33:d=2" \
     -ar 48000 -ac 2 assets/shorts/music/bed.wav

3) Mix
   ffmpeg -i assets/shorts/audio/voice.wav -i assets/shorts/music/bed.wav \
     -filter_complex "[1:a]volume=0.15[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2" \
     -ar 48000 -ac 2 -shortest assets/shorts/audio/mix.wav

4) Render video
   ffmpeg -f lavfi -i "color=c=#0b0b0f:s=1080x1920:d=34.90" \
     -i assets/shorts/audio/mix.wav \
     -vf "subtitles=assets/shorts/captions/short.srt:force_style='FontName=DejaVu Sans,FontSize=52,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=3,Shadow=0,Alignment=2,MarginV=140'" \
     -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
     -c:a aac -b:a 192k -shortest assets/shorts/video/shorts_ai_text_1080x1920.mp4
