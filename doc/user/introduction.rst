============
Introduction
============


----------
Philosophy
----------

This project is heavily inspired by the wonderful
`Kenneth Reitz <http://www.kennethreitz.org/projects>`__, known for the
`Requests <http://docs.python-requests.org>`__ library, which features an API that is
as beautiful as it is effective. Watching his
`"Documentation is King" talk <http://www.kennethreitz.org/talks/#/documentation-is-king/>`__,
I wanted to make some of the libraries I'm using suitable for human consumption too.

This project is to be developed following the same
`PEP 20 <https://www.python.org/dev/peps/pep-0020/>`__ idioms as
`Requests <http://docs.python-requests.org/en/master/user/intro/#philosophy>`__:

1. Beautiful is better than ugly.
2. Explicit is better than implicit.
3. Simple is better than complex.
4. Complex is better than complicated.
5. Readability counts.

To enable this, the project focuses on one task alone: making it easy to generate a podcast.

-----
Scope
-----

This library does NOT help you publish a podcast, or manage the metadata of your
podcasts. It's just a tool that accepts information about your podcast and
outputs an RSS feed which you can then publish however you want.

Both the process of getting information
about your podcast, and publishing it needs to be done by you. Even then,
it will save you from hammering your head over confusing and undocumented APIs
and conflicting views on how different RSS elements should be used. It also
saves you from reading the RSS specification, the RSS Best Practices and the
documentation for iTunes' Podcast Connect.

PodGen is geared towards developers who aren't super familiar with
RSS and XML. If you know exactly how you want the XML to look, then you're
better off using a template engine like Jinja2 (even if friends don't let
friends touch XML bare-handed). If you just want an easy way to create and
manage your podcasts, use `Podcast Generator <http://www.podcastgenerator.net/>`_.

-------
License
-------
PodGen is licensed under the terms of both the FreeBSD license and the LGPLv3+.
Choose the one which is more convenient for you. For more details, have a look
at license.bsd_ and license.lgpl_.

.. _license.bsd: https://github.com/tobinus/python-podgen/blob/master/license.bsd
.. _license.lgpl: https://github.com/tobinus/python-podgen/blob/master/license.lgpl

