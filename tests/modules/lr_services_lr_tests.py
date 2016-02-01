import sys
import os
import json

import unittest

sys.path.append(os.path.join('..','..'))
import application.modules.lr_service as sut_service


if __name__ == '__main__':
    sut_service.get_all_courses_from_learning_registry()
    
