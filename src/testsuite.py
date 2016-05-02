#! /usr/local/bin/python3
"""
This script creates a test suite that makes it easy for me to run regression 
tests on the code I've written and measure the coverage of that same code using
coverage.py

.. note::
    In order to get a more extended coverage report, use the following two 
    commands: 
    
    coverage run testsuite.py -m <prefixes>
    coverage html
"""
import unittest

from testsuiteutils import not_included, with_coverage, with_warnings

from tests.pynusmv.testAssoc             import TestAssoc
from tests.pynusmv.testBe                import TestBe
from tests.pynusmv.testBeCnf             import TestBeCnf
from tests.pynusmv.testBeEnc             import TestBeEnc
from tests.pynusmv.testBeFsm             import TestBeFsm
from tests.pynusmv.testBeManager         import TestBeManager
from tests.pynusmv.testBeVar             import TestBeVar
from tests.pynusmv.testBmcGlob           import TestBmcGlob
from tests.pynusmv.testBmcInvarSpec      import TestBmcInvarSpec
from tests.pynusmv.testBmcLTLspec        import TestBmcLTLSpec
from tests.pynusmv.testBmcModel          import TestBmcModel
from tests.pynusmv.testBmcUtils          import TestBmcUtils
from tests.pynusmv.testBoolSexpFsm       import TestBoolSexpFsm
from tests.pynusmv.testBuildBooleanModel import TestBuildBooleanModel
from tests.pynusmv.testIndexed           import TestIndexed
from tests.pynusmv.testNodeIterator      import TestNodeIterator
from tests.pynusmv.testNodeList          import TestNodeList
from tests.pynusmv.testSatSolver         import TestSatSolver
from tests.pynusmv.testSatIncSolver      import TestSatIncSolver
from tests.pynusmv.testSatSolverFactory  import TestSatSolverFactory
from tests.pynusmv.testSlist             import TestSlist
from tests.pynusmv.testTrace             import TestTrace
from tests.pynusmv.testTraceStep         import TestTraceStep
from tests.pynusmv.testWriteOnly         import TestWriteOnly
from tests.pynusmv.testWff               import TestWff

# from tests.pynusmv.testBeManager import TestBeRbcManager

def suite():
    """:return: the configured test suite"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAssoc))
    suite.addTest(unittest.makeSuite(TestBe))
    suite.addTest(unittest.makeSuite(TestBeCnf))
    suite.addTest(unittest.makeSuite(TestBeEnc))
    suite.addTest(unittest.makeSuite(TestBeFsm))
    suite.addTest(unittest.makeSuite(TestBeManager))
    suite.addTest(unittest.makeSuite(TestBeVar))
    suite.addTest(unittest.makeSuite(TestBmcGlob))
    suite.addTest(unittest.makeSuite(TestBmcInvarSpec))
    suite.addTest(unittest.makeSuite(TestBmcLTLSpec))
    suite.addTest(unittest.makeSuite(TestBmcModel))
    suite.addTest(unittest.makeSuite(TestBmcUtils))
    suite.addTest(unittest.makeSuite(TestBoolSexpFsm))
    suite.addTest(unittest.makeSuite(TestBuildBooleanModel))
    suite.addTest(unittest.makeSuite(TestIndexed))
    suite.addTest(unittest.makeSuite(TestNodeIterator))
    suite.addTest(unittest.makeSuite(TestNodeList))
    suite.addTest(unittest.makeSuite(TestSatSolver))
    suite.addTest(unittest.makeSuite(TestSatIncSolver))
    suite.addTest(unittest.makeSuite(TestSatSolverFactory))
    suite.addTest(unittest.makeSuite(TestSlist))
    suite.addTest(unittest.makeSuite(TestTrace))
    suite.addTest(unittest.makeSuite(TestTraceStep))
    suite.addTest(unittest.makeSuite(TestWriteOnly))
    suite.addTest(unittest.makeSuite(TestWff))
    
    not_included("tools.bmcLTL.*")
    return suite

@with_warnings
@with_coverage(
    'pynusmv/be/*',
    'pynusmv/bmc/*',
    'pynusmv/sexp/*',
    'pynusmv/collections.py',  
    'pynusmv/sat.py',
    'pynusmv/trace.py',
    'pynusmv/utils.py',
    'pynusmv/wff.py')
def run_suite():
    """Runs the configured test suite"""
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)

if __name__ == '__main__':
    run_suite()