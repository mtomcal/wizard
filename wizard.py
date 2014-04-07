import os
import urllib
import glob
import sys
import operator
import tempfile
import shutil
import json

class Tmp():
    def __init__(self):
        self.tempdir = ""
        self._mktemp()

    def _mktemp(self):
        self.tempdir = tempfile.mkdtemp()

    def open_tmp(self, filename, flags):
        return open(os.path.join(self.tempdir, filename), flags)

    def del_tmp(self):
        shutil.rmtree(self.tempdir)

    def tmp_path(self, filename):
        return os.path.join(self.tempdir, filename)

    def filecopy_to_tmp(self, path):
        shutil.copy(path, self.tmp_path(''))

    def dircopy_to_tmp(self, path):
        shutil.copytree(path, self.tmp_path(''))

def read_file(self, filename):
    with open(filename, 'r') as reader:
        return reader.readlines()
    raise IOError

def load_config():
    with open('config.json', 'r') as reader:
        return json.load(reader)
    raise IOError

def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
                os.symlink(os.readlink(s), d)
                try:
                    st = os.lstat(s)
                    mode = stat.S_IMODE(st.st_mode)
                    os.lchmod(d, mode)
                except:
                    pass # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
            print "%s updated" % (d)

def install(name, config, tmp):
    package = {}
    try:
        package = config["packages"][name]
    except KeyError:
        print "Could not find the package %s, sorry." % (name)
        sys.exit(1)
    os.system("git clone %s %s" % (package["source"], tmp.tmp_path(name)))
    shutil.rmtree("%s/.git" % tmp.tmp_path(name))
    os.system("easy_install --user `cat %s/requirements.txt`" % (tmp.tmp_path(name)))
    os.system("easy_install --user `cat %s/%s_requirements.txt`" % (tmp.tmp_path(name), name))
    shutil.copytree(tmp.tmp_path(name), "%s/%s" % (os.getcwd(), name))
    tmp.del_tmp()
    print "**** %s/%s installed ****" % (os.getcwd(), name)

def update(name, config, tmp):
    package = {}
    try:
        package = config["packages"][name]
    except KeyError:
        print "Could not find the package %s, sorry." % (name)
        sys.exit(1)

    if not os.path.isdir(name):
        print """****
The %s/ folder doesn't exist in %s so I can't update it.
Switch to the folder where %s/ is located and run update again.
****""" % (name, os.getcwd(), name)
        exit(1)
    os.system("git clone %s %s" % (package["source"], tmp.tmp_path(name)))
    shutil.rmtree("%s/.git" % tmp.tmp_path(name))
    os.system("easy_install --user `cat %s/requirements.txt`" % (tmp.tmp_path(name)))
    os.system("easy_install --user `cat %s/%s_requirements.txt`" % (tmp.tmp_path(name), name))
    copytree(tmp.tmp_path(name), "%s/%s" % (os.getcwd(), name))
    tmp.del_tmp()
    print "**** %s/%s updated ****" % (os.getcwd(), name)

def upgrade(config, tmp):
    urllib.urlretrieve("https://raw.githubusercontent.com/mtomcal/wizard/master/wizard.py", filename="wizard.py")
    urllib.urlretrieve("https://raw.githubusercontent.com/mtomcal/wizard/master/config.json", filename="config.json")
    print "**** Wizard upgraded ****"

def main():
    tmp = Tmp()
    config = load_config()
    usage = """wizard.py    A Simple Python Package Manager for Git repositories by Michael A Tomcal (c) 2014
Usage:
    python wizard.py install <name> Install a package by name to the current folder
    python wizard.py update <name>  Upgrade a package by name in a current folder
    python wizard.py upgrade        Upgrade Wizard and its package listings"""
    try:
        if sys.argv[1] == 'install':
            install(sys.argv[2], config, tmp)
        elif sys.argv[1] == 'update':
            update(sys.argv[2], config, tmp)
        elif sys.argv[1] == 'upgrade':
            upgrade(config, tmp)
        else:
            print usage
    except IndexError:
        print usage

main()




