#!/usr/bin/env python3

# Copyright © 2018 Broadcom. All rights reserved. The term "Broadcom"
# refers to Broadcom Inc. and/or its subsidiaries.
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

:mod:`switch_config_dump` - PyFOS util for specific config op use case.
***********************************************************************************
The :mod:`switch_config_dump` provides for a specific config op use case.

This module is a stand-alone script that can be used to dump
spreadsheet or JSON encoded switch configuration files into
a timestamped file or directory. The resulting configuration
files can be used to monitor drift or apply to a switch.

The configuration files can be in spreadsheet format or in JSON format.
By default, spreadsheet format is used. Resulting name of the
spreadsheet is given without .<vfid>.xlsx file extension for
--compare option. For JSON format configuration files, --json option
added to --compare option and directory name is given instead.

* Inputs:
    * -L=<login>: Login ID. If not provided, an interactive
        prompt will request one.
    * -P=<password>: Password. If not provided, an interactive
        prompt will request one.
    * -i=<IP address>: IP address.

* Outputs:
    * None

"""

import pyfos.pyfos_auth as pyfos_auth
import pyfos.pyfos_brocade_zone as pyfos_zone
import pyfos.pyfos_brocade_fibrechannel_switch as pyfos_switch
import pyfos.pyfos_brocade_fibrechannel as pyfos_switchfcport
import pyfos.pyfos_brocade_fabric as pyfos_fabric
import pyfos.pyfos_rest_util as pyfos_rest_util
import pyfos.pyfos_util as pyfos_util
import pyfos.pyfos_brocade_fibrechannel_logical_switch as fc_ls
import sys
import pyfos.utils.brcd_util as brcd_util
import json
import os
import switch_config_util
import switch_config_obj
import openpyxl


def usage():
    print("")


def dump_by_vf(session, envelope_name, in_json, vf):
    if vf is 128:
        print("dumping for default switch or non-vf")
    else:
        print("dumping for VFID", vf)

    pyfos_auth.vfid_set(session, vf)

    dir_name = None
    if in_json:
        if vf is 128:
            dir_name = envelope_name
        else:
            dir_name = envelope_name + "." + str(vf)
        try:
            os.stat(dir_name)
        except OSError:
            os.mkdir(dir_name)
    else:
        wb = openpyxl.Workbook()

    for obj in switch_config_obj.objects_to_process:
        writer = None
        if in_json:
            switch_config_util.dump_object_in_json(session, obj["obj_name"], dir_name)
        else:
            if "writer" in obj:
                writer = obj["writer"]
            else:
                writer = switch_config_util.write_simple_object
            writer(session, obj["obj_name"], wb)

    if not in_json:
        file_name = None
        if vf == 128:
            file_name = envelope_name + ".xlsx"
        else:
            file_name = envelope_name + "." + str(vf) + ".xlsx"
        wb.save(filename=file_name)


def main(argv):
    valid_options = ["json", "compare"]
    inputs = brcd_util.generic_input(argv, usage, valid_options)

    session = pyfos_auth.login(inputs["login"], inputs["password"],
                               inputs["ipaddr"], inputs["secured"],
                               verbose=inputs["verbose"])
    if pyfos_auth.is_failed_login(session):
        print("login failed because",
              session.get(pyfos_auth.CREDENTIAL_KEY)
              [pyfos_auth.LOGIN_ERROR_KEY])
        usage()
        sys.exit()

    brcd_util.exit_register(session)

    vfid = None
    if 'vfid' in inputs:
        vfid = inputs['vfid']

    if vfid is not None:
        pyfos_auth.vfid_set(session, vfid)

    in_json = False
    if 'json' in inputs:
        in_json = inputs['json']

    envelope_name = switch_config_util.get_envelope_name(inputs['ipaddr'])

    result = fc_ls.fibrechannel_logical_switch.get(session)
    if pyfos_util.is_failed_resp(result):
        dump_by_vf(session, envelope_name, in_json, 128)
    else:
        for switch in result:
            dump_by_vf(session, envelope_name, in_json, switch.peek_fabric_id())

    print("done")

    pyfos_auth.logout(session)


if __name__ == "__main__":
    main(sys.argv[1:])
