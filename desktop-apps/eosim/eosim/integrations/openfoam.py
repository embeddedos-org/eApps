# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""OpenFOAM CFD integration.

Case management, solver execution, result parsing.
"""
import subprocess
import shutil
import os
import re
from typing import Optional, Dict, List


class OpenFOAMRunner:
    """Run OpenFOAM CFD solvers and parse results.

    Manages case directories, executes solvers (simpleFoam, icoFoam, etc.),
    and parses field results.
    """

    SOLVERS = ['simpleFoam', 'icoFoam', 'pisoFoam', 'pimpleFoam',
               'potentialFoam', 'rhoSimpleFoam']

    def __init__(self, case_dir: str = ''):
        self.case_dir = case_dir
        self.solver = 'simpleFoam'
        self._process: Optional[subprocess.Popen] = None
        self._results: Dict[str, list] = {}
        self._log: str = ''
        self._converged = False

    @staticmethod
    def available() -> bool:
        for solver in ['simpleFoam', 'icoFoam']:
            if shutil.which(solver) is not None:
                return True
        return False

    def set_case(self, case_dir: str):
        self.case_dir = case_dir

    def set_solver(self, solver: str):
        if solver in self.SOLVERS:
            self.solver = solver

    def validate_case(self) -> List[str]:
        errors = []
        if not self.case_dir or not os.path.isdir(self.case_dir):
            errors.append('Case directory does not exist: %s' % self.case_dir)
            return errors
        required = ['system/controlDict', 'system/fvSchemes',
                    'system/fvSolution', 'constant']
        for req in required:
            path = os.path.join(self.case_dir, req)
            if not os.path.exists(path):
                errors.append('Missing: %s' % req)
        return errors

    def run(self, timeout: int = 300) -> dict:
        result = {
            'success': False, 'solver': self.solver,
            'case_dir': self.case_dir, 'log': '', 'converged': False,
        }
        if not self.available():
            result['log'] = 'OpenFOAM not installed'
            return result

        errors = self.validate_case()
        if errors:
            result['log'] = 'Case validation failed:\n' + '\n'.join(errors)
            return result

        solver_path = shutil.which(self.solver)
        if not solver_path:
            result['log'] = 'Solver not found: %s' % self.solver
            return result

        try:
            proc = subprocess.run(
                [solver_path, '-case', self.case_dir],
                capture_output=True, text=True, timeout=timeout,
                cwd=self.case_dir,
            )
            self._log = proc.stdout + proc.stderr
            result['log'] = self._log[-2000:]
            result['success'] = proc.returncode == 0

            if 'FOAM FATAL ERROR' in self._log:
                result['success'] = False
            if 'End' in self._log or 'Finalising' in self._log:
                result['converged'] = True
                self._converged = True

        except subprocess.TimeoutExpired:
            result['log'] = 'Solver timed out after %ds' % timeout
        except FileNotFoundError:
            result['log'] = 'Solver binary not found'

        return result

    def parse_residuals(self) -> Dict[str, List[float]]:
        residuals: Dict[str, List[float]] = {}
        pattern = re.compile(
            r'Solving for (\w+),.*Initial residual = ([0-9.e+-]+)')
        for line in self._log.split('\n'):
            m = pattern.search(line)
            if m:
                field = m.group(1)
                val = float(m.group(2))
                residuals.setdefault(field, []).append(val)
        self._results = residuals
        return residuals

    def get_field_data(self, field: str, time_step: str = 'latest') -> dict:
        if not self.case_dir:
            return {}
        if time_step == 'latest':
            time_dirs = []
            for d in os.listdir(self.case_dir):
                try:
                    float(d)
                    time_dirs.append(d)
                except ValueError:
                    pass
            if not time_dirs:
                return {}
            time_step = sorted(time_dirs, key=float)[-1]

        field_path = os.path.join(self.case_dir, time_step, field)
        if not os.path.exists(field_path):
            return {'error': 'Field file not found: %s' % field_path}

        return {
            'field': field,
            'time_step': time_step,
            'path': field_path,
            'size_bytes': os.path.getsize(field_path),
        }

    def get_status(self) -> dict:
        return {
            'available': self.available(),
            'case_dir': self.case_dir,
            'solver': self.solver,
            'converged': self._converged,
            'results_fields': list(self._results.keys()),
        }
