Flask Test Driven Development
#############################

..  include::   /references.inc

One problem with |TDD| is finding a way to get started. In this project, I am
using Python in a virtual environment. It seems appropriate to verify that we
are properly running in that environment as our first test. 

Checking the VirtualEnv Setup
*****************************

On my system, there is an environment variable set to point to the directory
where Python can be found. Since I set up a virtualenv for eahc project, and
name the folder containing all the Python files, all we need to do to verify
that things are running well is to verify that the project directory *venv*
folder matches the one registered in the environment, and that the Python
executable we are running is in that folder. Here is the needed test code:

..  pylitinclude::  tests/test_venv.py
    :linenos:
    :language: python

Testing URLs
************

Once we start development of the FLask app, we will be setting up a server that can return data to a browser. A simple test of this server is that is returns a proper response codes when a request is received. Here is a simple test that checks the return code for a home page request:

..  pylitinclude::  tests/test_urls.py
    :linenos:
    :language: python



