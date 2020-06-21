import regex

class LogexpsException(Exception):
    pass

class IncorrectFormulaException(LogexpsException):
    pass

class TooManyPropsException(LogexpsException):
    pass

class LengthException(LogexpsException):
    pass

def num_to_bin(num, length):
    bin_li = list(map(int,bin(num)[2:]))
    if len(bin_li) < length:
        bin_li = [0 for _ in range(length - len(bin_li))] + bin_li
    return bin_li

class Resolver:

    max_props = 8
    max_length = 100

    def __init__(self, formula):
        self.formula = formula
        if len(self._formula) > Resolver.max_length:
            raise LengthException
        self._check_entire_formula()
        self.props = Resolver._get_propositionals(self._formula)
        num_of_props = len(self.props)
        if num_of_props > Resolver.max_props:
            raise TooManyPropsException
        self.special_cases = [(dict(zip(self.props,num_to_bin(num,num_of_props))), list(self._formula)) for num in range(2 ** num_of_props)]


    operations = {'|':lambda a,b: a | b,
                  '&':lambda a,b: a & b,
                  '<->':lambda a,b: ((not a) | b) & ((not b) | a),
                  '->':lambda a,b: (not a) | b}

    def _check_entire_formula(self):
        pat = r'\(!?(\w|(?R))((->|<->|&|\|)!?(\w|(?R)))?\)'
        if not regex.fullmatch(pat,self._formula):
            raise IncorrectFormulaException(self._formula)

    @property
    def formula(self):
        return self._formula[1:-1]

    @formula.setter
    def formula(self, raw):
        self._formula = '(' + ''.join(raw.split()) + ')'

    def _get_propositionals(formula):
        return sorted(set(formula) - set('!|&<->()'))

    def _calculate_primitive(chunk, propvals):

        def calc_val(val):
            val = list(val)
            if val[-1] not in ('0','1'):
                val[-1] = propvals[val[-1]]

            if len(val) == 2:
                return int(not int(val[-1]))
            else:
                return int(val[0])

        chunk = ''.join(chunk)
        variables = regex.findall(r'!?\w', chunk)
        operation = regex.findall(r'<->|->|&|\|', chunk)
        variables = list(map(calc_val, variables))
        if operation:
            return [str(Resolver.operations[operation[0]](*variables))]
        return [str(variables[0])]

    def calculate(self):
        calculated = False
        last_used_bra = None
        last_bra = None
        offset = 0

        while not calculated:
            for ind, symb in tuple(enumerate(self.special_cases[0][1])):
                if symb == '(':
                    last_bra = ind
                
                if symb == ')' and last_bra != last_used_bra:
                    last_used_bra = last_bra
                    finst = last_bra - offset
                    sinst = ind - offset
                    offset += ind - last_bra

                    for propvals, sc_formula in self.special_cases:
                        sc_formula[finst:sinst+1] = Resolver._calculate_primitive(sc_formula[finst:sinst+1], propvals)

            if len(self.special_cases[0][1]) == 1:
                calculated = True

            offset = 0
            last_bra = None
            last_used_bra = None

class ArgException(LogexpsException):
    pass

class TooManyFormulasException(LogexpsException):
    pass

class Table_maker:

    max_formulas = 8
    max_joined_props = 10

    def __init__(self,formulas=None,*,filename=None):
        if formulas:
            if len(formulas) > Table_maker.max_formulas:
                raise TooManyFormulasException(len(formulas))
            self.formulas = [Resolver(formula) for formula in formulas]
        elif filename:
            self.formulas = []
            with open(filename) as file:
                count = 0
                for line in file:
                    self.formulas.append(Resolver(line.strip()))
                    if count > Table_maker.max_formulas:
                        break
                    count+=1
        else:
            raise ArgException

        self.propositionals = set()
        for formula in self.formulas:
            self.propositionals.update(formula.props)
        self.propositionals = sorted(self.propositionals)
            
        if len(self.propositionals) > Table_maker.max_joined_props:
            raise TooManyPropsException(len(self.propositionals))

        for formula in self.formulas:
            formula.calculate()
        


    def get_table(self):
        table = []
        for prop in self.propositionals:
            table.append(prop + ' ')
        table.append(' ' * 3)
        for formula in self.formulas:
            table.append(formula.formula + ' ' * 4)
        table.append('\n')

        num_of_props = len(self.propositionals)
        for k in range(2**num_of_props):
            bin_list = num_to_bin(k,num_of_props)
            props_and_vals = dict(zip(self.propositionals,bin_list))
            for bit in bin_list:
                table.append(str(bit) + ' ')
            table.append(' ' * 3)
            for formula in self.formulas:
                indent = int(len(formula.formula)/2)

                values = [props_and_vals[prop] for prop in formula.props]
                index = int(''.join(map(str,values)),2)

                res_of_sc = formula.special_cases[index][1][0]
                table.append((' '*indent)+res_of_sc+(' '*(len(formula.formula)-indent-1)) + ' ' * 4)
            table.append('\n')
        return ''.join(table)

if __name__ == '__main__':
    a = Table_maker(('A->B',))
    print(a.get_table())