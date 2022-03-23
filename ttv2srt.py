#!/usr/bin/env python3

################################################################################
############################# USER SETTINGS: START #############################
################################################################################

# How long each comment should appear on screen (in seconds)
commentDuration = 60

# Include emoji text values [True|False]
emojiText = False

# Color usernames (not supported by all media players) [True|False]
colorTags = True

# Subtitles in bottom-right corner (not supported by all media players) [True|False]
posTags = True

################################################################################
############################## USER SETTINGS: END ##############################
################################################################################

import argparse
import sys
import re
import requests
import datetime
import srt

def main():
    parser = argparse.ArgumentParser(
            description='Download Twitch VOD chat as a SubRip (.srt) file. ' +
                        'Modify defaults by editing this file (%(prog)s).')
    parser.add_argument(
            'input',
            type=str,
            help='Twitch VOD URL or ID')
    parser.add_argument(
            '-e', '--emoji',
            dest='emoji',
            action='store_const',
            const=True,
            default=emojiText,
            help='Display emojis as their text values (default = ' + str(emojiText) +')')
    parser.add_argument(
            '-t', '--time',
            dest='time',
            type=int,
            default=commentDuration,
            help='Comment on-screen duration in seconds (default = ' + str(commentDuration) + ')')
    color = parser.add_mutually_exclusive_group()
    color.add_argument(
            '-k', '--color',
            dest='color',
            action='store_const',
            const=True,
            help='Color usernames. Not supported by all media players. (default = ' + str(colorTags) + ')')
    color.add_argument(
            '-m', '--monochrome',
            dest='color',
            action='store_const',
            const=False,
            help='Don\'t color usernames (default = ' + str(not colorTags) + ')')
    parser.set_defaults(color=colorTags)
    position = parser.add_mutually_exclusive_group()
    position.add_argument(
            '-x', '--extended',
            dest='position',
            action='store_const',
            const=True,
            help='Subtitles in bottom-right corner. Not supported by all media players. (default = ' + str(posTags) + ')')
    position.add_argument(
            '-s', '--simple',
            dest='position',
            action='store_const',
            const=False,
            help='Subtitles in default position (default = ' + str(not posTags) + ')')
    parser.set_defaults(position=posTags)
    parser.add_argument(
            '-o', '--output',
            dest='output',
            type=str,
            help='output filename.')

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    vodID = re.search('.*?(\d+).*', args.input, re.I).group(1)
    url = 'https://api.twitch.tv/v5/videos/' + vodID + '/comments'
    headers = {'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko'}

    r = requests.get(url, headers=headers)
    jsonCurrent = r.json()
    jsonDump = jsonCurrent['comments']

    print('Downloading chat...')
    while '_next' in jsonCurrent:
        nextCursor = jsonCurrent['_next']
        r = requests.get(url + '?cursor=' + nextCursor, headers=headers)
        jsonCurrent = r.json()
        jsonDump += jsonCurrent['comments']

    print('Parsing comments...')
    unmerged = ''
    idx = 1
    for comment in jsonDump:
        currSub = ''
        currSubText = ''
        if args.emoji:
            currSubText += comment['message']['body']
        else:
            for obj in comment['message']['fragments']:
                if len(obj) == 1:
                    currSubText += obj['text'].strip() + ' '
            if not currSubText or currSubText.isspace():
                continue
        currSub += (str(idx) + '\n' +
                '0' + str(datetime.timedelta(seconds=comment['content_offset_seconds']))[:-3] +
                ' --> ' +
                '0' + str(datetime.timedelta(seconds=(comment['content_offset_seconds'] +
                    args.time)))[:-3] + '\n')
        if args.position:
            currSub += '{\\an3}'
        if args.color:
            currSub += '<font color="'
            try:
                currSub += comment['message']['user_color']
            except:
                currSub += '#1E90FF'
            currSub += '">'
        currSub += comment['commenter']['display_name']
        currSub += ': </font><font color="#FFFFFF">' if args.color else ': '
        currSub += currSubText.rstrip()
        currSub += '</font>\n\n' if args.color else '\n\n'
        unmerged += currSub 
        idx += 1

    del r, jsonCurrent, jsonDump

    print('Merging overlaps...')
    merged = merge(unmerged)

    if args.output is None:
        args.output = str(vodID) + '.srt'

    with open(args.output, 'w') as f:
        f.write(merged)
    print(args.output + ' written.')

def merge(s):
    subs = list(srt.parse(s))
    curr = len(subs) - 2
    nxt = curr + 1

    while curr >= 0:
        if subs[curr].end == subs[nxt].end and subs[curr].start == subs[nxt].start:
            subs[curr].content += '\n' + subs[nxt].content
            del subs[nxt]
        i = 0
        while subs[curr].end > subs[nxt].start:
            sel = nxt + i
            if subs[curr].end < subs[sel].end:
                subs.insert(sel, srt.Subtitle(subs[sel].index,
                                                subs[sel].start,
                                                subs[sel].end,
                                                subs[sel].content,
                                                subs[sel].proprietary))
                subs[sel+1].start = subs[curr].end
                subs[sel].end = subs[curr].end
                j = 0
                while sel - j > curr:
                    subs[sel-j].content = subs[curr].content + '\n' + subs[sel-j].content
                    j += 1
                subs[curr].end = subs[nxt].start
            i += 1
        curr -= 1
        nxt -= 1

    i = len(subs) -1
    while i >= 0:
        if subs[i].start == subs[i].end:
            del subs[i]
        i -= 1

    i = 0
    while i < len(subs):
        subs[i].index = i + 1
        i += 1

    return srt.compose(subs, reindex=False, start_index=1, strict=False, eol=None, in_place=False)

if __name__ == "__main__":
    main()
