#ifndef ___ECC_FUNCTIONS___
#define ___ECC_FUNCTIONS___
#include <gmp.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define DAA 1

#define __align __attribute__((aligned(4096))) __attribute__((noinline))  
#define __maybe_unused __attribute__((unused))
#define unlikely(x) __builtin_expect(!!(x), 0)

/*
 * Curve holds all data related to the curve.
 */
typedef struct Curve {
    mpz_t p;
    mpz_t a;
    mpz_t b;
    mpz_t x;
    mpz_t y;
    mpz_t q;

} Curve;

/*
 * Point describes a point on the curve.
 */
typedef struct Point {
    mpz_t x, y;
    int infinity;
} Point;

void compute_dh_pubkey(Curve *curve, char *privkey);

#endif
