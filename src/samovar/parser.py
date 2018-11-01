# encoding: UTF-8

from samovar.ast import World, Scenario, Rule, Cond, Assert, Retract
from samovar.terms import Term, Var
from samovar.scanner import Scanner


# World         ::= {Scenario}.
# Scenario      ::= "scenario" Atom "{" {Proposition | Rule} "}".
# Proposition   ::= Term ["." | ","].
# Rule          ::= Cond {Term | Punct} Cond.
# Cond          ::= "[" Expr {"," Expr} "]".
# Expr          ::= Term | NotSym Term.
# Term          ::= Var | Atom ["(" Term {AndSym Term} ")"].
# Var           ::= Qmark | Greek.
# Qmark         ::= '?' <<A-Za-z>>.
# Greek         ::= <<one of: αβγδεζθικλμνξοπρστυφχψω>>.
# Atom          ::= <<A-Za-z possibly with punctuation on either end>>.
# NotSym        ::= '~' | '¬'.
# AndSym        ::= ',' | '∧'.


class Parser(object):
    def __init__(self, text):
        self.scanner = Scanner(text)

    def world(self):
        scenarios = []
        while self.scanner.on('scenario'):
            scenarios.append(self.scenario())
        return World(scenarios=scenarios)

    def scenario(self):
        propositions = []
        rules = []
        self.scanner.expect('scenario')
        self.scanner.check_type('word')
        name = self.scanner.token
        self.scanner.scan()
        self.scanner.expect('{')
        while not self.scanner.on('}'):
            if self.scanner.on('['):
                rules.append(self.rule())
            else:
                propositions.append(self.proposition())
        self.scanner.expect('}')
        return Scenario(name=name, propositions=propositions, rules=rules)

    def proposition(self):
        term = self.term()
        self.scanner.consume('.')
        self.scanner.consume(',')
        return term

    def rule(self):
        terms = []
        pre = self.cond()
        while not self.scanner.on('['):
            terms.append(self.term())
        post = self.cond()
        return Rule(pre=pre, terms=terms, post=post)

    def cond(self):
        exprs = []
        self.scanner.expect('[')
        if not self.scanner.on(']'):
            exprs.append(self.expr())
            while self.scanner.consume(',', u'∧'):
                exprs.append(self.expr())
        self.scanner.expect(']')
        return Cond(exprs=exprs)

    def expr(self):
        if self.scanner.consume('~', u'¬'):
            return Retract(term=self.term())
        else:
            return Assert(term=self.term())

    def term(self):
        if self.scanner.on_type('variable') or self.scanner.on_type('qmark'):
            return self.var()
        self.scanner.check_type('word', 'punct')
        constructor = self.scanner.token
        self.scanner.scan()
        subterms = []
        if self.scanner.consume('('):
            subterms.append(self.term())
            while self.scanner.consume(','):
                subterms.append(self.term())
            self.scanner.expect(')')
        return Term(constructor, subterms=subterms)

    def var(self):
        #self.scanner.check_type('variable')
        name = self.scanner.token
        self.scanner.scan()
        v = Var(name)
        return v
