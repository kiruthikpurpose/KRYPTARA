/* Waist v1 W1 reference implementation: ac_genesis, ac_step, ac_ack, ac_ctx_digest.
 * Pure: no I/O, no allocation, no clock, no mutable globals, no recursion (scripts/arch_check.py
 * enforces this). Check order for every message, mirrored by models/step_model.py:
 *   1. context initialised            -> AC_E_STATE
 *   2. BOOT is read-only and handled here (no further checks)
 *   3. previous snapshot acknowledged -> AC_E_BUSY
 *   4. field validity                 -> AC_E_BADMSG
 *   5. evidence authorises the action -> AC_E_AUTH
 *   6. action-specific state, budget and admission checks
 *   7. apply, extend the chain, issue one snapshot intent
 * Nothing is modified before step 7, so a rejected message leaves the context unchanged. */
#include "kernel.c"

#define AC_TX_LEN 70u

static void put_u32(uint8_t *o, uint32_t v) {
    o[0] = (uint8_t)v; o[1] = (uint8_t)(v >> 8); o[2] = (uint8_t)(v >> 16); o[3] = (uint8_t)(v >> 24);
}

static ac_status_t reject(ac_effects_t *o, int32_t code) {
    o->n = 1; o->it[0].kind = AC_INT_REJECT; o->it[0].seq = 0; o->it[0].code = code;
    return code;
}

static int admissible(const ac_ctx_t *c, unsigned tier, const ac_tbl_t *t) {
    if (!ac_tbl_monotone(t) || !ac_tbl_is_projected(t, c->present)) return 0;
    if (tier == AC_T0_HALT) return 1;   /* HALT is availability-only and exempt from the safety bound */
    ac_tbl_t U, L;
    const ac_budget_t *b = &c->bud[tier];
    uint32_t xc[AC_MAX_CLASSES] = {0}, xl[AC_MAX_CLASSES] = {0};
    if (b->xc_a != 0xff) xc[b->xc_a] |= 1u << b->xc_b;
    if (b->xl_a != 0xff) xl[b->xl_a] |= 1u << b->xl_b;
    uint8_t absent = (uint8_t)~c->present;
    uint8_t expo = (uint8_t)(ac_expo_from_kinds(c->kinds, c->present) | absent);
    if (ac_tbl_upper(&U, b->fc, b->nfc, b->t, expo, xc)) return 0;
    if (ac_tbl_lower(&L, b->fl, b->nfl, b->s, absent, xl)) return 0;
    return ac_tbl_within(t, &U, &L);
}

static void serialise_tx(uint8_t o[AC_TX_LEN], const ac_msg_t *m) {
    o[0] = m->kind; o[1] = m->action; o[2] = m->evidence; o[3] = m->atom; o[4] = m->bundle; o[5] = m->tier;
    memcpy(o + 6, m->digest, 32);
    for (unsigned i = 0; i < 8; i++) put_u32(o + 38 + 4 * i, m->table.w[i]);
}

