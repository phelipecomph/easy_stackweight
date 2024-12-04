import json
import warnings
from dataclasses import dataclass
from heapq import nlargest


@dataclass
class SkillStack:
    stack_id: int = None
    json_stack_path: str = "skill_stack.json"
    json_stack_template_path: str = "skill_stack.json.template"
    forget_weight: float = 0.5

    def __post_init__(self):
        if self.stack_id:
            self.load_stack(self.stack_id)
        else:
            self.create_stack()

    def load_stack(self, stack_id):
        """
        Loads an existing stack based on the stack_id.

        Params:
        stack_id : int
            The ID of the stack to be loaded.

        Returns:
        SkillStack
            An instance of SkillStack with the loaded stack.

        Raises:
        IndexError
            If the stack with the specified ID is not found in the JSON file.
        """
        try:
            with open(self.json_stack_path, "r") as f:
                self.stack = json.load(f)[str(stack_id)]

        except KeyError:
            raise IndexError(
                f"Stack of id ({stack_id}) not found on {self.json_stack_path}"
            )

    def create_stack(self):
        """
        Creates a new stack and returns the SkillStack instance.

        Returns:
        SkillStack
            An instance of SkillStack with a new stack created.

        Raises:
        FileNotFoundError
            If the stack template is not found.
        """
        self.stack = {}

    def update(self, weights: dict, decays: dict):
        """
        Updates the stack with new weights, applying the forgetting logic.

        Params:
        weights : dict
            A dictionary where the keys correspond to skills and the values
            are the weights to be added to the stack.
        decays : dict
            TODO
        """
        self._forget(decays)
        self.stack = {
            key: round(self.stack.get(key, 0.0) + weights[key], 2) for key in weights
        }

    def greater(self, n: int = 1):
        """
        Returns the n skills with the highest values in the stack.

        Params:
        n : int, optional
            The number of skills to return. Default is 1.

        Returns:
        list
            A list of the n skills with the highest values.
        """
        return nlargest(n, self.stack, key=self.stack.get)

    def _forget(self, decays):
        """
        Applies the forgetting logic to the skills in the stack,
        reducing their values according to the forgetting weight.
        """
        self.stack = {
            key: self.stack[key] * (1 - decays[key]) for key in self.stack
        }

    def to_jsonfile(self):
        """
        Saves the current stack to the JSON file, updating or creating the entry
        corresponding to the stack_id.

        Raises:
        IOError
            If there is an error trying to open or write to the JSON file.
        """
        with open(self.json_stack_path, "r+") as f:
            stacks = json.load(f)

            stacks[str(self.stack_id)] = self.stack

            f.seek(0)
            json.dump(stacks, f, indent=4)
            f.truncate()
