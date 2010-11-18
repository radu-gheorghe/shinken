#!/usr/bin/env python
#Copyright (C) 2009-2010 :
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#
#This file is part of Shinken.
#
#Shinken is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Shinken is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with Shinken.  If not, see <http://www.gnu.org/licenses/>.


#This class is an application for launch checks
#The poller listen configuration from Arbiter in a port (first argument)
#the configuration gived by arbiter is schedulers where actionner will
#take checks.
#When already launch and have a conf, poller still listen to arbiter
#(one a timeout) if arbiter whant it to have a new conf, poller forgot
#old cheduler (and checks into) take new ones and do the (new) job.

import sys, os
import getopt
import ConfigParser
import platform

#We know that a Python 2.5 or Python3K will fail.
#We can say why and quit.
python_version = platform.python_version_tuple()

## Make sure people are using Python 2.5 or higher
if int(python_version[0]) == 2 and int(python_version[1]) < 4:
    print "Shinken require as a minimum Python 2.4.x, sorry"
    sys.exit(1)

if int(python_version[0]) == 3:
    print "Shinken is not yet compatible with Python3k, sorry"
    sys.exit(1)


#Pyro 4 dbg
sys.path.insert(0,'.')


#Try to load shinken lib.
#Maybe it's not in our python path, so we detect it
#it so (it's a untar install) we add .. in the path
try :
    from shinken.util import to_bool
    if os.name != 'nt':
      my_path = os.path.abspath(sys.modules['__main__'].__file__)
      elts = os.path.dirname(my_path).split(os.sep)[:-1]
      elts.append('shinken')
      sys.path.append(os.sep.join(elts))
except ImportError:
    #Now add in the python path the shinken lib
    #if we launch it in a direct way and
    #the shinken is not a python lib
    my_path = os.path.abspath(sys.modules['__main__'].__file__)
    elts = os.path.dirname(my_path).split(os.sep)[:-1]
    sys.path.append(os.sep.join(elts))
    elts.append('shinken')
    sys.path.append(os.sep.join(elts))

try:
    import shinken.pyro_wrapper
except ImportError:
    print "Shinken require the Python Pyro module. Please install it."
    sys.exit(1)

Pyro = shinken.pyro_wrapper.Pyro

from shinken.satellite import Satellite
from shinken.util import to_int, to_bool
from shinken.module import Module, Modules

VERSION = "0.3"


#Our main APP class
class Poller (Satellite):
	do_checks = True #I do checks
	do_actions = False #but no actions
	#default_port = 7771

	properties = {
		'workdir' : {'default' : '/usr/local/shinken/var', 'pythonize' : None, 'path' : True},
		'pidfile' : {'default' : '/usr/local/shinken/var/pollerd.pid', 'pythonize' : None, 'path' : True},
		'port' : {'default' : '7771', 'pythonize' : to_int},
		'host' : {'default' : '0.0.0.0', 'pythonize' : None},
		'user' : {'default' : 'shinken', 'pythonize' : None},
		'group' : {'default' : 'shinken', 'pythonize' : None},
		'idontcareaboutsecurity' : {'default' : '0', 'pythonize' : to_bool}
		}


################### Process launch part
def usage(name):
    print "Shinken Poller Daemon, version %s, from : " % VERSION
    print "        Gabes Jean, naparuba@gmail.com"
    print "        Gerhard Lausser, Gerhard.Lausser@consol.de"
    print "Usage: %s [options] [-c configfile]" % name
    print "Options:"
    print " -c, --config"
    print "\tConfig file."
    print " -d, --daemon"
    print "\tRun in daemon mode"
    print " -r, --replace"
    print "\tReplace previous running scheduler"
    print " -h, --help"
    print "\tPrint detailed help screen"
    print " --debug"
    print "\tDebug File. Default : no use (why debug a bug free program? :) )"


#lets go to the party
if __name__ == "__main__":
    #Manage the options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hrdc::w", ["help", "replace", "daemon", "config=", "debug=", "easter"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage(sys.argv[0])
        sys.exit(2)
    #Default params
    config_file = None
    is_daemon=False
    do_replace=False
    debug=False
    debug_file=None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage(sys.argv[0])
            sys.exit()
	elif o in ("-r", "--replace"):
            do_replace = True
        elif o in ("-c", "--config"):
            config_file = a
        elif o in ("-d", "--daemon"):
            is_daemon = True
	elif o in ("--debug"):
            debug = True
	    debug_file = a
        else:
            print "Sorry, the option",o, a, "is unknown"
	    usage(sys.argv[0])
            sys.exit()

    p = Poller(config_file, is_daemon, do_replace, debug, debug_file)
    #import cProfile
    p.main()
    #command = """p.main()"""
    #cProfile.runctx( command, globals(), locals(), filename="/tmp/Poller.profile" )
