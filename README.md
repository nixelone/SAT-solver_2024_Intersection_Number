# Description

The SAT solver used is [Glucose](https://www.labri.fr/perso/lsimon/research/glucose/), more specifically [Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1). The source code is compiled using

```
cmake .
make
```

This example contains a compiled UNIX binary of the Glucose solver. For optimal experience, we encourage the user to compile the SAT solver themselves. Note that the solver, as well as the Python script, are assumed to work on UNIX-based systems. In case you prefer using Windows, we recommend to use WSL.

Note that the provided encoding for the intersection number problem is not the only existing encoding. Usually, there are several equivalent encodings one might use. Choosing the encoding is up to the user based on experience and experiments.

Also note, that the intersection number problem is an optimization problem (i.e. try to solve it in as few steps as possible), however, SAT is a decision problem, therefore, we transfer the intersection number problem into a decision problem for a specific number of moves (i.e. is there a solution with this many moves?). To find the minimum number of moves, one has to solve a sequence of decision problems with a different number of moves allowed.

# Documentation

## Problem description

Given a group of sets, these sets have a specific intersection graph. In this graph each set is a vertex and there is an edge between two vertices if the sets representing them have an element in common. The intersection number is the smallest number of unique elements that from all the sets that would still produce the same intersection graph. The intersection number problem is trying to find this number.

An example of a valid input format is:

```
2
a 2 1
a b
b 3 4
```

where number 2 on the first line is the intersection number that we test for. On each next line is one set with elements of this set are separated by a whitespace " ". 

## Encoding

Each unique element is of the sets is represented by one variable starting from 1. In the order they are presented in the input. After that there is one unique variable for each subset of the elements that is of size of the tested intersection number.

Clauses:

Each subset variable implies that the variables representing the elements in this subest are true and that the variables that represent the element that are not in this subset are false.

At leas one of the subset variables is true.

At most one of the subset variables is true.

## User documentation


Basic usage: 
```
sliding_puzzle.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}]
```

Command-line options:

* `-h`, `--help` : Show a help message and exit.
* `-i INPUT`, `--input INPUT` : The instance file. Default: "input.in".
* `-o OUTPUT`, `--output OUTPUT` : Output file for the DIMACS format (i.e. the CNF formula).
* `-s SOLVER`, `--solver SOLVER` : The SAT solver to be used.
*  `-v {0,1}`, `--verb {0,1}` :  Verbosity of the SAT solver used.

## Example instances

* `input-2by2.in`: A 2x2 instance solvable in two steps.
* `input-2by2-unsat.in`: An unsolvable 2x2 instance.
* `input-3by3-unsat.in`: An unsolvable 3x3 instance (5 steps, the instance is solvable in 6 steps)
* `input-3by3.in`: An easy, solvable 3x3 instance
* `input-4by4.in`: An easy, solvable 3x3 instance
* `input-4by4-hard.in`: A solvable instance that takes approximately 18s to solve on our machine
