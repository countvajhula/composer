Install for Development
=======================

.. code-block:: bash

  pip install -e .[dev]

Install in Production
=====================

TODO

Running Tests
=============

Refer to the Makefile for all things related to the development workflow. E.g.

.. code-block:: bash

  make test

Drafting a Release
==================

.. code-block:: bash

  # increment the version
  bumpversion [major|minor|patch]
  # push new release tag upstream
  git push --follow-tags
