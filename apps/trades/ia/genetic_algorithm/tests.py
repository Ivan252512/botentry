from django.test import TestCase
from .ag import (
    Individual
)

import random

# Genetic Algorithm tests

class IndividualTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length = None
        self.mutation_intensity = None
        self.individual = None
        
    def setUp(self):
        self.length = random.randint(0, 1000)
        self.mutation_intensity = random.randint(0, 1000)
        self.individual = Individual(self.length, self. mutation_intensity)
                 
    def test_generate_individual(self):
        self.assertIsNotNone(self.length)
        self.assertIsNotNone(self.mutation_intensity)
        self.assertIsNotNone(self.individual)
        