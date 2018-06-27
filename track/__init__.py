from contextlib import contextmanager

from track.trial import Trial
from track.project import Project

# TODO: note that this might get icky when the user
# forks or uses multiple threads. The latter can be
# solved with locking. The former is more annoying, maybe
# it needs some checks that we're in the creation PID.
# TODO: nested trials require that _trial is actually
# a thread-local stack. Def doable but annoying.
_trial = None

@contextmanager
def trial(log_dir="~/ray_results/project_name",
          upload_dir=None,
          sync_period=None,
          trial_prefix="",
          param_map=None):
    """Generates a trial within a with context"""
    global _trial  # pylint: disable=global-statement
    if _trial:
        # TODO: would be nice to stack crawl at creation time to report
        # where that initial trial was created, and that creation line
        # info is helpful to keep around anyway.
        raise ValueError("A trial already exists in the current context")
    local_trial = Trial(
        log_dir=log_dir,
        upload_dir=upload_dir,
        sync_period=sync_period,
        trial_prefix=trial_prefix,
        param_map=param_map)
    try:
        _trial = local_trial
        _trial.start()
        yield
    finally:
        _trial = None
        local_trial.close()

def metric(*, iteration=None, **kwargs):
    """Applies Trial.metric to the trial in the current context."""
    _trial.metric(iteration=iteration, **kwargs)

def artifact(artifact_name, src):
    """Applies Trial.artifact to the trial in the current context."""
    _trial.artifact(artifact_name, src)

__all__ = ["Trial", "Project", "trial"]