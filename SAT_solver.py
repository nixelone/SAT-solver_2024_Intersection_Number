from ast import NotIn
from mailbox import NoSuchMailboxError
import subprocess
from argparse import ArgumentParser
import itertools
from xml.etree.ElementTree import tostring

def load_instance(input_file_name):
    # read the input instance
    # the instance is the intersection number we want to check for and then the sets, each set on one line
    # element of the set can be any string
    global INTERSECTION_NUMBER_TO_CHECK
    sets = []
    with open(input_file_name, "r") as file:
        INTERSECTION_NUMBER_TO_CHECK = int(next(file))       # second line is the intersection number we want to check
        for line in file:
            line = line.split()
            if line:
                sets.append(line)
    
    print("Input loaded")
    return sets

def encode(instance):
    global get_element, NUMBER_OF_UNIQUE_ELEMENTS
    # given the instance, create a cnf formula, i.e. a list of lists of integers
    # also return the total number of variables used

    # each unique element has its own variable
    # there is a new variable for each subset of size of the given intersection number to be checked
    # each variable is represented by an integer, varaibles are numbered from 1

    cnf = []
    nr_vars = 0             # will add 1 for every new var
    
    element_codes = {}      # convert element to variable
    get_element = []        # convert variable to element

    # create unique variables for each unique element in all of the sets
    for a_set in instance:
        for element in a_set:
            if element not in element_codes:
                nr_vars += 1
                get_element.append(element)
                element_codes[element] = nr_vars
    
    NUMBER_OF_UNIQUE_ELEMENTS = nr_vars
    
    # check if running the glucose makes any sense
    if NUMBER_OF_UNIQUE_ELEMENTS <= INTERSECTION_NUMBER_TO_CHECK:
        print("The total number of elements is less than or equal to the intersections number checked.")
        print("Skipping the program.")
        print()
        exit()
    
    # if two sets have share some elements at least one of these elements needs to be true  
    for i in range(len(instance)):
        for j in range(i+1, len(instance)):
            clause = []
            for el_1 in instance[i]:
                for el_2 in instance[j]:
                    if el_1 == el_2:
                        clause.append(element_codes[el_1])
            if len(clause) != 0:
                clause.append(0)
                cnf.append(clause)

    # extra variables for each unique subset of elements
    my_list = list(range(1, nr_vars+1))
    subsets = itertools.combinations(my_list, INTERSECTION_NUMBER_TO_CHECK)
    clause_of_all_subsets = []
    for subset in subsets:
        nr_vars += 1
        clause_of_all_subsets.append(nr_vars)
        for element in subset:
            cnf.append([element, -nr_vars, 0])
        
        not_in_subset = [x for x in my_list if x not in subset]
        
        for element in not_in_subset:
            cnf.append([-element, -nr_vars, 0])
    
    # only one subset of all elements that is of size of the checked intesection number can be true
    for i in range(len(clause_of_all_subsets)):
        for j in range(i+1, len(clause_of_all_subsets)):
            cnf.append([-clause_of_all_subsets[i], -clause_of_all_subsets[j], 0])
    
    clause_of_all_subsets.append(0)
    cnf.append(clause_of_all_subsets)

    return (cnf, nr_vars)

def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    # print CNF into formula.cnf in DIMACS format
    print("Running the SAT-solver")
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + '\n')
        for clause in cnf:
            file.write(' '.join(str(lit) for lit in clause) + '\n')

    # call the solver and return the output
    return subprocess.run(['./' + solver_name, '-model', '-verb=' + str(verbosity) , output_name], stdout=subprocess.PIPE)

def print_result(result):
    for line in result.stdout.decode('utf-8').split('\n'):
        print(line)                 # print the whole output of the SAT solver to stdout, so you can see the raw output for yourself

    # check the returned result
    if (result.returncode == 20):       # returncode for SAT is 10, for UNSAT is 20
        return

    # parse the model from the output of the solver
    # the model starts with 'v'
    model = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if line.startswith("v"):    # there might be more lines of the model, each starting with 'v'
            vars = line.split(" ")
            vars.remove("v")
            model.extend(int(v) for v in vars)      
    model.remove(0) # 0 is the end of the model, just ignore it

    print()
    print("##########################################################################")
    print("###########[ Human readable result of the intersection number ]###########")
    print("##########################################################################")
    print()
    print("These elements can satisfy the intersection number " + str(INTERSECTION_NUMBER_TO_CHECK) + ":")

    for i in range(NUMBER_OF_UNIQUE_ELEMENTS):
        if model[i] > 0:
            print(get_element[i], end=' ')
    print()      

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="instances/input.in",
        type=str,
        help=(
            "The instance file."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file for the DIMACS format (i.e. the CNF formula)."
        ),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help=(
            "The SAT solver to be used."
        ),
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0,2),
        help=(
            "Verbosity of the SAT solver used."
        ),
    )
    args = parser.parse_args()

    # get the input instance
    instance = load_instance(args.input)

    # encode the problem to create CNF formula
    cnf, nr_vars = encode(instance)

    # call the SAT solver and get the result
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)

    # interpret the result and print it in a human-readable format
    print_result(result)
