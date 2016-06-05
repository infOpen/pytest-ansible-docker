pytest-ansible-docker
===================================

.. image:: https://travis-ci.org/infOpen/pytest-ansible-docker.svg?branch=master
    :target: https://travis-ci.org/infOpen/pytest-ansible-docker
    :alt: See Build Status on Travis CI

Plugin to manage Ansible roles and plays testing with testinfra, using Docker containers

----

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.


Features
--------

This plugin help to manage Ansible roles and playbook testing with `Docker`_,
`Testinfra`_ and `tox`_.

This plugin is used with my Ansible role template: `ìnfopen_role_template`_.

For each Docker image configured, it:
* create a Docker container on localhost
* import ssh public key to root user account
* create a temporary inventory file
* run one or two provisions (second is used for idempotence testing) using SSH
* execute all tests into the container.

If used with `tox`_, you can manage quicly a matrix based testing:
* `tox`_ manage X `Ansible`_ version
* this plugin help to manage Y Docker systems


Requirements
------------

Some requirements:
* a local docker installation (Why not manage remote Docker install later)
* SSH key pair


Installation
------------

You can install "pytest-ansible-docker" via `pip`_ from `PyPI`_::

    $ pip install pytest-ansible-docker


Usage
-----

I only used this plugin to manage my role testing, locally and on Travis, you
can check `ìnfopen_role_template`_ for example.


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

Distributed under the terms of the `MIT`_ license, "pytest-ansible-docker" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/infOpen/pytest-ansible-docker/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.org/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi
.. _`Ansible`: https://www.ansible.com/
.. _`Docker`: https://www.docker.com/
.. _`Testinfra`: https://github.com/philpep/testinfra
.. _`ìnfopen_role_template`: https://github.com/infOpen/cookiecutter-ansible-role
