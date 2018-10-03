#!/usr/bin/env python3

# Copyright 2017 Brocade Communications Systems LLC.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may also obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

:mod:`port_trunk_area_create_add` - PyFOS util for adding port members to \
        of a portareatrunk-group/ Creating new portareatrunkgroup.
***********************************************************************************
The :mod:`port_trunk_area_create_add` - PyFOS util for adding port members to \
        of a portareatrunk-group/ Creating new portareatrunkgroup.

This module is a standalone script for for adding port members to \
        of a portareatrunk-group/ Creating new portareatrunkgroup.
* Infrastructure options:
    * -L=<login>: Login ID. If not provided, interactive
        prompt will request one.
    * -P=<password>: Password. If not provided, interactive
        prompt will request one.
    * -i=<IP address>: IP address
    * -n=<port name>: <slot>/<port> name of the port
    * -u=<user name>: string name to be assigned to switch
    * -f=<VFID>: VFID or -1 if VF is disabled. If unspecified,
        VFID of 128 is assumed.

* Util scripts options:
    -n,--name=NAME                      Port in slot/port.
    --trunk-index=VALUE                 Trunk-index of the porttrunkarea-group
    --trunk-members=PORTS               Ports in slot/port format to be added
                                        to the group. Eg. "0/1;0/2"

* outputs:
    * Python dictionary content with RESTCONF response data

"""

import pyfos.pyfos_auth as pyfos_auth
from pyfos.pyfos_brocade_fibrechannel_trunk import trunk_area
import pyfos.pyfos_util as pyfos_util
import sys
import pyfos.utils.brcd_util as brcd_util


def _create_add_port_trunk_area(session, trunkObject):
    return trunkObject.post(session)


def main(argv):
    filters = ["trunk_index", "trunk_members_trunk_member"]
    inputs = brcd_util.parse(argv, trunk_area, filters)

    fcObject = inputs['utilobject']
    if fcObject.peek_trunk_index() is None:
        print("Missing options in the commandline:")
        print(inputs['utilusage'])
        sys.exit(1)
    session = brcd_util.getsession(inputs)
    print(fcObject.peek_trunk_members_trunk_member())
    result = _create_add_port_trunk_area(session, fcObject)
    pyfos_util.response_print(result)
    pyfos_auth.logout(session)


if __name__ == "__main__":
    main(sys.argv[1:])