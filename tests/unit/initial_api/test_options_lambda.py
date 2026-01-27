import unittest
import os
import sys
import json
from unittest.mock import patch
folder_to_add = os.path.abspath('aws_developer_sample_project/initial_api') 
sys.path.append(folder_to_add) 

class TestOptions(unittest.TestCase):
      
   def setUp(self):
      import aws_developer_sample_project.initial_api.options as options
      self.options=options

   def test_options(self):
      event={
      }
      answer = self.options.handler(event, None)
      self.assertEqual(answer['statusCode'], 200)



if __name__ == '__main__':
    unittest.main()
