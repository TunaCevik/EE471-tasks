"""
Programming for the Puzzled -- Srini Devadas
You Will All Conform

Input is a list of 'F's and 'B's, in terms of forwards and backwards caps.
Output is a set of commands (printed out) to get either all 'F's or all 'B's.
Fewest commands are the goal.
"""

def please_conform(caps: list[str]) -> None:
    """
    Determines and prints the minimal number of commands needed 
    to make all elements in the array conform to the same direction.
    
    Clean Code Principles Applied:
    1. Space Complexity Optimization: Eliminated the `intervals` list. Because the 
       intervals of 'F' and 'B' alternate, the character that differs from the 
       first element will always constitute a number of intervals less than or 
       equal to the other character. Thus, we only need a single pass and O(1) space.
    2. DRY (Don't Repeat Yourself) & Removed Redundant Logic: Removed the manual 
       counting of forward and backward intervals, as well as the separate end-of-loop 
       interval attachment logic. By treating the end of the array as a conceptual 
       return to the starting character, we unify the interval closing logic.
    3. Descriptive Naming: Variables like `interval_start` make the state clearer.
    4. Type Hinting: Added proper typing for input parameters and return type.
    
    Args:
        caps (list[str]): A list of characters, either 'F' or 'B', representing 
                          the direction of each person's cap.
    """
    if not caps:
        return

    # Let the first person's cap define the "default" direction.
    # The direction differing from the default is guaranteed to have 
    # the minimum (or equal) number of contiguous blocks (intervals).
    default_cap = caps[0]
    interval_start = 0

    # We iterate up to len(caps) inclusive. The simulated element at index len(caps)
    # is set to default_cap to gracefully close any open interval at the end of the list.
    total_people = len(caps)
    for index in range(1, total_people + 1):
        current_cap = caps[index] if index < total_people else default_cap
        previous_cap = caps[index - 1]
        
        if current_cap != previous_cap:
            if current_cap != default_cap:
                # Sequence of caps differing from the default begins
                interval_start = index
            else:
                # Sequence of caps differing from the default ends
                interval_end = index - 1
                if interval_start == interval_end:
                    print(f"Person in position {interval_start} flip your cap!")
                else:
                    print(f"People in positions {interval_start} through {interval_end} flip your caps!")


if __name__ == "__main__":
    caps_list = ['F', 'F', 'B', 'B', 'B', 'F', 'B', 'B', 'B', 'F', 'F', 'B', 'F']
    caps_list_2 = ['F', 'F', 'B', 'B', 'B', 'F', 'B', 'B', 'B', 'F', 'F', 'F', 'F']
    
    print("Testing first caps list:")
    please_conform(caps_list)
    
    print("\nTesting second caps list:")
    please_conform(caps_list_2)
