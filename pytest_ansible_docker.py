# -*- coding: utf-8 -*-

"""
Pytest plugin entry point
"""

import logging
import logging.config
import os
import re
import testinfra
import pytest


# Use testinfra to get a handy function to run commands locally
local_command = testinfra.get_backend('local://').get_module('Command')


def pytest_addoption(parser):
    """
    Manage plugin command line arguments
    """

    group = parser.getgroup('ansible-docker')
    group.addoption(
        '--no-logging-overload',
        action='store_true',
        dest='no_logging_overload',
        default=False,
        help='Not overload logging, warning output is unreadeable.'
    )
    group.addoption(
        '--ssh-private-key-path',
        action='store',
        dest='ssh_private_key_path',
        required=True,
        type='string',
        help='Path to SSH private key file path.'
    )
    group.addoption(
        '--ssh-public-key-path',
        action='store',
        dest='ssh_public_key_path',
        required=True,
        type='string',
        help='Path to SSH public key file path.'
    )
    group.addoption(
        '--ansible-limit',
        action='append',
        dest='ansible_limit',
        default=[],
        help='Set the value for ansible-playbook "limit" parameter.'
    )
    group.addoption(
        '--ansible-groups',
        action='append',
        dest='ansible_groups',
        default=[],
        help='Set the value for container groups in Ansible inventory file.'
    )
    group.addoption(
        '--no-idempotence-check',
        action='store_true',
        dest='no_idempotence_check',
        default=False,
        help='Disabled second provision check, with changed value assert.'
    )
    group.addoption(
        '--ansible-idempotence-changed',
        action='store',
        dest='ansible_idempotence_changed',
        type='int',
        default=0,
        help='"changed" value returned by Ansible role idempotence check.'
    )


# Manage logging
@pytest.fixture(scope='module', autouse=True)
def manage_test_logging(request):
    """
    Logger management used with Ansible docker testing
    """

    handler_level = 'WARNING'
    logging_overload = not request.config.option.no_logging_overload

    if request.config.option.verbose == 1:
        handler_level = 'INFO'
    elif request.config.option.verbose > 1:
        handler_level = 'DEBUG'

    if logging_overload:
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': logging_overload,

            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
            },
            'handlers': {
                'default': {
                    'level': handler_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                },
            },
            'loggers': {
                '': {
                    'handlers': ['default'],
                    'level': 'DEBUG',
                    'propagate': True
                }
            }
        })


@pytest.yield_fixture(scope='function', autouse=True)
def newline_before_logging(request):
    """
    Add a new line before logging, more readeable
    """

    is_capture_disabled = request.config.getoption('capture') == 'no'
    is_verbose = request.config.option.verbose > 0

    if is_capture_disabled and is_verbose:
        print
    yield


def pytest_generate_tests(metafunc):
    """
    Overload pytest_generate_tests to set scope and image usage
    """

    if "TestinfraBackend" in metafunc.fixturenames:

        # Lookup "docker_images" marker
        marker = getattr(metafunc.function, "docker_images", None)
        if marker is not None:
            images = marker.args
        else:
            # Default image
            images = ["debian:jessie"]

        # If the test has a destructive marker, we scope TestinfraBackend
        # at function level (i.e. executing for each test). If not we scope
        # at session level (i.e. all tests will share the same container)
        if getattr(metafunc.function, "destructive", None) is not None:
            scope = "function"
        else:
            scope = "session"

        metafunc.parametrize(
            "TestinfraBackend", images, indirect=True, scope=scope)


@pytest.fixture
def AnsibleDockerTestinfraBackend(request):
    """
    Boot and stop a docker image.
    """

    logger = logging.getLogger('container-management')

    # Run a new container. Run in privileged mode, so systemd will start
    docker_id = local_command.check_output(
        "docker run --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro -d -P %s",
        request.param
    )
    logger.info('Test container id: %s', docker_id)

    def teardown():
        """
        Actions to execute on fixture end of life
        """

        local_command.check_output("docker kill %s", docker_id)
        local_command.check_output("docker rm %s", docker_id)
        local_command.check_output("rm /tmp/%s", docker_id)

    # At the end of each test, we destroy the container
    request.addfinalizer(teardown)

    # Get Docker host mapping for container SSH port expose
    host_ssh_port = local_command.check_output(
        "docker inspect --format"
        " '{{ (index (index .NetworkSettings.Ports \"22/tcp\") 0).HostPort }}'"
        " %s" % docker_id)

    # Create inventory file
    _manage_inventory_file(request, docker_id, host_ssh_port)

    # Get container instance
    container = testinfra.get_backend("docker://%s" % docker_id)

    # Add user public key to authorized connection
    _set_authorized_keys(request, container)

    _manage_ansible_provisionning(request, container)

    return container


