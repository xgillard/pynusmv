# Configures the environment in order to be able to run the tools etc..
# this function takes one param: the location of pynusmv
function setup_env {
  PYNUSMV=$1
  SOURCE=${PYNUSMV}/src
  LIBRARY=${SOURCE}/lib  

  # for python
  export PYTHONPATH=${PYTHONPATH}:${SOURCE}

  if [[ ! -e lib ]]; then
    # unfortunately, as of OSX El Capitan, SIP is enabled by default (and you don't want to disable it)
    # however, you need a way to load the dynamic lib so creating a symlink to that place does the job
    # since it does it well on both linux and OSX, there's no need to set the LD_LIBRARY_PATH anymore
    # (even though that might be somewhat cleaner) 
    ln -s ${LIBRARY} lib
  fi
}

function license_disclaimer {
    echo "**************************************************************************"
    echo "* This program is free software: you can redistribute it and/or modify   *"
    echo "* it under the terms of the GNU General Public License as published by   *"
    echo "* the Free Software Foundation, either version 3 of the License, or      *"
    echo "* (at your option) any later version.                                    *"
    echo "*                                                                        *"
    echo "* This program is distributed in the hope that it will be useful,        *"
    echo "* but WITHOUT ANY WARRANTY; without even the implied warranty of         *"
    echo "* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *"
    echo "* GNU General Public License for more details.                           *"
    echo "*                                                                        *"
    echo "* You should have received a copy of the GNU General Public License      *"
    echo "* along with this program.  If not, see <http://www.gnu.org/licenses/>.  *"
    echo "**************************************************************************"
}

function greet_info {
    echo "**************************************************************************"
    echo "* PyNuSMV is now configured for your system                              *"
    echo "* You may run it (ie) as such:                                           *"
    echo "* python3 -m tools.atl.check examples/atl/tictactoe.smv                  *"
    echo "*                                                                        *"
    echo "* The syntax of the properties is dependent on your logic.               *"
    echo "* Here's an example to check ATL, which means that player                *"
    echo "* circle can force a draw                                                *"
    echo "* <'circlep'> F ('finished' & ~ 'won')                                   *"
    echo "**************************************************************************"
    echo "* Press Crtl+<D> in order to leave the configured shell.                 *"
    echo "**************************************************************************"
}

setup_env $(pwd)
license_disclaimer
greet_info
bash
