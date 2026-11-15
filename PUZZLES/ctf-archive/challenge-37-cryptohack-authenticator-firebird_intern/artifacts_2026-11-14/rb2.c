/* Proper rainbow tables (position-dependent salts) for firebird authenticator.
 * password space: 6 distinct chars from 62 -> M = 44261653680.
 * T(pw) = blake3(pw[6] || "HANDSHAKE_FROM_SERVER" || 16*0x00)  (challenge_client = zeros)
 * step functions f_i(x) = unrank(le64(blake3(x || "RBSTEP-i" || 16*0))%M), i = pos mod K.
 * chain from start rank s: c0 = unrank(s*L); c_{p+1} = f_{p mod K}(c_p), p = 0..L-1.
 * endpoint key E(c_L) = blake3(c_L || "RBEND000" || 16*0)[:16]; store (E, start).
 * lookup round r: cur0 = unrank(t0 mod M); walk w=0..L-1: check E(cur); advance with
 *   f_{(r+1+w) mod K}; on hit (start q, walk w): j = L-1-w; cand = advance j steps (f_{p mod K})
 *   from unrank(q*L); accept iff T(cand)==t0. Run r=0..K-1 for full coverage.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include "blake3.h"

static clock_t g_t0 = 0;

static const char ALPHA[62] = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
#define M 44261653680ULL
#define L (1u << 11)
#define K 2048
#define NSTART (uint64_t)(M / L)   /* 5398150 */

static void unrank62(uint64_t idx, char* pw) {
    static const uint64_t bases[6] = {713897640ULL, 11703240ULL, 195054ULL, 3306ULL, 57ULL, 1ULL};
    char avail[62];
    memcpy(avail, ALPHA, 62);
    int navail = 62;
    for (int i = 0; i < 6; i++) {
        uint64_t d = idx / bases[i];
        idx %= bases[i];
        pw[i] = avail[d];
        memmove(avail + d, avail + d + 1, navail - d - 1);
        navail--;
    }
    pw[6] = 0;
}

static uint64_t rank62(const char* pw) {
    static const uint64_t bases[6] = {713897640ULL, 11703240ULL, 195054ULL, 3306ULL, 57ULL, 1ULL};
    char avail[62];
    memcpy(avail, ALPHA, 62);
    int navail = 62;
    uint64_t r = 0;
    for (int i = 0; i < 6; i++) {
        int d = 0;
        while (avail[d] != pw[i]) d++;
        r += (uint64_t)d * bases[i];
        memmove(avail + d, avail + d + 1, navail - d - 1);
        navail--;
    }
    return r;
}

static void b3(const char* pw, const char* tag, uint8_t* out, size_t want) {
    uint8_t buf[64];
    memcpy(buf, pw, 6);
    memcpy(buf + 6, tag, 8);
    memset(buf + 14, 0, 16);
    blake3_hasher hh;
    blake3_hasher_init(&hh);
    blake3_hasher_update(&hh, buf, 30);
    blake3_hasher_finalize(&hh, out, want);
    (void)want;
}

static void target_h(const char* pw, uint8_t* out) { /* out 32 */
    uint8_t buf[64];
    memcpy(buf, pw, 6);
    memcpy(buf + 6, "HANDSHAKE_FROM_SERVER", 21);
    memset(buf + 27, 0, 16);
    blake3_hasher hh;
    blake3_hasher_init(&hh);
    blake3_hasher_update(&hh, buf, 43);
    blake3_hasher_finalize(&hh, out, 32);
}

static const char STEPTAGS[8][9] = {
    "RBSTEP-0","RBSTEP-1","RBSTEP-2","RBSTEP-3","RBSTEP-4","RBSTEP-5","RBSTEP-6","RBSTEP-7"
};

/* salted REDUCTIONS (hash stays T): R_i(h) = unrank(le64(h) ^ SALTS[i]) % M */
static uint64_t SALTS[K];
static void init_salts(void) {
    for (int i = 0; i < K; i++) SALTS[i] = 0x5BD1E9914B0A5B23ULL * (uint64_t)(i + 1);
}

static void end_h(const char* pw, uint8_t* out) { b3(pw, "RBEND000", out, 32); }

static uint64_t le64(const uint8_t* p) {
    uint64_t v = 0;
    for (int i = 7; i >= 0; i--) v = (v << 8) | p[i];
    return v;
}

static void step_k(const char* pw, char* out, int k) {
    uint8_t h[32];
    target_h(pw, h);
    unrank62((le64(h) ^ SALTS[k]) % M, out);
}

/* advance from pw n steps using f_{p mod K} starting at position p0 */
static void advance(char* pw, uint32_t n, uint32_t p0) {
    char nxt[8];
    for (uint32_t i = 0; i < n; i++) {
        step_k(pw, nxt, (int)((p0 + i) % K));
        memcpy(pw, nxt, 8);
    }
}

typedef struct { uint64_t erank; uint32_t start; uint32_t pad; } Entry; /* 16 bytes */

