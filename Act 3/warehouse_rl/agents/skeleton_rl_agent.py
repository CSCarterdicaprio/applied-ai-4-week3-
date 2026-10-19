#!/usr/bin/env python3
"""
Skeleton Optimization Agent - Template for students to implement optimization algorithms

IMPORTANT: This is NOT an RL agent - it's a template for 
students to implement their own optimization algorithms (greedy, Hungarian, etc.)

This agent currently makes terrible decisions:
- Random staffing decisions
- No layout optimization 
- Ignores order priorities
- No intelligent assignment logic

Students should replace the naive methods with proper optimization algorithms.
"""

import numpy as np
from typing import Dict, Optional
from .standardized_agents import BaselineAgent

class SkeletonOptimizationAgent(BaselineAgent):
    """
    Template for students to implement their own optimization algorithms.
    
    Students should replace the naive methods with:
    - Economic models for staffing decisions
    - Hungarian algorithm for order assignment  
    - Greedy search for layout optimization
    - Multi-objective optimization techniques
    """
    
    def __init__(self, env):
        super().__init__(env)
        self.name = "StudentOptimization"
        
        # Enable unlimited hiring for true economic optimization
        # Disabled unlimited hiring as it causes the system to just endlessly hire people causing unavoidable bankruptcy 
        #self.env._unlimited_hiring = True 
        self.env._unlimited_hiring = False
        
        # Students can add their own state tracking here
        self.performance_metrics = []
        self.decision_history = []
        
        # Students can add algorithm parameters here
        # Example: Hungarian algorithm matrices, greedy search parameters, etc.
        self.staffing_parameters = {
            'hire_threshold_ratio': 3.0,
            'fire_threshold_ratio': 2.0,
            'profit_threshold': 0
        }
        
        # Students can implement adaptive parameters that change based on performance
        self.adaptive_optimization_enabled = False
        
    def reset(self):
        """Reset agent state - students should expand this"""
        self.action_history = []
        self.reward_history = []
        # TODO: Reset any neural network states, replay buffers, etc.
    
    def get_action(self, observation: Dict) -> Dict:
        """
        Generate action based on observation.
        Current implementation is intentionally terrible - students should improve!
        """
        
        # Extract basic info from observation
        current_timestep = observation['time'][0]
        financial_state = observation['financial']  # [profit, revenue, costs, burn_rate]
        queue_info = observation['order_queue']
        employee_info = observation['employees']

        # Track layout performance every 100 steps
        if observation['time'][0] % 100 == 0:
            self.track_layout_performance()
        
        action = {
            'staffing_action': self._get_naive_staffing_action(financial_state, employee_info),
            'layout_swap': self._get_naive_layout_action(current_timestep),
            'order_assignments': self._get_naive_order_assignments(queue_info, employee_info)
        }
        
        # TODO: Students should implement proper action recording for optimization
        self.action_history.append(action.copy())
        
        return action
    
    def _get_naive_staffing_action(self, financial_state, employee_info) -> int:
        """
        WEEK 2 STEP 1: Staffing decisions - students should improve this!
        
        Current problems:
        - Ignores queue length and workload
        - Random decisions regardless of profit
        - No consideration of employee efficiency
        """
        
        # TODO WEEK 2 STEP 1: Students should implement intelligent staffing logic
        # Current approach: Make random decisions based on "vibes"
        
        current_profit = financial_state[0]
        num_employees = np.sum(employee_info[:, 0] > 0)  # Count active employees
        
        # Terrible logic: Random decisions with slight bias
        # BUT: Hire managers more frequently so layout optimization can work
        has_manager = np.any(employee_info[:, 5] == 1)  # Check if we have a manager
        
        if np.random.random() < 0.3:  # 30% chance to hire
            if num_employees < 20:  # Don't go completely overboard
                return 1  # Hire worker
        elif np.random.random() < 0.1:  # 10% chance to fire
            if num_employees > 1:  # Don't fire everyone
                return 2  # Fire worker
        elif np.random.random() < 0.2:  # 20% chance to hire manager (increased from 5%)
            if not has_manager or num_employees > 10:  # Hire manager if we don't have one, or if we have lots of workers
                return 3  # Hire manager
        
        return 0  # No action

    
    
    def _get_naive_layout_action(self, current_timestep) -> list:
        """
        WEEK 1 STEP 1: Layout optimization - students should improve this!
        
        Current problems:
        - Random swaps with no strategic purpose
        - Ignores item co-occurrence patterns
        - No consideration of delivery distances
        - Wastes manager time on pointless moves
        """
        
        # TODO WEEK 1 STEP 1: Students should implement intelligent layout optimization
        # Current approach: Occasionally make random swaps
        #greedy variables for best swaps
        best_overall_swap = None
        max_global_improvement = 0

        #if its not a 100 step skip searching for swaps
        if(current_timestep % 100 != 0 or current_timestep == 0):
            return [0,0]
    
        grid = self.env.warehouse_grid
        item_accessed = self.env.warehouse_grid.item_access_frequency

        #finds the top 25%
        top_items =  np.percentile(item_accessed, 75)
        #makes a list of the index of the items
        items_list_coords = np.where(item_accessed >= top_items)[0].flatten()
        #finds the positions of the shipping bay
        delivery_positions = getattr(grid, 'truck_bay_positions', [(grid.width // 2, grid.height // 2)])

        #loops through the list 
        for current_idx in items_list_coords:
            #make sure current_idx wont crash if not int somehow
            current_idx_int = int(current_idx)

            #coords of the item
            current_x = current_idx_int % grid.width
            current_y = current_idx_int // grid.width
            current_pos = (current_x, current_y)

            #items distance from delivery spot
            current_dist = min(grid.manhattan_distance(current_pos, delivery_pos) 
                    for delivery_pos in delivery_positions)

            #checks distance from delivery spot, if its greater than 3 look for better spot
            if(current_dist > 3):
                #use helper method to find the stuff
                target_idx = self._find_closer_position(current_pos,delivery_positions)
                #checks to see if better position has been found
                if target_idx is not None and target_idx != current_idx_int:
                    # Calculate the distance improvement for this specific item swap
                    #secondary check just in case
                    target_x = int(target_idx) % grid.width
                    target_y = int(target_idx) // grid.width
                    target_dist = min(grid.manhattan_distance((target_x, target_y), delivery_pos) 
                                        for delivery_pos in delivery_positions)
                    
                    #benefit = frequency * distance
                    item_frequency = item_accessed[current_idx_int]
                    item_improvement = item_frequency * (current_dist - target_dist)
                    
                    # Greedy Selection: Track if this item swap is better than previous items checked
                    if item_improvement > max_global_improvement:
                        max_global_improvement = item_improvement
                        #best_overall_swap = {"from": current_idx_int, "to": int(target_idx)}
                        best_overall_swap = [current_idx_int, int(target_idx)]

        # If we found a highly beneficial swap anywhere in the warehouse, this will run it
        if best_overall_swap is not None:
            #debug code tester
            #print(f"--- TIMESTEP {current_timestep}: AGENT ATTEMPTING SWAP FROM INDEX {best_overall_swap[0]} TO {best_overall_swap[1]} ---")
            
            return best_overall_swap
        # Phase 2: If no frequency-based improvement found, try co-occurrence clustering
        if current_timestep % 200 == 0:  # Less frequent than hot-item optimization
            cooccurrence_swap = self._find_cooccurrence_swap()
            if cooccurrence_swap:
                return cooccurrence_swap

        #this is basically like returning None since it makes no change
        return [0,0]

    
        '''if current_timestep % 100 == 0 and np.random.random() < 0.2:  # Random timing
            # Pick two random positions to swap
            grid_size = self.env.grid_width * self.env.grid_height
            pos1 = np.random.randint(0, grid_size)
            pos2 = np.random.randint(0, grid_size)
            return [pos1, pos2]'''

    def _find_closer_position(self, current_pos, delivery_positions):
            """
            Greedy neighborhood search for better item placement.
            
            Algorithm: Exhaustive search of all storage positions to find
            the position that minimizes distance to delivery points.
            
            Returns [current_index, target_index] if beneficial swap found.
            """
            grid = self.env.warehouse_grid
            frequencies = grid.item_access_frequency

            current_idx = current_pos[1] * grid.width + current_pos[0]

            # Safety bound guard for the tracking array size
            if current_idx >= len(frequencies):
                return None
            #Find the index in the normal item list
            current_freq = frequencies[current_idx]
            
            # If the item has never been accessed, moving it provides 0 benefit
            if current_freq <= 0:
                return None
            # calculates distance for current item from the shipping bay
            current_dist = min(grid.manhattan_distance(current_pos, delivery_pos) 
                            for delivery_pos in delivery_positions)
            #greedy search variables
            max_improvement = 0
            best_target_idx = None

            #if the item is outside the list somehow prevent it from crashing
            if current_idx >= len(frequencies):
                return None
            # TODO: Implement exhaustive neighborhood search
            # TODO: Loop through all grid positions (nested for loops over x,y)
            for y in range(grid.height):
                for x in range(grid.width):

                    # TODO: Check if position is a storage cell (grid.cell_types[y, x] == 1)
                    if grid.cell_types[y, x] == 1:

                        candidate_pos = (x, y)
                    
                        if candidate_pos == current_pos:
                            continue

                        # TODO: Calculate distance from candidate position to delivery
                        candidate_dist = min(grid.manhattan_distance(candidate_pos, delivery_pos) 
                                            for delivery_pos in delivery_positions)
                            
                        dist_saved = current_dist - candidate_dist

                        benefit =  current_freq * dist_saved

                        # TODO: Apply greedy selection: choose position with maximum distance improvement
                        # TODO: Require minimum improvement threshold (>1 step closer)    
                        if (benefit > 1) and (benefit > max_improvement):
                            max_improvement = benefit
                            # TODO: Convert 2D coordinates to 1D index for return value
                            # HINT: 1D index = y * grid.width + x
                            best_target_idx = y * grid.width + x

                    
            return best_target_idx

    def _find_cooccurrence_swap(self):
        """
        Greedy clustering algorithm for association-based spatial optimization.
        
        Algorithm: Scan all item pairs for clustering opportunities,
        calculate benefit for each, and greedily select highest-benefit move.
        
        Returns swap that maximizes benefit = co-occurrence_frequency × distance_saved
        """
        grid = self.env.warehouse_grid
        cooccurrence = grid.item_cooccurrence
        
        # Greedy search parameters
        min_cooccurrence = 3      # Minimum frequency threshold
        min_distance = 4          # Minimum distance threshold for clustering
        best_benefit = 0          # Track best benefit found
        best_swap = None          # Track best swap candidate
        
        # TODO: Implement greedy benefit maximization
       
        num_items = cooccurrence.shape[0]

        # TODO: Scan co-occurrence matrix (nested loops: item1, item2 where item1 < item2)
        for item1 in range(num_items):
            for item2 in range(item1 + 1, num_items):
                # TODO: Apply frequency filter (cooccurrence[item1, item2] > min_cooccurrence)
                cooccurrence_count = cooccurrence[item1, item2]
                if cooccurrence_count > min_cooccurrence:
                    
                    # TODO: Get current locations using grid.find_item_locations()
                    locations = grid.find_item_locations()
                    pos1 = locations.get(item1)
                    pos2 = locations.get(item2)
                    
                
                    if pos1 is not None and pos2 is not None:
                        
                        # TODO: Calculate current distance between items
                        current_distance = grid.manhattan_distance(pos1, pos2)
                        # TODO: Apply distance filter (current_distance > min_distance)
                        if current_distance > min_distance:
                            # TODO: Calculate benefit = cooccurrence_count × current_distance
                            benefit = cooccurrence_count * current_distance
                            
                            # TODO: Update best_benefit and best_swap if this benefit is higher
                            if benefit > best_benefit:
                                best_benefit = benefit
                                # Temporarily save the best item pair to optimize
                                best_swap = (item1, item2)
        
        if best_swap is not None:
            locations = grid.find_item_locations()
            pos1 = locations.get(best_swap[0])  # Destination reference point (x, y)
            pos2 = locations.get(best_swap[1])  # The item we want to physically move (x, y)
            
            if pos1 is not None and pos2 is not None:
                # 1D index of the item being moved
                current_idx = pos2[1] * grid.width + pos2[0]
                
                # Pass pos2 as current_pos, and wrap pos1 in a list [pos1] as the target
                # TODO: Find adjacency swap for best pair (call helper method)
                target_idx = self._find_closer_position(pos2, [pos1])
                
                if target_idx is not None and int(target_idx) != int(current_idx):
                    return [int(current_idx), int(target_idx)]
            
        return None  # Return highest-benefit clustering move
        
        #return best_swap  # Return highest-benefit clustering move

    def track_layout_performance(self):
        """
        Performance analysis for greedy layout optimization algorithms.
        
        Measures: 
        - Layout efficiency (frequency-weighted distances)
        - Algorithm convergence (swaps per period)
        - Optimization impact over time
        """
        if not hasattr(self, 'layout_metrics'):
            self.layout_metrics = []
        
        # Calculate current layout efficiency using weighted distance metric
        efficiency = self._calculate_layout_efficiency()
        
        self.layout_metrics.append({
            'timestep': self.env.current_timestep,
            'efficiency': efficiency,
            'total_swaps': len([a for a in self.action_history if a['layout_swap'] != [0, 0]]),
            'phase1_swaps': self._count_frequency_swaps(),#this method did not exist had to make one
            'phase2_swaps': self._count_cooccurrence_swaps()#this method also did not exist had to make one 
        })
        
        # Print progress every 1000 steps
        if self.env.current_timestep % 1000 == 0:
            recent_efficiency = np.mean([m['efficiency'] for m in self.layout_metrics[-10:]])
            print(f"Layout efficiency: {recent_efficiency:.3f}")

    def _calculate_layout_efficiency(self):
        """
        Objective function evaluation for layout quality.
        
        Algorithm: Weighted average distance where weights = access frequency
        Lower weighted distance = higher efficiency (better layout)
        """
        # TODO: Implement frequency-weighted distance calculation   
        grid = self.env.warehouse_grid
        frequencies = grid.item_access_frequency
        
        # TODO: Get item frequencies and delivery positions
        delivery_positions = getattr(grid, 'truck_bay_positions', [(grid.width // 2, grid.height // 2)])
        
        total_weighted_distance = 0.0
        total_frequency = 0.0
        
        max_possible_distance = (grid.width - 1) + (grid.height - 1)
        if max_possible_distance <= 0:
            max_possible_distance = 1.0  

        for current_idx, freq in enumerate(frequencies):
            # TODO: For each item with frequency > 0:
            if freq > 0:
                #       - Get item location
                current_x = current_idx % grid.width
                current_y = current_idx // grid.width
                current_pos = (current_x, current_y)
                
                #       - Calculate distance to nearest delivery
                current_dist = min(grid.manhattan_distance(current_pos, delivery_pos) 
                                   for delivery_pos in delivery_positions)
                
                #       - Weight distance by access frequency
                total_weighted_distance += current_dist * freq
                total_frequency += freq

        
        if total_frequency == 0:
            return 1.0  

        # TODO: Return normalized efficiency score (0-1 scale)
        # HINT: efficiency = 1.0 - (weighted_avg_distance / max_possible_distance)
        weighted_avg_distance = total_weighted_distance / total_frequency

        efficiency = 1.0 - (weighted_avg_distance / max_possible_distance)
        
        return float(np.clip(efficiency, 0.0, 1.0))
        #return 0.5  # Placeholder - implement the weighted distance calculation

    def _count_frequency_swaps(self) -> int:
            """
            Helper metric tracker to resolve the AttributeError.
            Counts how many total layout swaps have been executed by your managers.
            """
            # Access the relocations logs directly from warehouse environment structure
            if hasattr(self.env, 'relocations_history'):
                return len(self.env.relocations_history)
                
            return 0  # Default fallback count if the history list hasn't initialized yet
    
    def _count_cooccurrence_swaps(self) -> int:
            """
            Helper metric tracker to resolve the AttributeError.
            Counts how many clustering swaps occurred on the 200-step windows.
            """
            if hasattr(self.env, 'relocations_history'):
                # Filter relocations to count swaps executed during the clustering window
                return sum(1 for swap in self.env.relocations_history 
                        if swap.get('timestep', 0) % 200 == 0)
                
            return 0  # Fallback if history list hasn't initialized yet
    
    def _get_naive_order_assignments(self, queue_info, employee_info) -> list:
        """
        WEEK 2 STEP 2: Order assignment - students should improve this!
        
        Current problems:
        - Ignores employee locations
        - No consideration of order priority/value
        - Random assignments regardless of efficiency
        - Doesn't check if employees are actually available
        """
        
        # TODO WEEK 2 STEP 2: Students should implement intelligent order assignment
        # Current approach: Random assignments
        
        assignments = [0] * 20  # No assignments by default
        
        # Count how many employees we have (very naive)
        num_employees = int(np.sum(employee_info[:, 0] > 0))
        
        # Randomly assign first few orders to first few employees
        if num_employees > 0:
            for i in range(min(3, num_employees)):  # Only assign 3 orders max
                if np.random.random() < 0.6:  # 60% chance to assign
                    assignments[i] = (i % num_employees) + 1  # Random employee
        
        return assignments
    
    def record_reward(self, reward: float):
        """
        WEEK 3 STEP 1: Reward tracking and learning - students should expand this
        
        TODO WEEK 3 STEP 1: Students should implement:
        - Proper reward tracking
        - Performance analysis
        - Adaptive parameter adjustment
        - Multi-objective optimization
        """
        self.reward_history.append(reward)
        
        # Skeleton optimization - doesn't actually learn anything useful
        if len(self.reward_history) > 10:
            # "Update" weights randomly (this doesn't actually improve performance)
            if reward > 0:
                self.staffing_weights += np.random.randn(4) * 0.01
                self.layout_weights += np.random.randn(3) * 0.01
    
    def should_update_policy(self) -> bool:
        """
        WEEK 3 STEP 2: Policy updates and adaptation - students should improve this
        
        TODO WEEK 3 STEP 2: Students should implement proper update schedules
        """
        return len(self.action_history) % 50 == 0  # Arbitrary update frequency
    
    def get_performance_metrics(self) -> Dict:
        """
        Get agent performance metrics for analysis
        Students can use this to debug their improvements
        """
        if not self.reward_history:
            return {"avg_reward": 0, "total_actions": 0}
        
        return {
            "avg_reward": np.mean(self.reward_history[-100:]),  # Last 100 rewards
            "total_actions": len(self.action_history),
            "exploration_rate": self.exploration_rate,
            "recent_performance": np.mean(self.reward_history[-10:]) if len(self.reward_history) >= 10 else 0
        }


def create_skeleton_optimization_agent(env) -> SkeletonOptimizationAgent:
    """Factory function to create skeleton Optimization agent"""
    return SkeletonOptimizationAgent(env)


# TODO: Students should implement these advanced components:

class StudentOptimizationAgent(SkeletonOptimizationAgent):
    """
    Template for students to implement their improved Optimization agent
    
    Suggested improvements:
    1. Replace random staffing with demand-based hiring
    2. Implement proper layout optimization using item frequencies
    3. Add distance-based order assignment
    4. Implement basic Q-optimization or policy gradients
    5. Add proper exploration vs exploitation balance
    """
    
    def __init__(self, env):
        super().__init__(env)
        self.name = "StudentOptimization"
        
        # TODO: Students implement these
        # self.q_table = {}
        # self.policy_network = SimpleNeuralNetwork()
        # self.experience_buffer = []
        # self.target_network = None
        
    def _get_improved_staffing_action(self, financial_state, employee_info, queue_info):
        """
        WEEK 2 STEP 1: Students implement intelligent staffing:
        - Hire when queue is growing
        - Fire when queue is empty for extended periods
        - Consider profit margins before hiring
        - Balance managers vs workers
        """
        pass
    
    def _get_improved_layout_action(self, observation):
        """
        WEEK 1 STEP 1: Students implement smart layout optimization:
        - Move frequently accessed items closer to delivery
        - Group items that are often ordered together
        - Only optimize when queue is manageable
        - Track swap effectiveness
        """
        pass
    
    def _get_improved_order_assignments(self, queue_info, employee_info):
        """
        WEEK 2 STEP 2: Students implement efficient order assignment:
        - Assign orders to closest available employees
        - Prioritize high-value or urgent orders
        - Consider employee current locations
        - Balance workload across employees
        """
        pass
    
    def learn_from_experience(self, state, action, reward, next_state, done):
        """
        WEEK 3 STEP 3: Students implement multi-objective optimization:
        - Performance trend analysis
        - Adaptive parameter tuning
        - Multi-objective trade-off handling
        - Robust optimization techniques
        """
        pass