# -*- coding: utf-8 -*-
'''
Created on 20.07.2015
@author: frank

Install the notedown hook into an ipython profile.

Usage example:
    python setup.py notedown --profile=myprofile 
'''
from distutils.core import setup, Command
from distutils.errors import DistutilsOptionError
import os
from subprocess import check_output

# http://stackoverflow.com/questions/677577/distutils-how-to-pass-a-user-defined-parameter-to-setup-py

DEFAULT_INSERT_POS_MARKER = "# c.FileContentsManager.post_save_hook = None"
INSERT_MARKER_START = "###BEGIN_ipyhooks_post_save_INSERT###"
INSERT_MARKER_END = "###END_ipyhooks_post_save_INSERT###"

HOOK_INSERT = '''
try:
    from ipyhooks.post_save import post_save
    c.FileContentsManager.post_save_hook = post_save
except ImportError:
    import warnings
    msg = """
***ImportError*****
You need to install Frank's little ipyhooks package!
Go to ObjSimPy/ipyhooks.
there you run: 'python setup.py install'
*******************
"""    
    warnings.warn(msg)
'''


class notedown(Command):
    description = "install ipython post save hook for saving notebooks as Markdown"
    user_options = [
        ('profile=', ## '=' defines that the parameter has arguments. See getopt doc. 
         None, 
         'specify the ipython profile where the hook is to be installed',
         ),
        ]
    
    def initialize_options(self):
        self.profile = 'default'
        self.profile_dir = None
        
    def finalize_options(self):
        profile_dir = os.path.join(os.environ.get('HOME'), '.ipython', 'profile_'+self.profile)
        if not os.path.isdir(profile_dir):
            raise DistutilsOptionError("Profile dir not found: " + profile_dir)
        self.profile_dir = profile_dir
        
    def run(self):
        print "checking notedown ..."
        try:
            version = check_output(['notedown', '--version'])
        except OSError:
            print("Error: notedown not installed!")
            print("       Please install notedown before installing the hook!")
            print("       You can get notedown from github by calling:")
            print("       > git clone https://github.com/aaren/notedown.git")
            print("       --> Hook installation canceled <--")            
            return       
            
        print "installed notedown version = " + version
        
        
        print "installing notedown hook in profile: " + self.profile
        print "profile dir: " + self.profile_dir
        fname_config = os.path.join(self.profile_dir, 'ipython_notebook_config.py')
        if not os.path.isfile(fname_config):
            # create file
            print "creating config file: " + fname_config
            fobj = open(fname_config, 'w')
            fobj.write("c = get_config()\n")
            fobj.close()
        
        self.strip_old_hook(fname_config)
        self.insert_hook(fname_config)
        
    def strip_old_hook(self, fname_config):
        fobj = open(fname_config, 'r')
        lines = fobj.readlines()
        fobj.close()
        
        start_line = None
        stop_line = None
        
        # find start and stop marker
        for line_num, line in enumerate(lines):
            if line.startswith(INSERT_MARKER_START):
                start_line = line_num
            if line.startswith(INSERT_MARKER_END):
                stop_line = line_num
                break
            
        if start_line is not None and stop_line is not None:            
            print "stripping old hook insert: lines from {} to {}".format(start_line, stop_line)
            out_lines = lines[:start_line] + lines[stop_line+1:]        
            fobj = open(fname_config, 'w')
            fobj.write(''.join(out_lines))
            fobj.close()
        
    def insert_hook(self, fname_config):
        print "inserting hook into: " + fname_config
        
        fobj = open(fname_config, 'r')
        lines = fobj.readlines()
        fobj.close()
        
        out_lines = []
        for line_num, line in enumerate(lines):
            out_lines.append(line)
            if line.startswith(DEFAULT_INSERT_POS_MARKER):
                break
        out_lines.append(INSERT_MARKER_START + "\n")
        out_lines.append(HOOK_INSERT)
        out_lines.append(INSERT_MARKER_END + "\n")
        
        out_lines += lines[line_num+1:]
        
        fobj = open(fname_config, 'w')
        fobj.write(''.join(out_lines))
        fobj.close()

setup(name='ipyhooks',
      version='0.1',
      cmdclass={'notedown': notedown,
                },
      packages=['ipyhooks',
                ],
      )
