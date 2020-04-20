#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import re
import requests
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import getpass
import time
import yaml

# Default values:
url_string = 'https://nordvpn.com/ru/ovpn/'
regex = re.compile(r'<span class="mr-2">'
                   r'(\S*)'
                   r'</span>')


def isOpen(host, port=80):
    '''
    Checking host for open port
    host - string
    port - string / int
    
    Returns (string, bool)
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      s.connect((host, int(port)))
      s.shutdown(2)
      return host, True
    except:
      return host, False

def getContent(url_string):
    '''
    Loading web page form provided url by using http
    url_string - string
    
    Returns string
    '''
    try:
        print('Geting content from ', url_string)
        r = requests.get(url_string)
        return r.text
    except requests.exceptions.ConnectionError as e:
        raise SystemExit(str(e).strip('()'))
    except requests.exceptions.SSLError as e:
        raise SystemExit(str(e).strip('()'))
    except requests.exceptions.RequestException as e:
        raise SystemExit(str(e).strip('()'))

def findMatches(obj, regex):
    '''
    Searching object using provided regexp
    obj - string
    regex - re object
    
    Returns list
    '''
    print('Finding servers...')
    match = regex.findall(obj)
    if match: return match

def writeFile(d):
    '''
    Writing dictionary into yaml file.
    d - proxy dictionary
    '''
    print('Making yaml with all servers...')
    timestr = 'all_servers_' + time.strftime("%Y%m%d-%H%M%S") + '.yml'
    with open (timestr, 'w') as f:
        yaml.dump(d, f)
        
def generateProxy(hosts):
    '''
    Generating proxys list
    hosts - list of strings
    
    Returns dictionary
    '''
    print('Generating proxys list...')
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_list = []
        tlist = []
        flist = []
        for host in hosts:
            future = executor.submit(isOpen, host, '80')
            future_list.append(future)
        with click.progressbar(length=len(future_list),
                               show_pos=True,
                               fill_char='#',
                               empty_char=' ') as bar:           
            for f in as_completed(future_list):
                if f.result()[1]:
                    tlist.append(f.result()[0])
                else:
                    flist.append(f.result()[0])                
                bar.update(1)
        d = {True:tlist, False:flist}
        return d
  
def generateConfig(login, password, proxy_d, port=80):
    '''
    Writing dictionary into txt file.
    login - string
    password - string
    proxy_d - proxy dictionary 
    port - integer/string
    '''
    print('Making config file...')
    timestr = 'config_file_' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
    with open (timestr, 'w') as f:
        for host in proxy_d[True]:
            s = 'http://' + login + ':' + password + '@' + host + ':' + str(port) + '\r\n'
            f.write(s)            

if __name__ == '__main__':  
    t = getContent(url_string)
    try:
        l = findMatches(t, regex)    
        d = generateProxy(l)
        writeFile(d)
        print('Proxys list successfully generated!')
    except:
        raise SystemExit('Something went terrible wrong!')
    try:
        login = input('Input login: ')
        password = getpass.getpass()
        generateConfig(login, password, d)
        print('Success!')
    except:
        raise SystemExit('Something went terrible wrong!')