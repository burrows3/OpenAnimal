import unittest

from openanimal.agent import LifeAgent
from openanimal.world import WorldSignalStream


class TestLifeAgent(unittest.TestCase):
    def test_birth_has_no_name(self):
        agent = LifeAgent.birth()
        self.assertTrue(agent.animal_id)
        self.assertEqual(agent.phase, "infancy")

    def test_expression_can_happen(self):
        agent = LifeAgent.birth()
        agent.pressure = 1.0
        agent.tolerance = 0.2
        agent.last_expression_tick = -999
        world = WorldSignalStream(seed=1).signals_for_tick(agent.age_ticks)
        output = agent.tick(world)
        self.assertIsNotNone(output)
        self.assertGreaterEqual(len(output), 1)


if __name__ == "__main__":
    unittest.main()