def _manage_ansible_provisionning(request, container):
    """
    Execute proper ansible command based on command line options
    """

    logger = logging.getLogger('ansible-management')
    do_idempotence_check = not request.config.option.no_idempotence_check
    idempotence_changed = request.config.option.ansible_idempotence_changed
    limit = request.config.option.ansible_limit
    ssh_private_key_path = request.config.option.ssh_private_key_path

    # Install Ansible requirements
    _install_ansible_requirements(container)

    # First role provisionning
    logger.info(' * First role provision: provision testing ...')
    _provision_with_ansible_by_ssh(container, limit, ssh_private_key_path)

    if do_idempotence_check:

        # Second role provisionning: idempotence test
        logger.info(' * Second role provision: idempotence testing ...')
        command = _provision_with_ansible_by_ssh(
                        container, limit, ssh_private_key_path)

        changed_value = re.search(r'changed=(\d+)', command.stdout).group(1)
        assert changed_value in range(idempotence_changed)


def _manage_inventory_file(request, docker_id, host_ssh_port):
    """
    Manage ansible inventory file

    :param docker_id: Testing container ID
    :param host_ssh_port: Docker host mapping for container SSH port expose
    :param LocalCommand: Testinfra LocalCommand fixture with module scope
    :type docker_id: str
    :type host_ssh_port: str
    :type LocalCommand: pytest.fixture
    """

    ansible_version = local_command.check_output('ansible --version')
    is_ansible_v2 = re.match(r'^ansible\s+2.*', ansible_version)
    ansible_prefix = 'ansible_ssh'

    groups = request.config.option.ansible_groups
    groups.append(docker_id)

    if is_ansible_v2:
        ansible_prefix = 'ansible'

    with open('/tmp/{}'.format(docker_id), 'w') as tmp_inventory:
        for group in groups:
            content = ("[{1}]\n{1} {0}_port={2} {0}_host={3} {0}_user=root\n".format(
                ansible_prefix, group, host_ssh_port, '127.0.0.1'))
            tmp_inventory.write(content)


def _set_authorized_keys(request, container):
    """
    Set authorized keys content for root user into container
    """

    ssh_public_key_path = request.config.option.ssh_public_key_path

    with open(ssh_public_key_path) as ssh_public_key_file:
        public_key = ssh_public_key_file.read()
        container.run('mkdir /root/.ssh')
        container.run('echo "%s" > /root/.ssh/authorized_keys' % public_key)

        logger = logging.getLogger('set_authorized_keys')
        logger.debug('Add public SSH key: %s', public_key)


def _install_ansible_requirements(container):
    """
    Install Ansible requirements
    """

    cmd = local_command(
            'test ! -f ./requirements.yml '
            '|| ansible-galaxy install -r ./requirements.yml -p ./roles')

    logger = logging.getLogger('install_ansible_requirements')
    logger.debug('Install Ansible requirements:\n%s', cmd.stdout)

    assert cmd.rc == 0
    return cmd


def _provision_with_ansible_by_ssh(container, limit, ssh_private_key_path):
    """
    Provision the image with Ansible
    """

    limit_arg = '-l ' + container.name

    if limit != []:
        limit_arg = '-l ' + ','.join(limit)

    cmd = local_command(
        "ANSIBLE_SSH_CONTROL_PATH=./%%h-%%r "
        "ANSIBLE_PRIVATE_KEY_FILE={1} "
        "ANSIBLE_HOST_KEY_CHECKING=False "
        "ANSIBLE_SSH_PIPELINING=True "
        "ANSIBLE_ROLES_PATH={2}/../:{2}:{3} "
        "ansible-playbook {4} -i /tmp/{0} ./testing_deployment.yml "
        "-e 'ansible_python_interpreter=\"/usr/bin/env python2.7\"'".format(
            container.name, ssh_private_key_path,
            os.path.dirname(os.getcwd()), os.getcwd(), limit_arg))

    logger = logging.getLogger('provision_with_ansible_by_ssh')
    logger.debug('Ansible provision command:\n%s', cmd.command)
    logger.debug('Execute ansible provision:\n%s', cmd.stdout)

    assert cmd.rc == 0
    return cmd
