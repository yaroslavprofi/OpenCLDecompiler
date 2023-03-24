class ExecCondition:
    def __init__(self, and_chain):
        self.and_chain = and_chain

    def __and__(self, other: str) -> 'ExecCondition':
        return ExecCondition([other] + self.and_chain[:])

    def __or__(self, other: 'ExecCondition') -> 'ExecCondition':
        return ExecCondition(self.and_chain[1:])

    def __xor__(self, other: 'ExecCondition') -> 'ExecCondition':
        longer = self if len(self.and_chain) > len(other.and_chain) else other
        return ExecCondition(["~" + longer.and_chain[0]] + longer.and_chain[1:])

    def top(self) -> str:
        if self.and_chain:
            return self.and_chain[0]
        return ""
