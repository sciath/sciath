""" Utility classes """


class DotDict(dict):  #pylint: disable=too-many-instance-attributes
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
