import subprocess


class CalledProcessError(Exception):
    def __init__(self, returncode, cmd, stdout, stderr):
        self.returncode = returncode
        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return 'Command %s return non-zero exits status %d' % \
               (self.cmd, self.returncode)


class ResourceNotFound(Exception):

    def __init__(self, message):
        self.message = message


class KubeletBinaryRunner(object):

    KUBELET_BINARY = 'kubelet'

    def __init__(self):
        pass

    def _run_cmd(self, cmd, stdin=None):
        p = subprocess.Popen(cmd,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(input=stdin)

        if p.returncode != 0:
            raise CalledProcessError(p.returncode, cmd, stdout, stderr)

        return stdout, stderr

    def apply(self, namespace, definition=None, definition_file=None):
        cmd = [self.KUBELET_BINARY]
        stdin = None
        if namespace:
            cmd += ['--namespace', namespace]
        cmd += ['apply']
        if definition:
            cmd += ['--filename', '-']
            stdin = definition
        if definition_file:
            cmd += ['--filename', definition_file]
        stdout, stderr = self._run_cmd(cmd, stdin)
        return stdout

    def delete(self, namespace=None, resource_type=None, resource_name=None,
               definition=None, definition_file=None):
        cmd = [self.KUBELET_BINARY]
        stdin = None
        if namespace:
            cmd += ['--namespace', namespace]
        cmd += ['delete']
        if definition:
            cmd += ['--filename', '-']
            stdin = definition
        if definition_file:
            cmd += ['--filename', definition_file]
        try:
            stdout, stderr = self._run_cmd(cmd, stdin)
            return stdout
        except CalledProcessError as ex:
            # When the resource doesn't exist
            # returncode=1
            # stderr='Error from server (NotFound): error when stopping
            # "STDIN": deploymentconfig "echoserver" not found'
            if (ex.returncode == 1 and
                    ex.stderr.find('Error from server (NotFound)') != -1):
                msg = ex.stderr.split(':')[2]
                raise ResourceNotFound(msg)
            else:
                raise


class OCBinaryRunner(KubeletBinaryRunner):
    KUBELET_BINARY = 'oc'


class PythonRunner(object):

    def apply(self):
        pass