static int cmp_entry(const void* a, const void* b) {
    const Entry* x = (const Entry*)a; const Entry* y = (const Entry*)b;
    if (x->erank != y->erank) return (x->erank < y->erank) ? -1 : 1;
    return (x->start < y->start) ? -1 : (x->start > y->start);
}

typedef struct { Entry* tab; long n; uint32_t HSZ; uint32_t shift; int32_t* hidx; } Index;

static void index_build(Index* ix) {
    ix->HSZ = 1;
    ix->shift = 64;
    while (ix->HSZ < (uint32_t)ix->n * 4) { ix->HSZ <<= 1; ix->shift--; }
    ix->hidx = (int32_t*)malloc((size_t)ix->HSZ * sizeof(int32_t));
    for (uint32_t z = 0; z < ix->HSZ; z++) ix->hidx[z] = -1;
    for (long z = 0; z < ix->n; z++) {
        uint64_t k0 = ix->tab[z].erank * 0x9E3779B97F4A7C15ULL;
        uint32_t slot = (uint32_t)(k0 >> ix->shift);
        uint32_t probes = 0;
        while (ix->hidx[slot] >= 0) { slot = (slot + 1) & (ix->HSZ - 1); if (++probes > 1000000) { fprintf(stderr, "CLUSTER at z=%ld slot=%u\n", z, slot); fflush(stderr); exit(3);} }
        ix->hidx[slot] = (int32_t)z;
    }
}

static long index_probe(const Index* ix, uint64_t erank) {
    uint64_t k0 = erank * 0x9E3779B97F4A7C15ULL;
    uint32_t slot = (uint32_t)(k0 >> ix->shift);
    while (ix->hidx[slot] >= 0) {
        long z = ix->hidx[slot];
        if (ix->tab[z].erank == erank) return z;
        slot = (slot + 1) & (ix->HSZ - 1);
    }
    return -1;
}

static void index_load(Index* ix, const char* path) {
    FILE* f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "no table %s\n", path); exit(2); }
    fseek(f, 0, SEEK_END); long sz = ftell(f); rewind(f);
    fprintf(stderr, "loading %ld bytes\n", sz); fflush(stderr);
    ix->n = sz / sizeof(Entry);
    ix->tab = (Entry*)malloc((size_t)sz);
    if (fread(ix->tab, sizeof(Entry), (size_t)ix->n, f) != (size_t)ix->n) { fprintf(stderr,"short read\n"); exit(2); }
    fclose(f);
    fprintf(stderr, "read done, indexing %ld\n", ix->n); fflush(stderr);
    index_build(ix);
    fprintf(stderr, "index done\n"); fflush(stderr);
}

/* try to recover pw with T(pw)==t0. returns 1 and writes pw8 on success. */
static int lookup_full(const Index* ix, const uint8_t* t0, char* pw8) {
    char cur[8];
    uint64_t h0 = le64(t0);
    for (int r = 0; r < K; r++) {
        if (getenv("RBDEBUG") && (r % 128) == 0) {
            fprintf(stderr, "round %d (%ld ms)\n", r, (long)(clock()-g_t0)*1000/CLOCKS_PER_SEC);
            fflush(stderr);
        }
        unrank62((h0 ^ SALTS[r]) % M, cur);
        uint8_t e[32];
        for (uint32_t w = 0; w < L; w++) {
            long z = index_probe(ix, rank62(cur));
            if (z >= 0) {
                uint32_t j = (uint32_t)(L - 1 - w);
                char cand[8];
                unrank62((uint64_t)ix->tab[z].start * L, cand);
                advance(cand, j, 0);
                uint8_t tt[32];
                target_h(cand, tt);
                if (memcmp(tt, t0, 32) == 0) {
                    memcpy(pw8, cand, 7); pw8[7] = 0;
                    return 1;
                }
            }
            step_k(cur, cur, (int)((r + 1 + w) % K));
        }
    }
    return 0;
}

