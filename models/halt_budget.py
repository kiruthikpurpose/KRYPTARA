# REQ-HALT-01 (ADR-009): "One custody atom MAY halt one bundle at most h times per epoch; a T1
# RESUME cancels; a halt never lowers a floor." [C]
# Property-based reference model (not the planned TLA+ spec, which is still incomplete -- see
# docs/validation/validation-gates.md GATE-08/SIM-04). This is a small explicit state machine plus
# randomised sequence testing, in the same spirit as models/interval.py's brute-force cross-check:
# it is evidence the THREE stated invariants hold under this state machine's own rules, not a
# replacement for the exhaustive TLA+ check the roadmap still calls for.
import random

class HaltState:
    def __init__(self, h, epoch_len):
        self.h = h                    # max halts per atom per epoch
        self.epoch_len = epoch_len
        self.floor = 0
        self.halted = set()           # bundles currently halted
        self.halt_count = {}          # (atom, epoch) -> count used this epoch

    def epoch_of(self, t):
        return t // self.epoch_len

    def halt(self, atom, bundle, t):
        """Returns True if the halt was accepted (within budget), False if refused."""
        key = (atom, self.epoch_of(t))
        used = self.halt_count.get(key, 0)
        if used >= self.h:
            return False               # budget exhausted for this atom this epoch: refused
        self.halt_count[key] = used + 1
        self.halted.add(bundle)
        return True                    # halting NEVER touches self.floor

    def resume(self, bundle, is_t1):
        """A T1 RESUME cancels a halt; anything less than T1 cannot."""
        if is_t1 and bundle in self.halted:
            self.halted.discard(bundle)
            return True
        return False

    def advance_floor(self, new_floor):
        if new_floor > self.floor:
            self.floor = new_floor

def random_sequence_test(trials=2000, seed=20261109):
    rng = random.Random(seed)
    violations = []
    for trial in range(trials):
        h = rng.randint(1, 4)
        epoch_len = rng.randint(1, 8)
        s = HaltState(h, epoch_len)
        atoms = [f"A{i}" for i in range(rng.randint(1, 4))]
        bundles = [f"B{i}" for i in range(rng.randint(1, 4))]
        floor_before_any_halt = s.floor
        for step in range(rng.randint(5, 60)):
            t = step
            action = rng.choice(["halt", "resume", "advance"])
            if action == "halt":
                atom, bundle = rng.choice(atoms), rng.choice(bundles)
                key = (atom, s.epoch_of(t))
                used_before = s.halt_count.get(key, 0)
                floor_before = s.floor
                accepted = s.halt(atom, bundle, t)
                if accepted and used_before >= s.h:
                    violations.append((trial, "halt accepted past budget", atom, used_before, s.h))
                if s.floor != floor_before:
                    violations.append((trial, "halt changed the floor", atom, bundle))
            elif action == "resume":
                bundle, is_t1 = rng.choice(bundles), rng.random() < 0.7
                was_halted = bundle in s.halted
                floor_before = s.floor
                s.resume(bundle, is_t1)
                if not is_t1 and was_halted and bundle not in s.halted:
                    violations.append((trial, "non-T1 cancelled a halt", bundle))
                if s.floor != floor_before:
                    violations.append((trial, "resume changed the floor", bundle))
            else:
                s.advance_floor(s.floor + rng.randint(0, 2))
        # per-epoch budget must never have been exceeded, checked again at the end over the whole history
        for (atom, epoch), used in s.halt_count.items():
            if used > h:
                violations.append((trial, "end-state budget exceeded", atom, epoch, used, h))
    return violations

if __name__ == "__main__":
    violations = random_sequence_test()
    print(f"REQ-HALT-01 property test: {2000} random sequences, "
          f"{'0 violations' if not violations else f'{len(violations)} VIOLATIONS'}")
    for v in violations[:10]:
        print("  ", v)
    print(f"REQ-HALT-01 failures={len(violations)}")
    if violations:
        raise SystemExit(1)
