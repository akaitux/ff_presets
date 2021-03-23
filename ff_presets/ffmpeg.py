import shutil
from subprocess import Popen, PIPE
import logging


def find_ffmpeg_bin():
    ffmpeg_bin = shutil.which('ffmpeg')
    return ffmpeg_bin


def run_ffmpeg(args, timeout=None, overwrite=None):
    cmd = find_ffmpeg_bin()
    if timeout:
        cmd += ' -t {} '.format(timeout)
    if overwrite:
        cmd += ' -y '
    cmd += args
    logging.debug("Exec cmd:\n{}".format(cmd))
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if stdout:
        stdout = stdout.decode('utf-8')
    if stderr:
        stderr = stderr.decode('utf-8')
    logging.debug("EXIT CODE:\n{}".format(p.returncode))
    logging.debug("STDOUT:\n{}".format(stdout))
    logging.debug("STDERR:\n{}".format(stderr))
    return p.returncode, stdout, stderr
