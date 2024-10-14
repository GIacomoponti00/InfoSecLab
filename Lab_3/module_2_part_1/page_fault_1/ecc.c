#include "ecc.h"

static void pointdouble(Point *p, Curve *cu);
static void pointaddition(Point *point1, Point *point2, Curve *cu);

static inline __attribute__((always_inline)) void add(mpz_t a, mpz_t b, mpz_t n) {
    mpz_add(a, a, b);
    mpz_mod(a, a, n);
}

static inline __attribute__((always_inline)) void sub(mpz_t a, mpz_t b, mpz_t n) {
    mpz_sub(a, a, b);
    mpz_mod(a, a, n);
}

static inline __attribute__((always_inline)) void mul(mpz_t a, mpz_t b, mpz_t n) {
    mpz_mul(a, a, b);
    mpz_mod(a, a, n);
}

static inline __attribute__((always_inline)) void calc_inv(mpz_t a, mpz_t n, mpz_t inverse) {
    mpz_invert(inverse, a, n);
}

static void __align pointaddition(Point *point1, Point *point2, Curve *cu) {
    mpz_t s, p1, x3, y3;
    if (unlikely(point2->infinity == 1)) {
        return;
    }
    if (unlikely(point1->infinity == 1)) {
        point1->infinity = 0;
        mpz_set(point1->x, point2->x);
        mpz_set(point1->y, point2->y);
        return;
    }
    mpz_init(s);
    if (unlikely(mpz_cmp(point1->x, point2->x) == 0)) {
        mpz_neg(s, point1->y);
        mpz_mod(s, s, cu->p);
        if (mpz_cmp(s, point2->y) == 0) {
            point1->infinity = 1;
            mpz_clear(s);
            return;
        } else {
            pointdouble(point1, cu);
            return;
        }
    }

    mpz_inits(p1, x3, y3, NULL);
    mpz_sub(p1, point2->y, point1->y);
    mpz_sub(s, point2->x, point1->x);
    calc_inv(s, cu->p, s);
    mul(s, p1, cu->p);

    mpz_mul(p1, s, s);
    sub(p1, point1->x, cu->p);
    sub(p1, point2->x, cu->p);
    mpz_set(x3, p1);

    mpz_sub(p1, point1->x, x3);
    mul(p1, s, cu->p);
    mpz_sub(y3, p1, point1->y);

    mpz_mod(y3, y3, cu->p);
    mpz_mod(x3, x3, cu->p);

    mpz_set(point1->x, x3);
    mpz_set(point1->y, y3);
    mpz_clears(s, p1, x3, y3, NULL);
}

static void __align pointdouble(Point *p, Curve *cu) {
    mpz_t s, p1, x3, y3;
    if (mpz_cmp_d(p->y, 0) == 0) {
        p->infinity = 1;
        return;
    }
    mpz_inits(s, p1, x3, y3, NULL);

    mpz_mul(p1, p->x, p->x);
    mpz_mul_ui(p1, p1, 3);
    add(p1, cu->a, cu->p);

    mpz_mul_ui(s, p->y, 2);
    calc_inv(s, cu->p, s);
    mul(s, p1, cu->p);

    //* compute s
    mpz_pow_ui(p1, s, 2);
    sub(p1, p->x, cu->p);
    sub(p1, p->x, cu->p);
    mpz_set(x3, p1);

    mpz_sub(p1, p->x, x3);
    mul(p1, s, cu->p);
    mpz_sub(y3, p1, p->y);

    mpz_mod(y3, y3, cu->p);
    mpz_mod(x3, x3, cu->p);

    mpz_set(p->x, x3);
    mpz_set(p->y, y3);
    mpz_clears(s, p1, x3, y3, NULL);
}

static void __maybe_unused __align doubleandadd(mpz_t factor, Point *ret_p, Curve *cu) {
    mpz_mod(factor, factor, cu->q);
    int range = mpz_sizeinbase(factor, 2);
    Point tmp_p = {.infinity = 0};

    mpz_init_set(tmp_p.x, cu->x);
    mpz_init_set(tmp_p.y, cu->y);
    mpz_init_set(ret_p->x, cu->x);
    mpz_init_set(ret_p->y, cu->y);

    for (int i = range - 2; i >= 0; --i) {
        pointdouble(ret_p, cu);
        if (mpz_tstbit(factor, i)) {
            pointaddition(ret_p, &tmp_p, cu);
        }
    }
}

