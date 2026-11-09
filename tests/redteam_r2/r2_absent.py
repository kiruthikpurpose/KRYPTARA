# R2: absent atoms are excluded from compromise sets -> latent single-key authority after re-key. [C]
# Also: proof-by-test that adding absent atoms to every compromise set (the fix) never changes Lo or
# interval non-emptiness, so the fix is free for liveness.
import random, sys, itertools
sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)),"..","..","models"))
from lint import ATOMS, ALL, OPERATE, RECOVERY, structures, N
from interval import upper, lower

def up(seeds):
    return sum(1 << m for m in range(256) if any((s & ~m) == 0 for s in seeds))
def admit(f, U, Lo):
    mono = all(not (f >> m) & 1 or all((f >> (m | 1 << i)) & 1 for i in range(8)) for m in range(256))
    return mono and (f & ~U) == 0 and (Lo & ~f) == 0

ESC1, WIT = 1 << 4, 1 << 7
# 1. Group ESC is lost; slots retired -> absent. Budget as THEORY T1: 1-safe, live vs 1 loss.
present = ALL - {"ESC1", "ESC2"}
Ac, Al, *_ = structures(ATOMS, present, 1, 1, loss_kinds=("SIG", "PRES"))
U, Lo = upper(N, Ac), lower(N, Al)
print(f"[1] ESC absent: T1-budget interval non-empty = {(Lo & ~U) == 0}; installed OPERATE still live = {(Lo & ~OPERATE) == 0}")
_a, _l, *_ = structures(ATOMS, present, 1, 2, loss_labels={"group", "family"}, exclude_loss_combo=[("family:H1", "family:H2")])
print(f"[1b] ESC absent: claimed T2 budget (1-safe, 2 losses) interval non-empty = {(lower(N,_l) & ~upper(N,_a)) == 0}")
# T1's own budget becomes unsatisfiable after a group retirement: what does the device do? Use T2 budget instead:
Ac2, Al2, *_ = structures(ATOMS, present, 1, 1, loss_labels={"group", "family"})   # T2 budget must shrink after a retirement (see [1b])
U2, Lo2 = upper(N, Ac2), lower(N, Al2)
f_bad = RECOVERY | up([ESC1 | WIT])          # T2 'widen tables': adds "ESC1 + log" as an authorising set
print(f"[2] widened T2 table with {{ESC1,WIT}} admitted while ESC absent: {admit(f_bad, U2, Lo2)}")
# 2. Later, T2 're-key lost groups' installs a new ESC1/ESC2 key. Re-evaluate with ESC present:
Ac3, *_ = structures(ATOMS, ALL, 1, 0)
U3 = upper(N, Ac3)
print(f"[3] after re-key, table still safe vs 1 compromise: {(f_bad & ~U3) == 0}; "
      f"ESC1 key + free WIT authorises: {bool((f_bad >> (ESC1 | WIT)) & 1)}")
# 3. Fix: treat absent atoms as attacker-available (add to every compromise set)
absent = (1 << 4) | (1 << 5)
U2fix = upper(N, [a | absent for a in Ac2])
print(f"[4] FIX (absent added to compromise sets): widened table admitted = {admit(f_bad, U2fix, Lo2)}; "
      f"original RECOVERY still admitted = {admit(RECOVERY, U2fix, Lo2)}")
# 4. The fix never changes non-emptiness: A|absent|L == A|L because absent is in every L.
random.seed(5); diff = 0; trials = 0
for _ in range(20000):
    n = 8; P = 255
    absent = random.randrange(256) & random.randrange(256)
    Ac = [random.randrange(256) & ~absent for _ in range(random.randint(1, 6))]
    Al = [random.randrange(256) | absent for _ in range(random.randint(1, 6))]
    U, Lo = upper(n, Ac), lower(n, Al)
    Uf = upper(n, [a | absent for a in Ac])
    trials += 1
    diff += (((Lo & ~U) == 0) != ((Lo & ~Uf) == 0))
print(f"[5] random structures={trials}: non-emptiness changed by the fix in {diff} cases")
# 5. Companion rule: when atoms become absent, project every table onto present atoms,
#    f'(S) = f(S & present). This is a tightening (monotone f), keeps Lo (seeds avoid absent atoms).
absent = (1 << 4) | (1 << 5); pres_mask = 255 & ~absent
def project(f): return sum(1 << m for m in range(256) if (f >> (m & pres_mask)) & 1)
Rp = project(RECOVERY)
print(f"[6] projected RECOVERY: tightening={(Rp & ~RECOVERY) == 0}, admitted under FIX={admit(Rp, U2fix, Lo2)}; "
      f"projected widened table admitted under FIX={admit(project(f_bad), U2fix, Lo2)}")
