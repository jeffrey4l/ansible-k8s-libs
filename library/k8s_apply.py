#!/usr/sbin/env python

import re
from ansible.module_utils import k8s_runner

'''
secret \"deploy-private-key\" unchanged\n
secret \"deploy-private-key\" created\n
secret \"deploy-private-key\" configured\n
'''

EXAMPLES = '''
- name: create deploy private key
  oc_apply:
    namespace: dev_env
    definition: "{{ lookup('template', 'deploy-private-key.yaml') }}"

- name: delete test pod
  oc_apply:
    namespace: dev_env2
    definition: "{{ lookup('template', 'test-pod.yaml') }}"
    state: absent
'''


APPLY_OUTPUT_REG_STR = r'^(?P<resource>\w+) "(?P<name>[^"]+)" (?P<action>\w+)$'
APPLY_OUTPUT_REG = re.compile(APPLY_OUTPUT_REG_STR)


class KubernetesApply(object):

    def __init__(self, namespace=None, resource_type=None, resource_name=None,
                 definition=None, definition_file=None):
        self.namespace = namespace
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.definition = definition
        self.definition_file = definition_file

        self.runner = k8s_runner.OCBinaryRunner()

        # used by kubernetes module
        self.changed = False
        self.message = ''

    def create(self):
        stdout = self.runner.apply(self.namespace, definition=self.definition)
        self.message = stdout
        for line in stdout.splitlines():
            match = APPLY_OUTPUT_REG.match(line)
            result = match.groupdict()
            if result['action'] != 'unchanged':
                self.changed = True

    def delete(self):
        try:
            stdout = self.runner.delete(self.namespace,
                                        definition=self.definition)
            self.message = stdout
            self.changed = True
        except k8s_runner.ResourceNotFound as ex:
            self.changed = False
            self.message = ex.message


def main():
    specs = dict(
        namespace=dict(type='str'),
        resource_type=dict(type='str'),
        resource_name=dict(type='str'),
        definition=dict(type='str'),
        definition_file=dict(type='str'),
        state=dict(type='str',
                   choices=['absent', 'present'],
                   default='present')
    )
    module = AnsibleModule(argument_spec=specs,  # noqa
                           supports_check_mode=False)

    namespace = module.params.get('namespace', None)
    definition = module.params.get('definition', None)

    manager = KubernetesApply(namespace=namespace,
                              definition=definition)

    if module.params.get('state') == 'present':
        manager.create()
    else:
        manager.delete()

    module.exit_json(changed=manager.changed,
                     msg=manager.message)


from ansible.module_utils.basic import *  # noqa
if __name__ == "__main__":
    main()