static int8_t __align *calc_naf_representation(mpz_t exponent, int size){
	mpz_t loop_var;
	mpz_init_set(loop_var,exponent);

	int8_t *naf_array = malloc((size+1) * sizeof(int8_t));

	naf_array[size] = 2;
	
	int8_t x;
	for (int i = 0; i <= size; ++i)
	{
		if (mpz_cmp_ui(loop_var, 0) == 0)break;
		x = (int8_t)mpz_fdiv_ui(loop_var,4);
		switch (x) {
		case 1:
			naf_array[i] = 2 - x;
			mpz_sub_ui(loop_var,loop_var,1);
			break;
		case 3:
			naf_array[i] = 2 - x;
			mpz_add_ui(loop_var,loop_var,1);
			break;
		default:
			naf_array[i] = 0;
		}
		mpz_tdiv_q_ui(loop_var,loop_var,2);
	}	
	//----------------------------------------------------------------------------------
	mpz_clear(loop_var);
	return naf_array;
}

static void __maybe_unused __align naf_exponentiation(mpz_t mul, Point *ret_p, Curve *cu) {
    Point tmp_p = {.infinity = 0}, inverse_p = {.infinity = 0};
	size_t size;
	int8_t *naf_array;

    mpz_mod(mul,mul,cu->q);
	size = mpz_sizeinbase(mul,2);
    naf_array = calc_naf_representation(mul,size);
    if (naf_array[size]==2)
        size--;

    // initialize points
    mpz_init_set(tmp_p.x, cu->x);
    mpz_init_set(tmp_p.y, cu->y);
	mpz_init_set(inverse_p.x,tmp_p.x);
	mpz_init(inverse_p.y);
	mpz_neg(inverse_p.y,tmp_p.y);
	mpz_mod(inverse_p.y,inverse_p.y,cu->p);
    mpz_set(ret_p->x,tmp_p.x);
	mpz_set(ret_p->y,tmp_p.y);
	ret_p->infinity = 0;
    
	for (long i = size-1; i >= 0; --i)
	{
		pointdouble(ret_p, cu);
		if (naf_array[i] == 1) {
			pointaddition(ret_p,&tmp_p,cu);
        } else if (naf_array[i] == -1) {
            __asm__ volatile(".align 4096");
			pointaddition(ret_p,&inverse_p,cu);
            __asm__ volatile(".align 4096");
        }
	}
	// free memory
	free(naf_array);
	mpz_clear(inverse_p.x);
	mpz_clear(inverse_p.y);

}

/*
 * brainpoolP256r1
 */
static void __align initCruve(Curve *a) {
    mpz_init_set_str(a->a, "7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9", 16);
    mpz_init_set_str(a->p, "A9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377", 16);
    mpz_init_set_str(a->b, "26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6", 16);
    mpz_init_set_str(a->q, "A9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7", 16);
    mpz_init_set_str(a->x, "8BD2AEB9CB7E57CB2C4B482FFC81B7AFB9DE27E1E3BD23C23A4453BD9ACE3262", 16);
    mpz_init_set_str(a->y, "547EF835C3DAC4FD97F8461A14611DC9C27745132DED8E545C1D54C72F046997", 16);
}

static void __align free_curve(Curve *a) {
    mpz_clears(a->a, a->p, a->x, a->y, a->b, a->q, NULL);
}

void __align compute_dh_pubkey(Curve *curve, char *privkey) {
    mpz_t factor;
    Point pub_key_point = {.infinity = 0};

    mpz_init_set_str(factor, privkey, 16);
    mpz_inits(pub_key_point.x, pub_key_point.y, NULL);
    mpz_set(pub_key_point.x, curve->x);
    mpz_set(pub_key_point.y, curve->y);
#if DAA
    doubleandadd(factor, &pub_key_point, curve);
#else
    naf_exponentiation(factor, &pub_key_point, curve);
#endif
    gmp_printf("DH Pubkey:\n%ZX\n%ZX\n", pub_key_point.x, pub_key_point.y);
    mpz_clears(factor, pub_key_point.x, pub_key_point.y, NULL);
}

int __align main(int argc, char *argv[]) {
    Curve curve;
    if (argc != 2) {
        exit(-1);
    }
    initCruve(&curve);
    compute_dh_pubkey(&curve, argv[1]);
    free_curve(&curve);
    return 0;
}
