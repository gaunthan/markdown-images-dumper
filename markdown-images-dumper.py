#!/bin/python2
#encoding=utf-8
#
# 备份Markdown文件中的图片，并且更改图片链接为本地链接

import sys
import os
import requests

def getResName(res_url):
    begin = res_url.rfind('/')
    if begin == -1:
        raise Exception('Cannot resolve resource link: ' + res_url)
    end = res_url.find('?')

    return res_url[begin+1 : end]

def dumpToFile(path, data):
    fo = open(path, 'wb')
    fo.write(data)
    fo.close()

def dumpToLocal(res_url, dump_path):
    r = requests.get(res_url) 
    if r.status_code != requests.codes.ok:
        raise Exception('Cannot get "' + res_url + '"')
    res_name = getResName(r.url)    # need raw link
    dump_path = dump_path + '/' + res_name
    print 'Dumpping %s to %s' %(r.url, dump_path)
    dumpToFile(dump_path, r.content)
    
    return dump_path
    
def replaceResLinks(path, dump_path):
    line_contents = []

    fo = open(path, 'rb')
    for line in fo.readlines():
        begin = line.find('![](')
        if begin == -1:
            line_contents.append(line)
            continue

        begin = begin + 4
        offset = line[begin:].find(')')         
        if offset == -1:
            line_contents.append(line)
            print 'Invalid markdown useage: "%s"' %line
            continue
        
        res_url = line[begin : begin+offset]
        new_line = '![](' + dumpToLocal(res_url, dump_path) + ')\n'
        # print 'Replacing line "%s" to "%s"' %(line, new_line)
        line_contents.append(new_line)

    fo.close()

    fo = open(path, 'w')
    fo.writelines(line_contents) 
    fo.close()

def dumpDir(dir_path, dump_path):
    dirs = os.listdir(dir_path)
    for dir in dirs:
        path = dir_path + '/' + dir

        if os.path.isfile(path):
            if getResName(path) == getResName(sys.argv[0]) or path[-3:] != '.md':
                continue
            print 'Dealing with file %s' %path
            replaceResLinks(path, dump_path)
        else: # recursivly for directory
            print 'Found directory %s' %path
            dumpDir(path, dump_path)

if __name__ == '__main__':
    dir_path = raw_input('Enter working directory (default is "."):')
    if not dir_path:
        dir_path = '.'

    dump_path = raw_input('Saving to where (default is "./images"):')
    if not dump_path:
        dump_path = './images'

    print 'Dumpping...'
    dumpDir(dir_path, dump_path)
    print 'Done.'
        
    exit()
