def f():
    try:
        g()
    except Exception:  # fail-loud.bare-except-ok: detector fixture; the pack must flag this line
        pass
