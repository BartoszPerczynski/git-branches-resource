import sys
import subprocess
import unittest

from unittest.mock import patch
from assets.run_check import main


class TestRunCheck(unittest.TestCase):
    @patch('subprocess.run')
    @patch('subprocess.Popen')
    def test_successful_subprocess_execution(self, mock_popen, mock_run):
        # Given concourse has valid setup
        payload = '{"source": {"uri": "aoldershaw/git-branches-resource.git"}}'

        mock_run.return_value = subprocess.CompletedProcess(
            args=['git', 'ls-remote', '--heads', 'aoldershaw/git-branches-resource.git'],
            returncode=0,
            stdout=b'84d690a3cae703984ac5044179f3b498dc21fe4c\trefs/heads/main',
            stderr=b''
        )
        mock_popen.return_value = subprocess.Popen(
            ['bash', 'run_check.sh', payload],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        sys.argv = ['run_check.py', payload]

        # When we run the branches resource check
        with patch('sys.stdout') as mock_stdout, patch('sys.stderr') as mock_stderr:
            main()

        # Then we return a formatted list of branches
        mock_run.assert_called_once_with(
            ['git', 'ls-remote', '--heads', 'aoldershaw/git-branches-resource.git'],
            stdout=subprocess.PIPE
        )
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_stdout.write.call_count, 2)
        self.assertEqual(mock_stderr.write.call_count, 0)
        self.assertRegex(mock_stdout.write.call_args_list[0][0][0], r'^\[')

    @patch('subprocess.run')
    @patch('subprocess.Popen')
    def test_failed_subprocess_execution(self, mock_popen, mock_run):
        # Given we are
        mock_run.return_value = subprocess.CompletedProcess(
            args=['git', 'ls-remote', '--heads', 'example.git'],
            returncode=1,
            stdout=b'',
            stderr=b'fatal: not a git repository'
        )

        payload = '{"source": {"uri": "example.git"}}'
        # When we call git to get remote branches
        mock_popen.return_value = subprocess.Popen(
            ['bash', 'run_check.sh', payload],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        sys.argv = ['run_check.py', payload]

        # Then assert that check fails and subprocess raises exception
        with self.assertRaises(subprocess.CalledProcessError):
            main()


if __name__ == '__main__':
    unittest.main()
