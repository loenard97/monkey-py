let fib = fn(x) {
	if (x == 0) {
		return 0;
	}
	if (x == 1) {
		return 1;
	return fib(x-1) + fib(x-2);
}

let x = 5;
return fib(x);
