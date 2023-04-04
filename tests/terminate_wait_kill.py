"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2023-04-04
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import time


def _terminate_wait_kill(cpi, timeout=3, sleepbefore=None, sleepafter=None):
    """
    :Author: Daniel Mohr
    :Date: 2022-01-13
    """
    if sleepbefore is not None:
        time.sleep(sleepbefore)
    cpi.terminate()
    cpi.wait(timeout=timeout)
    cpi.kill()
    if sleepafter is not None:
        time.sleep(sleepafter)
