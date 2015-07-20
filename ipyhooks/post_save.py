# -*- coding: utf-8 -*-
"""
Created on 20.07.2015

@author: frank
"""

import os
from subprocess import check_call

def extract_path_list(path, path_list=None):
    if path_list is None:
        path_list = []
    head, tail = os.path.split(path)
    if tail:
        path_list.insert(0, tail)
        return extract_path_list(head, path_list)
    else:
        if head:
            path_list.insert(0, head)
        return path_list

def post_save(model, os_path, contents_manager):
    """post-save hook for converting notebooks to .py scripts"""
    if model['type'] != 'notebook':
        return # only do this for notebooks
    base_dir = 'ipynb'
    rel_path = os.path.relpath(os_path)
    path_list = extract_path_list(rel_path)
    if path_list[0] == base_dir:        
        fname_md = os.path.join('md', os.path.join(*path_list[1:]))
        fname_md = os.path.splitext(fname_md)[0] + '.md'
        md_dir = os.path.dirname(fname_md)
        if not os.path.isdir(md_dir):
            print "create directory: " + md_dir
            os.makedirs(md_dir)
    else:        
        fname_base = os.path.splitext(os_path)[0]
        fname_md = fname_base + '.md'
    
    cmd_line = ['notedown', os_path, '--to', 'markdown', '--strip', '--output', fname_md]
    print("c.FileContentsManager.post_save_hook: running command line\n" + " ".join(cmd_line))
    check_call(cmd_line)
