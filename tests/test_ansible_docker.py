# -*- coding: utf-8 -*-

"""
Basic pytest plugin testing
"""


def test_help_message_without_keys(testdir):
    """
    This plugin makes ssh private and public keys mandatory
    """

    result = testdir.runpytest(
        '--help',
    )

    assert len(result.errlines) > 0
    result.stderr.fnmatch_lines([
        '*--ssh-private-key-path*',
    ])


def test_help_message(testdir):
    """
    Check plugin arguments
    """

    result = testdir.runpytest(
        '--help',
        '--no-logging-overload',
        '--ssh-private-key-path=foo',
        '--ssh-public-key-path=bar'
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'ansible-docker:',
        '*--no-logging-overload',
        '*--ssh-private-key-path=SSH_PRIVATE_KEY_PATH',
        '*--ssh-public-key-path=SSH_PUBLIC_KEY_PATH',
        '*--ansible-limit=ANSIBLE_LIMIT',
        '*--ansible-groups=ANSIBLE_GROUPS',
        '*--no-idempotence-check',
        '*--ansible-idempotence-changed=ANSIBLE_IDEMPOTENCE_CHANGED'
    ])
