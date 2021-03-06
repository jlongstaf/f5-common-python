# Copyright 2016 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from requests import HTTPError


TEST_DESCR = "TEST DESCRIPTION"


def setup_device_group_test(request, bigip, name, partition):
    def teardown():
        try:
            for d in dg.devices_s.get_collection():
                d.delete()
            dg.delete()
        except HTTPError as err:
            if err.response.status_code != 404:
                raise
    request.addfinalizer(teardown)

    dgs = bigip.cm.device_groups
    dg = dgs.device_group
    dg.create(name=name, partition=partition)
    return dg, dgs


class TestDeviceGroup(object):
    def test_device_group_CURDL(self, request, bigip):
        # Create and delete are taken care of by setup
        dg1, dgs = setup_device_group_test(
            request, bigip, name='test-device-group', partition='Common')
        assert dg1.generation > 0
        assert dg1.name == 'test-device-group'

        # Load
        dg2 = bigip.cm.device_groups.device_group.load(
            name=dg1.name, partition=dg1.partition)
        assert dg1.generation == dg2.generation

        # Update
        dg1.update(description=TEST_DESCR)
        assert dg1.generation > dg2.generation
        assert dg1.description == TEST_DESCR

        # Refresh
        dg2.refresh()
        assert dg1.generation == dg2.generation
        assert dg2.description == TEST_DESCR

    def test_add_device(self, request, bigip):
        dg1, dgs = setup_device_group_test(
            request, bigip, name='test-group', partition='Common')
        devices = bigip.cm.devices.get_collection()
        this_device = devices[0]
        d1 = dg1.devices_s.devices.create(
            name=this_device.name, partition=this_device.partition)
        assert len(dg1.devices_s.get_collection()) == 1
        assert d1.name == this_device.name

    def test_sync(self, request, bigip):
        dg1, dgs = setup_device_group_test(
            request, bigip, name='test-group', partition='Common')

        assert dg1.sync() is None

    def test_cm_sync(self, request, bigip):
        dg1, dgs = setup_device_group_test(
            request, bigip, name='test-group', partition='Common')
        assert bigip.cm.sync(dg1.name) is None
