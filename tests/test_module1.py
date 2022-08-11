# Test module 1

import pytest
from package.module1 import class1


def test_class1():

    assert class1().name == "class1"