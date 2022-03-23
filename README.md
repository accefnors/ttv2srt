# ttv2srt
Download twitch.tv VOD chats as SubRip .srt files  
Inspired by https://vods.online/

```
usage: ttv2srt.py [-h] [-e] [-t TIME] [-k | -m] [-x | -s] [-o OUTPUT] input

Download Twitch VOD chat as a SubRip (.srt) file. Modify defaults by editing this file (ttv2srt.py).

positional arguments:
  input                 Twitch VOD URL or ID

options:
  -h, --help            show this help message and exit
  -e, --emoji           Display emojis as their text values (default = False)
  -t TIME, --time TIME  Comment on-screen duration in seconds (default = 60)
  -k, --color           Color usernames. Not supported by all media players. (default = True)
  -m, --monochrome      Don't color usernames (default = False)
  -x, --extended        Subtitles in bottom-right corner. Not supported by all media players. (default = True)
  -s, --simple          Subtitles in default position (default = False)
  -o OUTPUT, --output OUTPUT
                        output filename.
```
