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


# here is a node class for dependency_node(s) and a factory to create them

import re

#pat = "(h1;db | h2;db | h3;db) & (h4;Apache & h5;Apache & h6;Apache) & (h7;lvs | h8;lvs)"
#pat2 = "h1;db | h2;db"
#pat3 = "(h1;db | h2;db | h3;db) & (h4;Apache & h5;Apache)"
#pat4 = "2 of: h1;db | h2;db | h3;db"

class DependencyNode(object):
    def __init__(self):
        self.operand = None
        self.sons = []
        self.of_values = 0

    def __str__(self):
        return "Op:'%s' Val:'%s' Sons:'[%s]'" % (self.operand, self.of_values, ','.join([str(s) for s in self.sons]))


    # We will get the state of this node, by looking at the state of
    # our sons, and apply our operand
    def get_state(self):
        print "Ask state of me", self

        # If we are a 'object', wee just git the host/service
        # hard state
        if self.operand == 'object':
            state = self.sons[0].last_hard_state
            print "Get the hard state %s for the object %s" % (state, self.sons[0].get_name())
            return state
        
        # First we get teh state of all our sons
        states = []
        for s in self.sons:
            st = s.get_state()

        return 0

        


class DependencyNodeFactory(object):
    def __init__(self):
        pass

    # the () will be eval in a recursiv way, only one level of ()
    def eval_cor_patern(self, patern, hosts, services):
        patern = patern.strip()
        print "*****Loop", patern
        complex_node = False
    
        # Look if it's a complex patern (with rule) or
        # if it's a leef ofit, like a host/service
        for m in '()+&|':
            if m in patern:
                complex_node = True
    
        is_of_nb = False

        node = DependencyNode()
        p = "^(\d+) *of: *(.+)"
        r = re.compile(p)
        m = r.search(patern)
        if m != None:
            print "Match the of: thing N=", m.groups()
            node.operand = 'of:'
            node.of_values = int(m.groups()[0])
            patern = m.groups()[1]
    
        print "Is so complex?", patern, complex_node
    
        # if it's a single host/service
        if not complex_node:
            print "Try to find?", patern
            node.operand = 'object'
            obj = self.find_object(patern, hosts, services)
            node.sons.append(obj)
            return node
        else:
            print "Is complex"

        in_par = False
        tmp = ''
        for c in patern:
            if c == '(':
                in_par = True
                tmp = tmp.strip()
                if tmp != '':
                    o = self.eval_cor_patern(tmp, hosts, services)
                    print "1( I've %s got new sons" % patern , o
                    node.sons.append(o)
                continue
            if c == ')':
                in_par = False
                tmp = tmp.strip()
                if tmp != '':
                    print "Evaling sub pat", tmp
                    o = self.eval_cor_patern(tmp, hosts, services)
                    print "2) I've %s got new sons" % patern , o
                    node.sons.append(o)
                else:
                    print "Fuck a node son!"
                tmp = ''
                continue

            if not in_par:
                if c == '&' or c == '|':
                    current_rule = node.operand
                    print "Current rule", current_rule
                    if current_rule != None and current_rule != 'of:' and c != current_rule:
                        print "Fuck, you mix all dumbass!"
                        return None
                    if current_rule != 'of:':
                        node.operand = c
                    tmp = tmp.strip()
                    if tmp != '':
                        o = self.eval_cor_patern(tmp, hosts, services)
                        print "3&| I've %s got new sons" % patern , o
                        node.sons.append(o)
                    tmp = ''
                    continue
                else:
                    tmp += c
            else:
                tmp += c

        tmp = tmp.strip()
        if tmp != '':
            o = self.eval_cor_patern(tmp, hosts, services)
            print "4end I've %s got new sons" % patern , o
            node.sons.append(o)

        print "End, tmp", tmp
        print "R %s :" % patern, node
        return node


    # We've got an object, like h1,db1 that mean the
    # db1 service of the host db1, or just h1, that mean
    # the host h1.
    def find_object(self, patern, hosts, services):
        print "Finding object", patern
        is_service = False
        # h_name, service_desc are , separated
        elts = patern.split(',')
        host_name = elts[0]
        # Look if we have a service
        if len(elts) > 1:
            is_service = True
            service_description = elts[1]
        if is_service:
            obj = services.find_srv_by_name_and_hostname(host_name, service_description)
            print "Find service", obj.get_name()
            return obj
        else:
            obj = hosts.find_by_name(host_name)
            print "Find host", obj.get_name()
            return obj
