from pynusmv.nusmv.cmd    import cmd    as _cmd
from pynusmv.nusmv.bmc    import bmc    as _bmc
from pynusmv.nusmv.utils  import utils  as _utils

from pynusmv.nusmv.enc    import enc    as _enc
from pynusmv.nusmv.enc.be import be     as _be


import pynusmv.init    as init
import pynusmv.glob    as glob
import pynusmv.be      as be

def go_bmc(model):
  glob.load_from_file(model)
  _cmd.Cmd_CommandExecute("flatten_hierarchy")
  _cmd.Cmd_CommandExecute("encode_variables")
  _cmd.Cmd_CommandExecute("build_boolean_model")
  _cmd.Cmd_CommandExecute("bmc_setup");


with init.init_nusmv():
  go_bmc("./examples/ctl/mutex.smv")
  _be_enc = _enc.Enc_get_be_encoding()
  _be_mgr = _be.BeEnc_get_be_manager(_be_enc)
  
  mgr = be.BeRbcManager(_be_mgr, freeit=False)
  vrai= be.Be.imply(be.Be.true(mgr), be.Be.true(mgr) + be.Be.false(mgr) )
  mgr.dump_gdl(vrai, None)

