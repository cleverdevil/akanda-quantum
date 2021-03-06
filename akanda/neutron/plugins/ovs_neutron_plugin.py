# Copyright 2014 DreamHost, LLC
#
# Author: DreamHost, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from neutron.plugins.openvswitch import ovs_neutron_plugin

from akanda.neutron.plugins import decorators as akanda
from akanda.neutron.plugins import floatingip

akanda.monkey_patch_ipv6_generator()


class OVSNeutronPluginV2(floatingip.ExplicitFloatingIPAllocationMixin,
                         ovs_neutron_plugin.OVSNeutronPluginV2):
    _supported_extension_aliases = (
        ovs_neutron_plugin.OVSNeutronPluginV2._supported_extension_aliases +
        ["dhportforward", "dhaddressgroup", "dhaddressentry",
         "dhfilterrule", "dhportalias"])

    try:
        _supported_extension_aliases.remove('agent_scheduler')
    except ValueError:
        pass

    @akanda.auto_add_other_resources
    @akanda.auto_add_ipv6_subnet
    def create_network(self, context, network):
        return super(OVSNeutronPluginV2, self).create_network(context, network)

    @akanda.auto_add_subnet_to_router
    def create_subnet(self, context, subnet):
        return super(OVSNeutronPluginV2, self).create_subnet(context, subnet)

    @akanda.sync_subnet_gateway_port
    def update_subnet(self, context, id, subnet):
        return super(OVSNeutronPluginV2, self).update_subnet(
            context, id, subnet)

    def list_routers_on_l3_agent(self, context, agent_id):
        return {
            'routers': self.get_routers(context),
        }

    def list_active_sync_routers_on_active_l3_agent(
            self, context, host, router_ids):
        # Override L3AgentSchedulerDbMixin method
        filters = {}
        if router_ids:
            filters['id'] = router_ids
        routers = self.get_routers(context, filters=filters)
        new_router_ids = [r['id'] for r in routers]
        if new_router_ids:
            return self.get_sync_data(
                context,
                router_ids=new_router_ids,
                active=True,
            )
        return []
