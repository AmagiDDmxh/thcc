import sys
import os
import requests
import re
import subprocess
import time
from template import *
from bs4 import BeautifulSoup

def get_card_list(types, topics):
    # The library Topic site Souplify the
    # s.get('https://teamtreehouse.com/library/topic:python').text
    type_course = BeautifulSoup(s.get(treehouse
                                      + '/library/topic:'
                                      + topics
                                      + '/type:'
                                      + types).text,
                                'lxml')
    print('[+] Got the library typeof: ' + types + '\n')
    print('[+] topics is: ' + topics)

    # Got the available card to a list
    # [<li class="card">...</li>,<li class="card">..</li>.and so on]
    card_list = list(filter(lambda li: len(li.find_all('li', 'pro-content')) <= 0,
                            type_course.select('.card-list li.card')))
    print('[+] Got the available card-list amount: {}'.format(len(card_list)))

    return card_list


def workshop(i):
    print('[+] Try to find workshop card')

    card_box = treehouse + i.find('a')['href']
    card_prompt = '[*] Got the card-box link'
    print('-' * len(card_prompt))

    at_preview = BeautifulSoup(s.get(card_box).text, 'lxml')
    stage_xhr = BeautifulSoup(
        s.get(treehouse
              + at_preview.find(
            'ul', 'stage-progress-list')['data-url']).text,
        'lxml'
    )
    steps = list(
        map(lambda a: treehouse + a['href'],
            stage_xhr.select('a.stage-progress-step-link')
            ))

    steps_prompt = '[*] Find steps: {}.length: {}'.format(steps, len(steps))
    print('-' * len(steps_prompt))

    markdown = open('!teacher_note.html', 'w')
    print('[+] Create teacherNote')
    markdown.write(HTMLheader)

    with open('markdown-zone.css', 'w') as markdown_css:
        markdown_css.write(markdown_zone_css)
        markdown_css.close()

    for j in steps:
        c = BeautifulSoup(s.get(j).text, 'lxml')
        step_title = c.select('.secondary-heading h1')[0].string
        print('[*] Current step: {}'.format(step_title))

        if c.find('div', 'markdown-zone'):
            markdown.write(c.find('div', 'markdown-zone').decode_contents())
            print('[+] Find markdown-zone')

        caption_name = '{}_subtitle.html'.format(step_title)

        caption = open(caption_name, 'w')
        caption.write(HTMLheader)
        print('[+] Create caption file')
        if c.select('#video-transcript-tab-content ul'):
            caption.write(c.select('#video-transcript-tab-content ul')[0].decode())
            markdown.write('<p>Translate:  <a href="{}">{}</a><hr></p>'.format(caption_name, step_title))

        caption.write(HTMLfooter)
        caption.close()
        caption_prompt = '[*] save caption file'
        print('{}\n{}'.format(caption_prompt, '-' * len(caption_prompt)))

        src = re.findall(r'src="(.*?)"', str(c.video))[0]
        print('[+] Find video src')
        print('[+] Try to download----------------------------')

        youtube_cmd = ['youtube-dl', '--proxy', socks5, src]
        subprocess.run(youtube_cmd)
        video_prompt = '[*] Video **{}** download Done!' \
                       '\nTrying to download next'.format(step_title)
        print('{}\n{}'.format(video_prompt, '-' * len(video_prompt)))
        time.sleep(10)

    markdown.write(HTMLfooter)
    markdown.close()
    os.chdir('..')
    time.sleep(30)
    return


def course(i):
    print('[*] Try to find course card')
    card_box = treehouse + i.find('a')['href'] + '/stages'
    print('[x] Got the card-box link')

    markdown = open('!teachers_note.html', 'w')
    print('[X] Create teacherNote')
    markdown.write(HTMLheader)

    stages = BeautifulSoup(s.get(card_box).text, 'lxml')
    print('[*] Stages lenth: {}'.format(len(stages.select('.steps-list'))))

    steps = list(
        map(lambda a: treehouse + a['href'],
            filter(
                lambda a: not re.search(r'questions|objective', a.p.string),
                stages.select('.steps-list li a'))))
    print('[*] Find steps: {}.length: {}'.format(steps, len(steps)))

    with open('markdown-zone.css', 'w') as markdown_css:
        markdown_css.write(markdown_zone_css)
        markdown_css.close()

    for j in steps:
        c = BeautifulSoup(s.get(j).text, 'lxml')
        step_title = c.select('.secondary-heading h1')[0].string

        if c.find('div', 'markdown-zone'):
            markdown.write(c.find('div', 'markdown-zone').decode_contents())

        caption_name = '{}_subtitle.html'.format(re.sub(r'[\\/:*<>?"|]+', '', step_title))

        caption = open(caption_name, 'w')
        caption.write(HTMLheader)
        print('[+] create caption file')
        if c.select('#video-transcript-tab-content ul'):
            caption.write(
                c.select('#video-transcript-tab-content ul')[0].decode())
            markdown.write(
                '<p>Translate:  <a href="{}">{}</a><hr><p>'
                    .format(caption_name, step_title))

        caption.write(HTMLfooter)
        caption.close()
        caption_prompt = '[*] save caption file'
        print('{}\n{}'.format(caption_prompt, '-' * len(caption_prompt)))

        src = re.findall(r'src="(.*?)"', str(c.video.contents))[0]
        print('[+] Find video src')
        print('[+] Trying to download----------------------------')

        youtube_cmd = ['youtube-dl', '--proxy', socks5, src]
        subprocess.run(youtube_cmd)

        video_prompt = '[*] Video **{}** download Done!\nTrying to download next'.format(step_title)
        print('{}\n{}'.format(video_prompt, '-' * len(video_prompt)))
        time.sleep(10)

    markdown.write(HTMLfooter)
    markdown.close()
    os.chdir('..')
    time.sleep(30)
    return


def main():
    print('current dir: {}'.format(os.path.abspath('.')))
    types = 'course'
    topic = 'css'
    card_list = get_card_list(types, topic)

    for i in card_list:
        card_title = i.find('h3', 'card-title').string
        print('[x] Got the card-title: {}'.format(card_title))

        if os.path.isdir('./{}'.format(card_title)):
            os.chdir('./{}'.format(card_title))
        else:
            os.mkdir(card_title)
            os.chdir('./{}'.format(card_title))
        print('[*] Current dir is: {}'.format(os.path.abspath('.')))

        if types == 'course':
            course(i)
        elif types == 'workshop':
            workshop(i)

        card_prompt = '[*] Stage Done! Trying to next card~'
        print('{}\n{}'.format(card_prompt, '-' * len(card_prompt)))
        print('current dir: {}'.format(os.path.abspath('.')))


if __name__ == '__main__':
    main()
