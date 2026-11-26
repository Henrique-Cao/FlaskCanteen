import os
from pathlib import Path

pytest_plugins = ["pytester"]


def configure_test_run(pytester, monkeypatch):
    tests_dir = Path(__file__).resolve().parents[1]
    project_dir = tests_dir.parent
    pytester.makeconftest((tests_dir / "conftest.py").read_text(encoding="utf-8"))
    pythonpath = os.pathsep.join(filter(None, (str(project_dir), os.environ.get("PYTHONPATH", ""))))
    monkeypatch.setenv("PYTHONPATH", pythonpath)


def test_summary_counts_outcomes_and_teardown_failure(pytester, monkeypatch):
    configure_test_run(pytester, monkeypatch)
    pytester.makepyfile(
        """
        import pytest

        def test_pass():
            pass

        def test_fail():
            assert False

        @pytest.mark.skip(reason="example")
        def test_skip():
            pass

        @pytest.mark.xfail(reason="example")
        def test_expected_failure():
            assert False

        @pytest.mark.xfail(reason="example")
        def test_unexpected_pass():
            pass

        @pytest.fixture
        def broken_teardown():
            yield
            assert False

        def test_teardown(broken_teardown):
            pass
        """
    )
    result = pytester.runpytest_subprocess("-q")
    assert result.ret == 1
    result.stdout.fnmatch_lines([
        "*Test results: 1/6 passed; 2 failed; 1 skipped; 1 xfailed; 1 xpassed; 0 not completed; 0 collection errors*"
    ])


def test_summary_shows_tests_not_run_after_stop(pytester, monkeypatch):
    configure_test_run(pytester, monkeypatch)
    pytester.makepyfile(
        """
        def test_first():
            assert False

        def test_second():
            pass
        """
    )
    result = pytester.runpytest_subprocess("-q", "-x")
    assert result.ret == 1
    result.stdout.fnmatch_lines([
        "*Test results: 0/2 passed; 1 failed; 0 skipped; 0 xfailed; 0 xpassed; 1 not completed; 0 collection errors*"
    ])


def test_summary_counts_only_selected_tests(pytester, monkeypatch):
    configure_test_run(pytester, monkeypatch)
    pytester.makepyfile(
        """
        def test_chosen():
            pass

        def test_not_chosen():
            pass
        """
    )
    result = pytester.runpytest_subprocess("-q", "-k", "chosen and not not_chosen")
    assert result.ret == 0
    result.stdout.fnmatch_lines(["*Test results: 1/1 passed;*"])


def test_summary_reports_collection_errors(pytester, monkeypatch):
    configure_test_run(pytester, monkeypatch)
    pytester.makepyfile("raise RuntimeError('collection failed')")
    result = pytester.runpytest_subprocess("-q")
    assert result.ret != 0
    result.stdout.fnmatch_lines(["*0 not completed; 1 collection errors*"])


def test_summary_counts_duplicate_test_runs(pytester, monkeypatch):
    configure_test_run(pytester, monkeypatch)
    testfile = pytester.makepyfile("def test_pass(): pass")
    result = pytester.runpytest_subprocess("-q", "--keep-duplicates", str(testfile), str(testfile))
    assert result.ret == 0
    result.stdout.fnmatch_lines(["*Test results: 2/2 passed;*"])
