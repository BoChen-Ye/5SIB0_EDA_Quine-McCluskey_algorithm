import re
from schemdraw.parsing import logicparse
from pyeda.inter import *


def combine_terms(term1, term2):
    diff = 0
    temp = 0
    new_term = []
    for i in range(len(term1)):
        if term1[i] == term2[i]:
            new_term += term1[i]
        elif term1[i] != '-' and term2[i] != '-':
            diff += 1
            new_term.append('-')
        elif (term1[i].isdigit() | term2[i].isdigit()) == 1:
            new_term.append('-')
            diff += 1
        else:
            new_term.append('-')
            temp += 1
    if diff == 1 or (diff == 0 and temp != 0):
        return new_term
    else:
        return None


def find_minimal_cover(terms):
    prime_implicants1 = terms.copy()
    flag = 0
    combined = []
    prime_implicants = []
    for item in prime_implicants1:
        if item not in prime_implicants:
            prime_implicants.append(item)
    for i in range(len(prime_implicants)):
        term1 = prime_implicants[i]
        for j in range(i + 1, len(prime_implicants)):
            term2 = prime_implicants[j]
            # if term2 == term1:
            #     prime_implicants.remove(term2)
            #     continue
            combined_term = combine_terms(term1, term2)
            if combined_term:
                flag = 1
                prime_implicants.append(combined_term)
                if term1 not in combined:
                    combined.append(term1)
                if term2 not in combined:
                    combined.append(term2)
    # prime_implicants[:] = (value for value in prime_implicants if value not in combined)
    for com in combined:
        if com in prime_implicants:
            prime_implicants.remove(com)

    while flag:
        prime_implicants = find_minimal_cover(prime_implicants)
        flag = 0

    return prime_implicants


def quine_mccluskey(minterms):
    minimal_cover = find_minimal_cover(minterms)
    return minimal_cover


def bool_expr_to_minterms(expr, n_variables):
    var_names = [chr(ord('A') + i) for i in range(n_variables)]
    minterms = []

    terms = [term.strip() for term in expr.split('|')]
    for term in terms:
        minterm = []
        for temp in range(n_variables):
            if '~{}'.format(var_names[temp]) in term:
                minterm.insert(0, '0')
            elif '{}'.format(var_names[temp]) in term:
                minterm.insert(0, '1')
            else:
                minterm.insert(0, '-')
        minterms.append(minterm)
    return minterms


def minimal_form_to_expr(minimal_form, n_variables):
    var_names = [chr(ord('A') + i) for i in range(n_variables)[::-1]]
    simplified_expr = []

    for term in minimal_form:
        term_expr = []
        for i, bit in enumerate(term):
            if bit != '-':
                var = var_names[i]
                term_expr.append(f'{var}' if bit == '1' else f'~{var}')
        term_expr.reverse()
        simplified_expr.append('&'.join(term_expr))
    simplified_expr[:] = (value for value in simplified_expr if value != '')
    return ' | '.join(simplified_expr)


def simplify_boolean_expression(expr, n_variables):
    transformed = deal(expr)
    minterms = bool_expr_to_minterms(transformed, n_variables)

    simplified_minterms = quine_mccluskey(minterms)

    return minimal_form_to_expr(simplified_minterms, n_variables)


def unfold(expr):
    terms = [term.strip() for term in expr.split(' | ')]
    final = [0] * len(terms)
    for i in range(len(terms)):
        term = terms[i]
        p = re.compile(r'[(](.*?)[)]', re.S)

        if re.findall(p, term):
            brac = re.findall(p, term)[0]
            brac1 = f'({brac})'
            remain = term.replace(brac1, "")
            remain = remain.strip('&')
            letters = brac.split('|')
            mid = [f'{letters[i]}&{remain}' for i in range(len(letters))]
            final[i] = ' | '.join(mid)
        else:
            final[i] = terms[i]

    new = ' | '.join(final)
    new = unfold(new) if '(' in new else new
    return new


def dealwithnot(expr):
    string = expr
    p = re.compile(r'[~][(](.*?)[)]', re.S)
    bracs = re.findall(p, string)
    rep = [0] * len(bracs)
    for num in range(len(bracs)):
        brac = bracs[num]
        string = string.replace(brac, '()')
        if ' | ' in brac:
            items = [f'~{temp}' for temp in brac.split(' | ')]
            brac = '&'.join(items)
            rep[num] = brac
            rep[num] = f'{rep[num]}'
            string = string.replace('~(())', rep[num])
        else:
            items = [f'~{temp}' for temp in brac.split('&')]
            brac = '|'.join(items)
            rep[num] = brac
            rep[num] = f'({rep[num]})'
            string = string.replace('~(())', rep[num])
    string = string.replace('~~', '')
    return string


def deal(expr):
    expr = dealwithnot(expr)
    expr = unfold(expr)
    return expr


def tocircuit(expr):
    expr = expr.replace(' | ', '+')
    return expr




if __name__ == "__main__":

    input_expr = "~(A | B)&~(C&D)"
    print("input_expr:",input_expr)
    # our QMC method
    n_variables = 4
    out_QMC = simplify_boolean_expression(input_expr, n_variables)
    print("out_QMC", out_QMC)
    # Espresso method
    A, B, C, D, E = map(exprvar, 'ABCDE')
    in_esp = expr(input_expr)
    print("in_esp:",in_esp)
    out_esp, = espresso_exprs(in_esp.to_dnf())
    print("out_esp:", out_esp)

    # validation
    if in_esp.equivalent(out_esp):
        print("The minimal functions are equivalent to the originals!")
    else: print("The minimal functions are NOT equivalent to the originals!")

    OUT_QMC = expr(out_QMC)
    print("OUT_QMC:",OUT_QMC)
    if OUT_QMC.equivalent(out_esp):
        print("Quine McCluskey algorithm results are consistent with Espresso results!")
    else: print("Quine McCluskey algorithm results are NOT consistent with Espresso results!")

    if in_esp.equivalent(out_esp) & OUT_QMC.equivalent(out_esp):
        print("Our validation success!")
    else: print("Our validation fail!")

    # generate circuit
    circuit = tocircuit(out_QMC)
    d = logicparse(circuit, outlabel='$y$')
    d.save("Output_gatecircuit.svg")