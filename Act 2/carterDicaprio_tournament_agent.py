#!/usr/bin/env python
"""
Tournament Agent: CartersAgent
Student: Carter DiCaprio
Generated: 2026-10-05 17:06:43

Evolution Details:
- Generations: 250
- Final Fitness: N/A
- Trained against: Adaptive, Generous Tit-for-Tat, Always Undercut, Random (0.7), Pavlov...

Strategy: climb to the top of the empire state building
"""

from agents import Agent, INVEST, UNDERCUT
import random


class CartersAgent(Agent):
    """
    CartersAgent

    Work till betrayed

    Evolved Genes: [1.0, 0.028378916079617202, 0.44814422774842316, 0.9343990997270166, 1.0, 0.6706252246533523]
    """

    def __init__(self):
        # These genes were evolved through 100 generations
        self.genes = [1.0, 0.028378916079617202, 0.44814422774842316, 0.9343990997270166, 1.0, 0.6706252246533523]

        # Required for tournament compatibility
        self.student_name = "Carter DiCaprio"

        super().__init__(
            name="CartersAgent",
            description="Work till betrayed"
        )

    def choose_action(self) -> bool:
        """
        IMPROVED decision logic - AGGRESSIVE VERSION
        More likely to retaliate, less exploitable
        """

        # First 2 rounds: use initial cooperation gene
        if self.round_num < 2:
            return random.random() < self.genes[0]

        # Calculate memory window
        memory_length = max(1, int(self.genes[4] * 10) + 1)
        recent_history = self.history[-memory_length:]
        cooperation_rate = sum(recent_history) / len(recent_history)
        defection_rate = 1 - cooperation_rate

        # Nice but Firm strategy:
        if defection_rate == 0:
            return INVEST
        elif defection_rate >= .8:
            return UNDERCUT
        else: 
            if cooperation_rate > .6:
                if(self.history[-1] == UNDERCUT):
                    if random.random() < self.genes[3]:
                        return INVEST
                    else:
                        return random.random() > self.genes[2]
                else:
                    return random.random() < self.genes[1]

            else:
                if(self.history[-1]==INVEST):
                    return random.random() < self.genes[1]
                else:
                    if random.random() < self.genes[3]:
                        return INVEST
                    else:
                        return random.random() > self.genes[2]


        # AGGRESSIVE STRATEGY: Higher threshold for cooperation

        # Only cooperate if opponent is VERY cooperative (>80%)
        '''if cooperation_rate > 0.8:
            return random.random() < self.genes[1]  # gene[1] should evolve HIGH

        # If somewhat cooperative (50-80%), be cautious
        elif cooperation_rate > 0.5:
            # Mix of cooperation and defection
            coop_prob = self.genes[1] * (cooperation_rate - 0.5) * 2  # Scale 0-1
            return random.random() < coop_prob

        # If aggressive (<50%), retaliate hard
        else:
            # Mostly defect, with small chance to forgive
            if random.random() < self.genes[3] * 0.3:  # Reduced forgiveness
                return INVEST
            else:
                return UNDERCUT'''



# Convenience function for tournament loading
def get_agent():
    """Return an instance of this agent for tournament use"""
    return CartersAgent()


if __name__ == "__main__":
    # Test that the agent can be instantiated
    agent = get_agent()
    print(f"✅ Agent loaded successfully: {agent.name}")
    print(f"   Genes: {agent.genes}")
    print(f"   Description: {agent.description}")