ac_status_t ac_ctx_digest(const ac_ctx_t *c, uint8_t out[32]) {
    if (c->version != AC_WAIST_VERSION) return AC_E_STATE;
    for (unsigned i = 0; i < AC_TIER_N; i++)
        if (!ac_tbl_dual_consistent(&c->eng.tier[i])) return AC_E_STATE;
    sha256_ctx h; uint8_t b[4]; sha256_init(&h);
    put_u32(b, c->version); sha256_update(&h, b, 4);
    sha256_update(&h, &c->present, 1); sha256_update(&h, c->kinds, 8); sha256_update(&h, &c->key_present, 1);
    for (unsigned i = 0; i < 8; i++) {
        static const uint8_t zero[32] = {0};
        sha256_update(&h, ((c->key_present >> i) & 1u) ? c->key[i].h : zero, 32);
    }
    for (unsigned t = 0; t < AC_TIER_N; t++)
        for (unsigned i = 0; i < 8; i++) { put_u32(b, c->eng.tier[t].t.w[i]); sha256_update(&h, b, 4); }
    for (unsigned t = 0; t < AC_TIER_N; t++) {
        sha256_update(&h, &c->bud[t].t, 8);   /* t, s, nfc, nfl, xc_a, xc_b, xl_a, xl_b */
        sha256_update(&h, c->bud[t].fc, AC_MAX_CLASSES); sha256_update(&h, c->bud[t].fl, AC_MAX_CLASSES);
    }
    sha256_update(&h, c->action_tier, AC_ACT_N);
    b[0] = (uint8_t)c->halted; b[1] = (uint8_t)(c->halted >> 8); sha256_update(&h, b, 2);
    sha256_update(&h, &c->halt_budget, 1); sha256_update(&h, c->halt_used, 8);
    put_u32(b, c->epoch); sha256_update(&h, b, 4);
    sha256_update(&h, &c->have_commit, 1); sha256_update(&h, c->committed, 32);
    sha256_update(&h, c->head, 32);
    put_u32(b, c->seq); sha256_update(&h, b, 4);
    put_u32(b, c->acked); sha256_update(&h, b, 4);
    sha256_final(&h, out);
    return AC_OK;
}

ac_status_t ac_genesis(ac_ctx_t *c, const ac_genesis_t *g) {
    memset(c, 0, sizeof *c);
    if (g->key_present & ~g->present) return AC_E_ADMIT;
    for (unsigned i = 0; i < 8; i++) {
        if (g->kinds[i] > 3) return AC_E_ADMIT;
        if (((g->key_present >> i) & 1u) && g->kinds[i] != 1) return AC_E_ADMIT;
    }
    for (unsigned t = 0; t < AC_TIER_N; t++) {
        const ac_budget_t *b = &g->bud[t];
        if (b->t > 2 || b->s > 2 || b->nfc > AC_MAX_CLASSES || b->nfl > AC_MAX_CLASSES) return AC_E_ADMIT;
        for (unsigned i = 0; i < AC_MAX_CLASSES; i++) {
            if (i < b->nfc && b->fc[i] == 0) return AC_E_ADMIT;
            if (i < b->nfl && b->fl[i] == 0) return AC_E_ADMIT;
        }
        if ((b->xc_a != 0xff || b->xc_b != 0xff) && !(b->xc_a < b->xc_b && b->xc_b < b->nfc)) return AC_E_ADMIT;
        if ((b->xl_a != 0xff || b->xl_b != 0xff) && !(b->xl_a < b->xl_b && b->xl_b < b->nfl)) return AC_E_ADMIT;
    }
    /* Profile (REQ-TIER-02): HALT is T0; routine actions are T1; re-keying (KEY_INSTALL and
     * INSTALL_TABLE) lives in exactly one T2 tier. */
    /* Every action's tier is pinned individually below, so no separate range check is needed. */
    if (g->action_tier[AC_ACT_HALT] != AC_T0_HALT) return AC_E_ADMIT;
    static const uint8_t t1_actions[] = { AC_ACT_RESUME, AC_ACT_ACTIVATE_IMAGE, AC_ACT_TIGHTEN_TABLE,
                                          AC_ACT_ADVANCE_EPOCH, AC_ACT_RETIRE_SLOT };
    for (unsigned i = 0; i < sizeof t1_actions; i++) if (g->action_tier[t1_actions[i]] != AC_T1_OPERATE) return AC_E_ADMIT;
    uint8_t rk = g->action_tier[AC_ACT_KEY_INSTALL];
    if ((rk != AC_T2_CONST && rk != AC_T2_RECOVERY) || g->action_tier[AC_ACT_INSTALL_TABLE] != rk) return AC_E_ADMIT;

    memcpy(c->kinds, g->kinds, 8);
    c->present = g->present; c->key_present = g->key_present;
    memcpy(c->bud, g->bud, sizeof c->bud);
    memcpy(c->action_tier, g->action_tier, AC_ACT_N);
    for (unsigned i = 0; i < 8; i++) if ((g->key_present >> i) & 1u) c->key[i] = g->key[i];
    for (unsigned i = 0; i < 8; i++) for (unsigned j = i + 1; j < 8; j++)
        if (((g->key_present >> i) & 1u) && ((g->key_present >> j) & 1u) && ac_hash_eq(&c->key[i], &c->key[j])) {
            memset(c, 0, sizeof *c); return AC_E_DUPKEY;
        }
    for (unsigned t = 0; t < AC_TIER_N; t++)
        if (!admissible(c, t, &g->table[t])) { memset(c, 0, sizeof *c); return AC_E_ADMIT; }
    ac_engine_load(&c->eng, g->table);
    c->halt_budget = g->halt_budget;
    /* The chain starts from a commitment to the whole genesis state. */
    c->version = AC_WAIST_VERSION;
    uint8_t d0[32], zero[32] = {0};
    ac_ctx_digest(c, d0);
    static const uint8_t dom[] = "AC1_GENESIS";
    ac_chain_hash(c->head, dom, sizeof dom - 1, zero, d0, 32);
    return AC_OK;
}