int main(int argc, char** argv) {
    init_salts();
    if (argc > 3 && strcmp(argv[1], "gen") == 0) {
        uint64_t lo = strtoull(argv[2], 0, 10);
        uint64_t hi = strtoull(argv[3], 0, 10);
        const char* out = argv[4];
        FILE* f = fopen(out, "wb");
        Entry en;
        char pw[8], nxt[8];
        for (uint64_t s = lo; s < hi; s++) {
            unrank62(s * L, pw);
            for (uint32_t p = 0; p < L; p++) {
                step_k(pw, nxt, (int)(p % K));
                memcpy(pw, nxt, 8);
            }
            en.erank = rank62(pw);
            en.start = (uint32_t)s;
            en.pad = 0;
            fwrite(&en, sizeof(Entry), 1, f);
        }
        fclose(f);
        return 0;
    }
    if (argc > 3 && strcmp(argv[1], "sort") == 0) {
        const char* in = argv[2]; const char* out = argv[3];
        FILE* f = fopen(in, "rb");
        fseek(f, 0, SEEK_END); long sz = ftell(f); rewind(f);
        long n = sz / sizeof(Entry);
        Entry* tab = (Entry*)malloc((size_t)sz);
        if (fread(tab, sizeof(Entry), (size_t)n, f) != (size_t)n) { fprintf(stderr,"short\n"); return 2; }
        fclose(f);
        qsort(tab, (size_t)n, sizeof(Entry), cmp_entry);
        FILE* g = fopen(out, "wb");
        fwrite(tab, sizeof(Entry), (size_t)n, g);
        fclose(g);
        fprintf(stderr, "sorted %ld entries\n", n);
        return 0;
    }
    if (argc > 2 && strcmp(argv[1], "lookup") == 0) {
        uint8_t t0[32];
        for (int i = 0; i < 32; i++) { unsigned v; sscanf(argv[2] + 2*i, "%2x", &v); t0[i] = (uint8_t)v; }
        Index ix; index_load(&ix, argv[3]);
        char pw8[8];
        g_t0 = clock();
        clock_t c0 = g_t0;
        int ok = lookup_full(&ix, t0, pw8);
        fprintf(stderr, "lookup: %s (%ld ms)\n", ok ? "FOUND" : "not found", (long)(clock()-c0)*1000/CLOCKS_PER_SEC);
        if (ok) { printf("%s\n", pw8); return 0; }
        return 1;
    }
    if (argc > 3 && strcmp(argv[1], "selftest") == 0) {
        /* selftest table rounds [0,K): pick random pw, compute T, lookup with round r only? */
        const char* tpath = argv[2];
        int ntest = atoi(argv[3]);
        uint32_t only_round = (argc > 4) ? (uint32_t)atoi(argv[4]) : 99;
        Index ix; index_load(&ix, tpath);
        uint8_t rnd[8];
        int found = 0, tested = 0;
        srand((unsigned)time(0));
        for (int t = 0; t < ntest; t++) {
            char pw[8], nxt[8];
            /* random distinct pw: random rank */
            uint64_t idx = ((uint64_t)rand() << 34) ^ ((uint64_t)rand() << 24) ^ ((uint64_t)rand() << 14) ^ ((uint64_t)rand() << 4) ^ (uint32_t)rand();
            idx %= M;
            unrank62(idx, pw);
            uint8_t t0[32]; target_h(pw, t0);
            char cur[8]; unrank62(le64(t0) % M, cur);
            /* walk all rounds; but to test coverage per round, replicate lookup_full */
            char got[8];
            int ok = 0;
            uint64_t h0 = le64(t0);
            for (uint32_t r = 0; r < K && !ok; r++) {
                if (only_round < K && r != only_round) continue;
                unrank62((h0 ^ SALTS[r]) % M, cur);
                uint8_t e[32];
                for (uint32_t w = 0; w < L; w++) {
                    long z = index_probe(&ix, rank62(cur));
                    if (z >= 0) {
                        uint32_t j = (uint32_t)(L - 1 - w);
                        char cand[8];
                        unrank62((uint64_t)ix.tab[z].start * L, cand);
                        advance(cand, j, 0);
                        uint8_t tt[32]; target_h(cand, tt);
                        if (memcmp(tt, t0, 32) == 0) { memcpy(got, cand, 7); got[7]=0; ok = 1; }
                    }
                    if (ok) break;
                    step_k(cur, cur, (int)((r + 1 + w) % K));
                }
            }
            (void)nxt; (void)rnd;
            tested++;
            if (ok) {
                found++;
                if (strcmp(got, pw) != 0) { printf("MISMATCH got=%s want=%s\n", got, pw); return 3; }
                printf("t%d OK pw=%s\n", t, pw);
            } else {
                printf("t%d MISS pw=%s\n", t, pw);
            }
            fflush(stdout);
        }
        printf("selftest: %d/%d recovered\n", found, tested);
        return 0;
    }
    if (argc > 2 && strcmp(argv[1], "serve") == 0) {
        Index ix; index_load(&ix, argv[2]);
        fprintf(stderr, "ready %ld\n", ix.n); fflush(stderr);
        char line[256];
        while (fgets(line, sizeof(line), stdin)) {
            line[strcspn(line, "\r\n")] = 0;
            if (!line[0]) continue;
            uint8_t t0[32];
            for (int i = 0; i < 32; i++) { unsigned v; sscanf(line + 2*i, "%2x", &v); t0[i] = (uint8_t)v; }
            char pw8[8];
            int ok = lookup_full(&ix, t0, pw8);
            if (ok) printf("%s\n", pw8); else printf("MISS\n");
            fflush(stdout);
        }
        return 0;
    }
    fprintf(stderr, "usage: rb2 gen lo hi out | rb2 sort in out | rb2 lookup t0 table | rb2 serve table | rb2 selftest table n [round]\n");
    return 2;
}
