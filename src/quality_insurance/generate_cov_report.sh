:
# This script generates the coverage report in html format.
coverage run -m unittest
coverage html --include "pynusmv/bmc/*,pynusmv/be/*,pynusmv/sexp/*,pynusmv/collections*,pynusmv/sat*,pynusmv/trace*,pynusmv/utils*,pynusmv/wff*,tools/bmcLTL/*,tools/diagnosability*" --omit "pynusmv/bmc/lower_intf/*"
