#include <gmp.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

#define __align __attribute__((aligned(4096))) __attribute__((noinline))  
#define __maybe_unused __attribute__((unused))
#define unlikely(x) __builtin_expect(!!(x), 0)

#define MAX_K 5

typedef struct large_num_struct{
    union{
        mpz_t data;
        char padding[1 << 12];
    };
} large_num_struct;

large_num_struct __attribute__((aligned(4096))) lookup_table[(1 << MAX_K)];

static inline __attribute__((always_inline)) void mul(mpz_t a,mpz_t b,mpz_t n){
	mpz_mul(a,a,b);
	mpz_mod(a,a,n);
}

int __align exponentiate_k_ary(mpz_t result, mpz_t g, mpz_t e, mpz_t modulus, int k)
{
    int bit_length = mpz_sizeinbase(e,2);
    int window_cardinality = bit_length / k;
    unsigned int window_value;
    int num = (1 << k);

    for (int i = 0; i < num; i++){
    	mpz_init(lookup_table[i].data);
    }
    mpz_set_ui(lookup_table[0].data,1);
    for (int i = 1; i < num; i++){
    	mpz_mul(lookup_table[i].data,lookup_table[i-1].data,g);
    	mpz_mod(lookup_table[i].data,lookup_table[i].data,modulus);
    }

	window_value = 0;
	for (int i = bit_length%k; i > 0; i--){
		window_value<<=1;
		if (mpz_tstbit(e,window_cardinality*k+i-1)){
			window_value|=1;
		}
	}

    mpz_set(result,lookup_table[window_value].data);

	for (int global = window_cardinality-1; global >= 0; --global){
		window_value = 0;
		for (int i = k-1; i >= 0; i--){
			window_value<<=1;
			if (mpz_tstbit(e,(global)*k+i)){
				window_value|=1;
			}
			mul(result,result,modulus);
		}
        mul(result,lookup_table[window_value].data,modulus);
	}

	for (int i = 0; i < num; i++){
		mpz_clear(lookup_table[i].data);
	}

	return 0;
}

int __align main(int argc, char const *argv[])
{
    mpz_t modulus, g, e, result;
	int r, k = 5;

	if (argc != 2) {
        exit(-1);
    }

	mpz_init(modulus);
	mpz_init(g);
	mpz_init(e);
	mpz_init(result);
	//mpz_init(test_res);
	/* you can use this fixed modulus, so you do not need to choose a 1024 bit prime number */
	r = mpz_set_str(modulus, "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
			"29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
			"EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
			"E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
			"EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
			"FFFFFFFFFFFFFFFF", 16);
	assert (r == 0);

	r = mpz_set_str(g, "FEDCBA9876543210FEDCBA9876543210FEDCBA9876543210"
			"FEDCBA9876543210FEDCBA9876543210FEDCBA9876543210"
			"FEDCBA9876543210FEDCBA9876543210FEDCBA9876543210"
			"FEDCBA9876543210FEDCBA9876543210FEDCBA9876543210"
			"FEDCBA9876543210FEDCBA9876543210FEDCBA9876543210"
			"FEDCBA9876543210", 16);
	assert (r == 0);

	mpz_init_set_str(e, argv[1], 16);

	//mpz_powm(test_res,g,e, modulus);
	r = exponentiate_k_ary(result, g, e, modulus, k);

/* 	if (!mpz_cmp(result, test_res)){
		printf("k-ary works properly\n");
	} else {
		printf("k-ary failed\n");
	} */

    // compare results of k-ary and mpz_pow
	return r;
}
