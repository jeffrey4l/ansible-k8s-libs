#!/usr/sbin/env python

import subprocess
import re

'''
secret \"deploy-private-key\" unchanged\n
secret \"deploy-private-key\" created\n
secret \"deploy-private-key\" configured\n
'''

EXAMPLES = '''
- name: create deploy private key
  oc_apply:
    namespace: dev_env
    stdin: "{{ lookup('template', 'deploy-private-key.yaml') }}"

- name: delete test pod
  oc_apply:
    namespace: dev_env2
    stdin: "{{ lookup('template', 'test-pod.yaml') }}"
    state: absent
'''


APPLY_OUTPUT_REG_STR = r'^(?P<resource>\w+) "(?P<name>[^"]+)" (?P<action>\w+)$'
APPLY_OUTPUT_REG = re.compile(APPLY_OUTPUT_REG_STR)


def main():
    specs = dict(
        stdin=dict(type='str'),
        namespace=dict(type='str'),
        state=dict(type='str',
                   choices=['absent', 'present'],
                   default='present')
    )
    module = AnsibleModule(argument_spec=specs,  # noqa
                           supports_check_mode=False)

    cmd = ['oc']
    namespace = module.params.get('namespace')
    if namespace:
        cmd.extend(['--namespace', namespace])
    if module.params.get('state') == 'present':
        cmd.extend(['apply', '-f', '-'])
    else:
        cmd.extend(['delete' '-f', '-'])
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdin = module.params.get('stdin')
    stdout, stderr = p.communicate(input=stdin)
    if p.returncode != 0:
        msg = 'Get failure. error code: %d,\n stdout: %s\n, stderr: %s\n' % (
                p.returncode, stdout, stderr)
        module.fail_json(msg=msg)
    changed = False
    results = []
    for line in stdout.splitlines():
        match = APPLY_OUTPUT_REG.match(line)
        result = match.groupdict()
        results.append(result)
        if result['action'] != 'unchanged':
            changed = True

    module.exit_json(changed=changed,
                     msg=stdout.splitlines())


from ansible.module_utils.basic import *  # noqa
if __name__ == "__main__":
    main()