ac_status_t ac_ack(ac_ctx_t *c, uint32_t seq) {
    if (c->version != AC_WAIST_VERSION) return AC_E_STATE;
    if (seq != c->seq || c->acked == c->seq) return AC_E_BADMSG;
    c->acked = seq;
    return AC_OK;
}

static unsigned popcount8(unsigned v) { unsigned n = 0; for (; v; v >>= 1) n += v & 1u; return n; }

ac_status_t ac_step(ac_ctx_t *c, const ac_msg_t *m, ac_effects_t *out, size_t *needed) {
    memset(out, 0, sizeof *out);
    if (needed) *needed = AC_MAX_INTENTS;
    if (c->version != AC_WAIST_VERSION) return reject(out, AC_E_STATE);

    if (m->kind == AC_MSG_BOOT) {
        if (!ac_image_bootable(c->committed, m->digest, c->have_commit)) return reject(out, AC_E_IMAGE);
        out->n = 1; out->it[0].kind = AC_INT_BOOT_IMAGE;
        return AC_OK;
    }
    if (c->seq != c->acked) return reject(out, AC_E_BUSY);

    unsigned action;
    if (m->kind == AC_MSG_HALT) action = AC_ACT_HALT;
    else if (m->kind == AC_MSG_PROPOSE_TX && m->action != AC_ACT_HALT && m->action < AC_ACT_N) action = m->action;
    else return reject(out, AC_E_BADMSG);

    unsigned slot = m->atom;
    int is_slot_action = action == AC_ACT_KEY_INSTALL || action == AC_ACT_RETIRE_SLOT;
    int is_bundle_action = action == AC_ACT_HALT || action == AC_ACT_RESUME || action == AC_ACT_ACTIVATE_IMAGE;
    int is_table_action = action == AC_ACT_TIGHTEN_TABLE || action == AC_ACT_INSTALL_TABLE;
    if (action == AC_ACT_HALT || is_slot_action) {
        if (slot >= 8 || !((c->present >> slot) & 1u) || c->kinds[slot] != 1) return reject(out, AC_E_BADMSG);
    }
    if (is_bundle_action && m->bundle >= 16) return reject(out, AC_E_BADMSG);
    if (is_table_action && m->tier >= AC_TIER_N) return reject(out, AC_E_BADMSG);
    if (action == AC_ACT_TIGHTEN_TABLE && m->tier == AC_T0_HALT) return reject(out, AC_E_BADMSG);

    if (!ac_engine_authorise(&c->eng, c->action_tier[action], m->evidence)) return reject(out, AC_E_AUTH);
    if (action == AC_ACT_HALT && !((m->evidence >> slot) & 1u)) return reject(out, AC_E_AUTH);

    uint16_t bundle_bit = m->bundle < 16 ? (uint16_t)(1u << m->bundle) : 0;   /* bundle is only meaningful (and range-checked) for bundle actions */
    switch (action) {
    case AC_ACT_HALT:
        if (c->halted & bundle_bit) return reject(out, AC_E_STATE);
        if (c->halt_used[slot] >= c->halt_budget) return reject(out, AC_E_BUDGET);
        break;
    case AC_ACT_RESUME:
        if (!(c->halted & bundle_bit)) return reject(out, AC_E_STATE);
        break;
    case AC_ACT_ACTIVATE_IMAGE:
        if (c->halted & bundle_bit) return reject(out, AC_E_HALTED);
        break;
    case AC_ACT_TIGHTEN_TABLE:
        if (!admissible(c, m->tier, &m->table) || !ac_tbl_tighten(&m->table, &c->eng.tier[m->tier].t))
            return reject(out, AC_E_ADMIT);
        break;
    case AC_ACT_INSTALL_TABLE:
        if (!admissible(c, m->tier, &m->table)) return reject(out, AC_E_ADMIT);
        break;
    case AC_ACT_KEY_INSTALL:
        if (((c->key_present >> slot) & 1u) && !((m->evidence >> slot) & 1u)) return reject(out, AC_E_HOLDER);
        for (unsigned j = 0; j < 8; j++)
            if (j != slot && ((c->key_present >> j) & 1u) && ac_hash_eq((const ac_key_hash_t *)m->digest, &c->key[j]))
                return reject(out, AC_E_DUPKEY);
        break;
    case AC_ACT_RETIRE_SLOT:
        if (!((c->key_present >> slot) & 1u)) return reject(out, AC_E_STATE);
        if (popcount8((unsigned)(c->key_present & ~(1u << slot))) < (unsigned)c->bud[AC_T1_OPERATE].t + c->bud[AC_T1_OPERATE].s + 1u)
            return reject(out, AC_E_NOCLASS);
        break;
    default: /* ADVANCE_EPOCH */
        break;
    }

    /* Apply. From here nothing can fail. */
    uint8_t tx[AC_TX_LEN];
    serialise_tx(tx, m);
    /* Domain tags with compile-time lengths: a runtime strlen would add a libc dependency. */
    #define TAG(x) { sizeof(x) - 1, x }
    static const struct { uint8_t len; const char *s; } tag[AC_ACT_N] = {
        TAG("AC1_HALT"), TAG("AC1_RESUME"), TAG("AC1_ACTIVATE_IMAGE"), TAG("AC1_TIGHTEN_TABLE"),
        TAG("AC1_ADVANCE_EPOCH"), TAG("AC1_RETIRE_SLOT"), TAG("AC1_INSTALL_TABLE"), TAG("AC1_KEY_INSTALL") };
    switch (action) {
    case AC_ACT_HALT: c->halted |= bundle_bit; c->halt_used[slot]++; break;
    case AC_ACT_RESUME: c->halted &= (uint16_t)~bundle_bit; break;
    case AC_ACT_ACTIVATE_IMAGE: c->have_commit = 1; memcpy(c->committed, m->digest, 32); break;
    case AC_ACT_TIGHTEN_TABLE:
    case AC_ACT_INSTALL_TABLE: ac_tbl_dual_init(&c->eng.tier[m->tier], &m->table); break;
    case AC_ACT_KEY_INSTALL: memcpy(c->key[slot].h, m->digest, 32); c->key_present |= (uint8_t)(1u << slot); break;
    case AC_ACT_RETIRE_SLOT: c->key_present &= (uint8_t)~(1u << slot); memset(c->key[slot].h, 0, 32); break;
    default: c->epoch++; memset(c->halt_used, 0, 8); break;
    }
    uint8_t head[32];
    ac_chain_hash(head, (const uint8_t *)tag[action].s, tag[action].len, c->head, tx, AC_TX_LEN);
    memcpy(c->head, head, 32);
    c->seq++;
    out->n = 1; out->it[0].kind = AC_INT_NV_WRITE_SNAPSHOT; out->it[0].seq = c->seq;
    return AC_OK;
}
