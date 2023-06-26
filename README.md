<div align="center">

# monkey-py
A Python interpreter for the monkey language from the book `Writing An Interpreter In Go` by `Thorsten Ball`

![](https://img.shields.io/github/last-commit/loenard97/monkey-py?&style=for-the-badge&logo=github&color=3776AB)
![](https://img.shields.io/github/repo-size/loenard97/monkey-py?&style=for-the-badge&logo=github&color=3776AB)

</div>


# The Monkey Language
Monkey is a toy language from the books `Writing An Interpreter In Go` and `Writing A Compiler In Go` by `Thorsten Ball`.
Check out the website [here](https://monkeylang.org/).

It includes some basic datatypes, conditionals and functions:
```
let x = 1;
let string = "Hello World!";
let array = [1, 2, 3];

let func = fn(x, y) {
    return x + y;
};

if (x == 0) {
    true
} else {
    false
}
```

This Implementation contains an Interpreter and a REPL:
```sh
python main.py
>> x = 3
3
```
