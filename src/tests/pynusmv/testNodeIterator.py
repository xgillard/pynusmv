"""
This module verifies the behavior of the NodeIterator
"""
import unittest

from pynusmv.nusmv.cmd    import cmd  as _cmd
from pynusmv.nusmv.prop   import prop as _prop
from pynusmv.nusmv.fsm.be import be   as _be 

from pynusmv              import glob 
from pynusmv.init         import init_nusmv, deinit_nusmv
from pynusmv.node         import Node
from pynusmv.collections  import NodeIterator 

class TestNodeIterator(unittest.TestCase):
    def model(self):
        return '''
                MODULE main
                VAR       v: boolean; 
                IVAR      i: boolean;
                FROZENVAR f: boolean;
                ASSIGN
                  init(v) := TRUE;
                  next(v) := !v;
                  
                FAIRNESS 
                    v = TRUE;
                FAIRNESS
                    i = FALSE;
                '''
    def go_bmc(self):
        _cmd.Cmd_CommandExecute("build_boolean_model")
        _cmd.Cmd_CommandExecute("bmc_setup");
        
    def setUp(self):
        init_nusmv()
        glob.load(self.model())
        glob.flatten_hierarchy()
        glob.encode_variables()  # does it for BDD
        self.go_bmc()
        
        pd = _prop.PropPkg_get_prop_database()
        fsm= _prop.PropDb_master_get_be_fsm(pd)
        self._TEST = _be.BeFsm_get_fairness_list(fsm)

    def tearDown(self):
        deinit_nusmv()
    
    def test_from_pointer(self):
        iterator = NodeIterator.from_pointer(self._TEST)
        lst = [i for i in iterator]
        self.assertEqual(2, len(lst))
        
    def test_from_node(self):
        iterator = NodeIterator.from_node(Node.from_ptr(self._TEST))
        lst = [i for i in iterator]
        self.assertEqual(2, len(lst))
            