#!/usr/bin/env python

import imp
import model

global config
config = imp.load_source('config', './config.py')

m = model.Model()

config.model(m)


#model Peers
#{
#  host Alice
#  host Bob
#  link [ Alice, Bob ]
#}
