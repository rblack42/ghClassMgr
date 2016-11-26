Basic Flask App Structure
#########################

Many tutorials on Flask show a simple one file starting point that creates the basic app and sets up simple test to prove FLask is installed. This is the "Hello, World" of Flask. We sill skip that and move straight to a more practical setup.

Application Factories
*********************

Flask creates an "application" that receives web requests and returns some response. The application can be configured using a number of settings, and it is common to use diffrent settings in different deployment situations.

Most Web Applications have three basic depolyments:

    * Development - where code is actually created
    * Staging, where we test the application for possible deployment.
    * Production - where the application is installed ona real public web server

We might have one more setup, for testing!

Here is a basic configuration setup:

..  pylitinclude::  ghcm/config.py
    :linenos:
    :language: python
