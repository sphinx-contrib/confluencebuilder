"""
This is a module docstring
"""

class Hello(object):
    """
    This is a Hello class docstring
    """

    def __init__(self, name, name2):
        """
        This is an __init__ method docstring.
        Creates a new :class:`Hello` instance.
        :param name: name for the hello
        :param name2: name2 for the hello
        :param name3: name3 for the hello
        :type name: str
        """
        self.name = name

    def say_hello(self):
        """
        This is a say_hello method decorator
        """
        print ('Hello %s' % self.name)

    def foo(self, arg1, arg2):
        """
        A method's docstring with parameters and return value.

        Use all the cool Sphinx capabilities in this description, e.g. to give
        usage examples ...

        :Example:

        >>> another_class.foo('', AClass())

        :param arg1: first argument
        :type arg1: string
        :param arg2: second argument
        :type arg2: :class:`module.AClass`
        :return: something
        :rtype: string
        :raises: TypeError
        """
        return '' + 1
