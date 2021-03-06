# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Nicole Thomas <nicole@saltstack.com>`
'''

# Import Python Libs
import os

# Import Salt Libs
import integration
from salt.config import cloud_providers_config

# Import Salt Testing Libs
from salttesting import skipIf
from salttesting.helpers import ensure_in_syspath, expensiveTest

ensure_in_syspath('../../../')

# Import Third-Party Libs
try:
    import libcloud  # pylint: disable=W0611
    HAS_LIBCLOUD = True
except ImportError:
    HAS_LIBCLOUD = False


@skipIf(HAS_LIBCLOUD is False, 'salt-cloud requires >= libcloud 0.13.2')
class RackspaceTest(integration.ShellCase):
    '''
    Integration tests for the Rackspace cloud provider using the Openstack driver
    '''

    def setUp(self):
        '''
        Sets up the test requirements
        '''
        super(RackspaceTest, self).setUp()

        # check if appropriate cloud provider and profile files are present
        profile_str = 'rackspace-config:'
        provider = 'rackspace'
        providers = self.run_cloud('--list-providers')
        if profile_str not in providers:
            self.skipTest(
                'Configuration file for {0} was not found. Check {0}.conf files '
                'in tests/integration/files/conf/cloud.*.d/ to run these tests.'
                .format(provider)
            )

        # check if api key, user, and tenant are present
        path = os.path.join(integration.FILES,
                            'conf',
                            'cloud.providers.d',
                            provider + '.conf')
        config = cloud_providers_config(path)
        user = config['rackspace-config']['openstack']['user']
        tenant = config['rackspace-config']['openstack']['tenant']
        api = config['rackspace-config']['openstack']['apikey']
        if api == '' or tenant == '' or user == '':
            self.skipTest(
                'A user, tenant, and an api key must be provided to run these '
                'tests. Check tests/integration/files/conf/cloud.providers.d/{0}.conf'
                .format(provider)
            )

    @expensiveTest
    def test_instance(self):
        '''
        Test creating an instance on rackspace with the openstack driver
        '''
        name = 'rackspace-testing'

        # create the instance
        instance = self.run_cloud('-p rackspace-test {0}'.format(name))
        ret = '        {0}'.format(name)

        # check if instance with salt installed returned successfully
        try:
            self.assertIn(ret, instance)
        except AssertionError:
            self.run_cloud('-d {0} --assume-yes'.format(name))
            raise

        # delete the instance
        delete = self.run_cloud('-d {0} --assume-yes'.format(name))
        ret = '            True'
        try:
            self.assertIn(ret, delete)
        except AssertionError:
            raise

    def tearDown(self):
        '''
        Clean up after tests
        '''
        name = 'rackspace-testing'
        query = self.run_cloud('--query')
        ret = '        {0}:'.format(name)

        # if test instance is still present, delete it
        if ret in query:
            self.run_cloud('-d {0} --assume-yes'.format(name))


if __name__ == '__main__':
    from integration import run_tests
    run_tests(RackspaceTest)
