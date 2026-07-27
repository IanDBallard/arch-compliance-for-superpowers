def f():
    try:
        g()
    except ValueError:
        raise
