import click


@click.group()
def greet():
    """A sample command group."""


@greet.command()
def test():
    """test command

    \b
        a:  line one
        b:  line two

    .. code-block:: text

        \b
        {
            "field1": "value1",
            "field2": "value2"
        }
    """


@greet.command()
def test2():
    """test command

    \b
            zzz
        a:  line one
                aaa
        b:  line two
            sub_b: line three
                aasf
    """
