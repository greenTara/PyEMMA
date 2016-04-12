# This file is part of PyEMMA.
#
# Copyright (c) 2016 Computational Molecular Biology Group, Freie Universitaet Berlin (GER)
#
# PyEMMA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import time

class _ProgressIndicatorCallBack(object):
    def __init__(self):
        self.time = 0.0

    def waiting(self):
        now = time.time()
        if now - self.time < .2:
            return True
        else:
            self.time = now
            return False


class _IterationProgressIndicatorCallBack(_ProgressIndicatorCallBack):
    def __init__(self, reporter, description, stage):
        super(_IterationProgressIndicatorCallBack, self).__init__()
        reporter._progress_register(10, description, stage=stage)
        self.stage = stage
        self.reporter = reporter

    def __call__(self, *args, **kwargs):
        if self.waiting(): return
        self.reporter._prog_rep_progressbars[self.stage].denominator = kwargs['maxiter']
        self.reporter._progress_update(1, stage=self.stage)


class _ConvergenceProgressIndicatorCallBack(_ProgressIndicatorCallBack):
    def __init__(self, reporter, stage, maxiter, maxerr):
        description =  str(stage) + ' error={err:0.1e}/{maxerr:0.1e} iteration={iteration_step}/{maxiter}'
        super(_ConvergenceProgressIndicatorCallBack, self).__init__()
        self.final = -np.log10(maxerr)
        reporter._progress_register(int(self.final), description, stage=stage)
        reporter._prog_rep_progressbars[stage].denominator = self.final
        reporter._prog_rep_progressbars[stage].template = '{desc:.60}: {percent:3d}% ({fraction}) {bar} {spinner}'
        self.stage = stage
        self.reporter = reporter
        self.state = 0.0

    def __call__(self, *args, **kwargs):
        if self.waiting(): return
        current = -np.log10(kwargs['err'])
        if current > 0.0 and current <= self.final and current >= self.state:
            difference = current - self.state
            self.reporter._progress_update(difference, stage=self.stage, show_eta=False, **kwargs)
            self.state = current
        else:
            self.reporter._progress_update(0, stage=self.stage, show_eta=False, **kwargs)