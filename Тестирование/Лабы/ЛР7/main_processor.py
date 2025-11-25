from itertools import combinations


def cluster_test(arr, funcs):
    return [(func[0](arr), func[1](arr)) for func in funcs]


def cluster_driver(arr, funcs):
    results = []

    for i in range(1, len(funcs) + 1):
        for comb in combinations(funcs, i):
            results.append(cluster_test(arr, comb))

    return results

def terminal_driver(arr, funcs):
    return [[res] for res in cluster_test(arr, funcs)]


'''
funcs = ((a, a`), (b, b`), (c, c`))
results =
[
	[(a(arr), a`(arr))],
    [(b(arr), b`(arr))],
    [(c(arr), c`(arr))],
    [
    	(a(arr), a`(arr)),
        (b(arr), b`(arr))
    ],
    [
    	(a(arr), a`(arr)),
        (c(arr), c`(arr))
    ],
    [
    	(b(arr), b`(arr)),
        (c(arr), c`(arr))
    ],
    [
    	(a(arr), a`(arr)),
        (b(arr), b`(arr)),
        (c(arr), c`(arr))
    ]
]
'''
