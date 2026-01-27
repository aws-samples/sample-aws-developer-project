import unittest
import os
import sys
import json
import moto

folder_to_add = os.path.abspath('aws_developer_sample_project/core_api') 
sys.path.append(folder_to_add) 

@moto.mock_aws
class TestOptions(unittest.TestCase):
      
   def setUp(self):
      import aws_developer_sample_project.core_api.options as options
      self.options=options

   def test_options(self):
      event={
      }
      answer = self.options.handler(event, None)
      self.assertEqual(answer['statusCode'], 200)



if __name__ == '__main__':
    unittest.main()
