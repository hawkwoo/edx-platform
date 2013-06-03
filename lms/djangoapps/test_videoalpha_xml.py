# -*- coding: utf-8 -*-
"""Test for VideoAlpha Xmodule functional logic.
These tests data readed from xml, not from mongo.

We have a ModuleStoreTestCase class defined in
common/lib/xmodule/xmodule/modulestore/tests/django_utils.py.
You can search for usages of this in the cms and lms tests for examples.
You use this so that it will do things like point the modulestore
setting to mongo, flush the contentstore before and after, load the
templates, etc.
You can then use the CourseFactory and XModuleItemFactory as defined in
common/lib/xmodule/xmodule/modulestore/tests/factories.py to create the
course, section, subsection, unit, etc.
"""

import json
import unittest
from mock import Mock
from lxml import etree

from xmodule.videoalpha_module import VideoAlphaDescriptor, VideoAlphaModule
from xmodule.modulestore import Location
from xmodule.tests import test_system
from xmodule.tests.test_logic import LogicTest


class VideoAlphaFactory(object):
    """A helper class to create videoalpha modules with various parameters
    for testing.
    """

    # tag that uses youtube videos
    sample_problem_xml_youtube = """
        <videoalpha show_captions="true"
        youtube="0.75:jNCf2gIqpeE,1.0:ZwkTiUPN0mg,1.25:rsq9auxASqI,1.50:kMyNdzVHHgg"
        data_dir=""
        caption_asset_path=""
        autoplay="true"
        from="01:00:03" to="01:00:10"
        >
            <source src=".../mit-3091x/M-3091X-FA12-L21-3_100.mp4"/>
        </videoalpha>
    """

    @staticmethod
    def create():
        """Method return VideoAlpha Xmodule instance."""
        location = Location(["i4x", "edX", "videoalpha", "default",
                             "SampleProblem{0}".format(1)])
        model_data = {'data': VideoAlphaFactory.sample_problem_xml_youtube}

        descriptor = Mock(weight="1")

        system = test_system()
        system.render_template = lambda template, context: context
        module = VideoAlphaModule(system, location, descriptor, model_data)

        return module


class VideoAlphaModuleTest(LogicTest):
    """Tests for logic of VideoAlpha Xmodule."""

    descriptor_class = VideoAlphaDescriptor

    raw_model_data = {
        'data': '<videoalpha />'
    }

    def test_get_timeframe_no_parameters(self):
        xmltree = etree.fromstring('<videoalpha>test</videoalpha>')
        output = self.xmodule.get_timeframe(xmltree)
        self.assertEqual(output, ('', ''))

    def test_get_timeframe_with_one_parameter(self):
        xmltree = etree.fromstring(
            '<videoalpha start_time="00:04:07">test</videoalpha>'
        )
        output = self.xmodule.get_timeframe(xmltree)
        self.assertEqual(output, (247, ''))

    def test_get_timeframe_with_two_parameters(self):
        xmltree = etree.fromstring(
            '''<videoalpha
                    start_time="00:04:07"
                    end_time="13:04:39"
                >test</videoalpha>'''
        )
        output = self.xmodule.get_timeframe(xmltree)
        self.assertEqual(output, (247, 47079))


class VideoAlphaModuleUnitTest(unittest.TestCase):
    """Unit tests for VideoAlpha Xmodule."""

    def test_videoalpha_constructor(self):
        """Make sure that all parameters extracted correclty from xml"""
        module = VideoAlphaFactory.create()

        # `get_html` return only context, cause we
        # overwrite `system.render_template`
        context = module.get_html()
        expected_context = {
            'track': None,
            'show_captions': 'true',
            'display_name': 'SampleProblem1',
            'id': 'i4x-edX-videoalpha-default-SampleProblem1',
            'end': 3610.0,
            'caption_asset_path': '/static/subs/',
            'source': '.../mit-3091x/M-3091X-FA12-L21-3_100.mp4',
            'streams': '0.75:jNCf2gIqpeE,1.0:ZwkTiUPN0mg,1.25:rsq9auxASqI,1.50:kMyNdzVHHgg',
            'normal_speed_video_id': 'ZwkTiUPN0mg',
            'position': 0,
            'start': 3603.0
        }
        self.assertDictEqual(context, expected_context)
`