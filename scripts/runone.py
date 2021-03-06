#!/usr/bin/env python

import argparse
import os
import sys

# I want this:
#   ERROR: test_update_and_fetch (mitx.cms.djangoapps.contentstore.tests.test_course_settings.CourseDetailsViewTest)
# to become:
#   test --settings=cms.envs.test --pythonpath=. -s cms/djangoapps/contentstore/tests/test_course_settings.py:CourseDetailsViewTest.test_update_and_fetch

def find_full_path(path_to_file):
    """Find the full path where we only have a relative path from somewhere in the tree."""
    for subdir, dirs, files in os.walk("."):
        full = os.path.relpath(os.path.join(subdir, path_to_file))
        if os.path.exists(full):
            return full

def main(argv):
    parser = argparse.ArgumentParser(description="Run just one test")
    parser.add_argument('--nocapture', '-s', action='store_true', help="Don't capture stdout (any stdout output will be printed immediately)")
    parser.add_argument('words', metavar="WORDS", nargs='+', help="The description of a test failure, like 'ERROR: test_set_missing_field (courseware.tests.test_model_data.TestStudentModuleStorage)'")

    args = parser.parse_args(argv)
    words = []
    # Collect all the words, ignoring what was quoted together, and get rid of parens.
    for argword in args.words:
        words.extend(w.strip("()") for w in argword.split())
    # If it starts with "ERROR:" or "FAIL:", just ignore that.
    if words[0].endswith(':'):
        del words[0]

    test_method = words[0]
    test_path = words[1].split('.')
    if test_path[0] == 'mitx':
        del test_path[0]
    test_class = test_path[-1]
    del test_path[-1]

    test_py_path = "%s.py" % ("/".join(test_path))
    test_py_path = find_full_path(test_py_path)
    test_spec = "%s:%s.%s" % (test_py_path, test_class, test_method)

    settings = None
    if test_py_path.startswith('cms'):
        settings = 'cms.envs.test'
    elif test_py_path.startswith('lms'):
        settings = 'lms.envs.test'

    if settings:
        # Run as a django test suite
        from django.core import management

        django_args = ["django-admin.py", "test", "--pythonpath=."]
        django_args.append("--settings=%s" % settings)
        if args.nocapture:
            django_args.append("-s")
        django_args.append(test_spec)

        print " ".join(django_args)
        management.execute_from_command_line(django_args)
    else:
        # Run as a nose test suite
        import nose.core
        nose_args = ["nosetests"]
        if args.nocapture:
            nose_args.append("-s")
        nose_args.append(test_spec)
        print " ".join(nose_args)
        nose.core.main(argv=nose_args)


if __name__ == "__main__":
    main(sys.argv[1:])
