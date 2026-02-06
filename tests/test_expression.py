import random
import unittest

from openanimal.expression import generate_expression
from openanimal.memory import MemoryStore
from openanimal.world import WorldSignals


class TestExpression(unittest.TestCase):
    def test_expression_constraints(self):
        rng = random.Random(42)
        memory = MemoryStore()
        world = WorldSignals(
            tick=1,
            time_elapsed=60,
            circadian=0.2,
            seasonality=0.1,
            light_level=0.3,
            environmental_noise=0.2,
            randomness=0.5,
        )
        sentences = generate_expression(world, memory, rng)
        self.assertGreaterEqual(len(sentences), 1)
        self.assertLessEqual(len(sentences), 3)
        joined = " ".join(sentences).lower()
        self.assertNotIn("you", joined)
        self.assertNotIn(" i ", f" {joined} ")


if __name__ == "__main__":
    unittest.main()
