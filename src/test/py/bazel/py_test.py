# Copyright 2018 The Bazel Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest
from src.test.py.bazel import test_base


class PyTest(test_base.TestBase):
  """Integration tests for the Python rules of Bazel."""

  def createSimpleFiles(self):
    self.ScratchFile('WORKSPACE')

    self.ScratchFile(
        'a/BUILD',
        [
            'py_binary(name="a", srcs=["a.py"], deps=[":b"])',
            'py_library(name="b", srcs=["b.py"])',
        ])

    self.ScratchFile(
        'a/a.py',
        [
            'import b',
            'b.Hello()',
        ])

    self.ScratchFile(
        'a/b.py',
        [
            'def Hello():',
            '    print("Hello, World")',
        ])

  def testSmoke(self):
    self.createSimpleFiles()
    exit_code, stdout, stderr = self.RunBazel(['run', '//a:a'])
    self.AssertExitCode(exit_code, 0, stderr)
    self.assertTrue('Hello, World' in stdout)

  def testRunfilesSymlinks(self):
    if test_base.TestBase.IsWindows():
      # No runfiles symlinks on Windows
      return

    self.createSimpleFiles()
    exit_code, _, stderr = self.RunBazel(['build', '//a:a'])
    self.AssertExitCode(exit_code, 0, stderr)
    self.assertTrue(os.path.isdir('bazel-bin/a/a.runfiles'))
    self.assertTrue(os.readlink('bazel-bin/a/a.runfiles/__main__/a/a.py')
                    .endswith('/a/a.py'))
    self.assertTrue(os.readlink('bazel-bin/a/a.runfiles/__main__/a/b.py')
                    .endswith('/a/b.py'))


if __name__ == '__main__':
  unittest.main()
