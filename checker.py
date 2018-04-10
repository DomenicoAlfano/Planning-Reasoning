#! /usr/bin/python

import re
import sys
import os


term = '^[a-zA-Z0-9_-]*$'
param = '^\?[a-zA-Z0-9_-]+$'
req = '^\:[a-zA-Z0-9_-]+$'


class PDDL_Checker:
    def __init__(self):
        self.names = {'domain': '', 'problem': ''}
        self.files = {'domain': None, 'problem': None}
        self.requirements = []
        self.predicates = {}
        self.actions = {}
        self.objects = []
        self.init_ = []
        self.init_precs = set()
        self.goals = set()
        self.goal_logic = []
        self.curr_pred = ''
        self.curr_params = []
        self.curr_length = 0
        self.curr_act = ''
        self.not_ = 0
        self.state = []
        self.actions_to_remove = set()
        self.preds_not_to_remove = set()
        self.path = 'data/' if os.path.isdir('data') else '../data/'
        self.d_states = eval(open(self.path + 'd_states.txt').read())
        self.dd_states = eval(open(self.path + 'dd_states.txt').read())
        self.p_states = eval(open(self.path + 'p_states.txt').read())
        self.pp_states = eval(open(self.path + 'pp_states.txt').read())

    # open domain and problem
    def set_files(self, domain, problem):
        try:
            with open(domain) as f:
                self.files['domain'] = f.read().split('\n')
        except:
            print('Domain file not found')
            sys.exit(1)
        try:
            with open(problem) as f:
                self.files['problem'] = f.read().split('\n')
        except:
            print('Problem file not found')
            sys.exit(1)

    # check code
    def parse_code(self, file, func):
        self.state = [0]
        for l, line in enumerate(file):
            tokens = re.findall(r'[()]|[^\s()]+', line)
            for n, token in enumerate(tokens):
                self.state[0] = func(token, self.state[0], l + 1, n)
        # check if end of file
        if self.state[0] != 29:
            name = 'domain' if func == self.parse_token_domain else 'problem'
            print('Missing character at line %d in %s file' % (l, name))
            sys.exit(1)

    # check token in domain
    def parse_token_domain(self, t, s, l, n):
        t = t.lower()
        name = 'domain'

        # main check
        if s in self.d_states:
            new_s = self.check_element(t, s, l, self.d_states[s], name)
        elif s in self.dd_states:
            new_s = self.check_elements(t, s, l, self.dd_states[s], name)
        elif s == 3:
            if t == 'domain':
                new_s = s + 1
            elif t == 'problem':
                print('The first argument must be the domain file!')
                sys.exit(1)
            else:
                print('Missing "domain" at line %d in %s file' % (l, name))
                sys.exit(1)
        # check logic in preconditions
        elif s == 24:
            new_s = self.check_logic(t, s, l, self.actions[self.curr_act]['precs'],
                                     self.actions[self.curr_act]['logic_precs'], name)
        # check logic in effects
        elif s == 26:
            new_s = self.check_logic(t, s, l, self.actions[self.curr_act]['effs'],
                                     self.actions[self.curr_act]['logic_effs'], name)
        else:
            print('Token "%s" not recognized at line %d in %s file' % (t, l, name))
            sys.exit(1)

        # check domain name
        if s == 4:
            self.names['domain'] = t
        # check requirements
        elif s == 8 and new_s == 8:
            self.requirements.append(t)
        # check predicates
        elif s == 12:
            self.curr_pred = t
            self.predicates[t] = {'params': [], 'start': (l, n - 1)}
        # check predicate parameters
        elif s == 13 or (s == 14 and new_s == 14):
            self.predicates[self.curr_pred]['params'].append(t)
        # check if end of predicate
        elif s == 14 and new_s == 15:
            self.predicates[self.curr_pred]['end'] = (l, n)
        # check action
        elif s == 18:
            self.curr_act = t
            self.actions[t] = {'params': [], 'precs': set(), 'effs': set(),
                               'start': (l, n - 2), 'logic_precs': [], 'logic_effs': []}
        # check action parameters
        elif s == 21 or (s == 22 and new_s == 22):
            self.actions[self.curr_act]['params'].append(t)
        # check end of action
        elif s == 27:
            self.actions[self.curr_act]['end'] = (l, n)

        # print('token: %s \t\t state: %s' % (t, new_s))
        return new_s

    # check token in problem
    def parse_token_problem(self, t, s, l, _):
        t = t.lower()
        name = 'problem'

        # main check
        if s in self.p_states:
            new_s = self.check_element(t, s, l, self.p_states[s], name)
        elif s in self.pp_states:
            new_s = self.check_elements(t, s, l, self.pp_states[s], name)
        elif s == 3:
            if t == 'problem':
                new_s = s + 1
            elif t == 'domain':
                print('The second argument must be the problem file!')
                sys.exit(1)
            else:
                print('Missing "problem" at line %d in %s file' % (l, name))
                sys.exit(1)
        # check goal
        elif s == 26:
            self.curr_act = 'goal'
            new_s = self.check_logic(t, s, l, self.goals, self.goal_logic, name)
        else:
            print('Token "%s" not recognized at line %d in %s file' % (t, l, name))
            sys.exit(1)

        # check problem name
        if s == 4:
            self.names['problem'] = t
        # check domain name
        elif s == 8 and t != self.names['domain']:
            print('Different domain name at line %d in %s file' % (l, name))
            sys.exit(1)
        # check objects
        elif s == 12 or (s == 13 and new_s == 13):
            self.objects.append(t)
        # check predicates
        elif (s == 17 and new_s == 20) or s == 19:
            self.curr_pred = [t]
            self.init_precs.add('not_' + t if s == 19 else t)
            if t not in self.predicates:
                print('Predicate "%s" not declared at line %d in %s file' % (t, l, name))
                sys.exit(1)
            self.preds_not_to_remove.add(t)
        # check negation
        elif s == 17 and new_s != 20:
            self.not_ = 1
        # check parameters
        elif s == 20 or (s == 21 and new_s == 21):
            self.curr_pred.append(t)
            if t not in self.objects:
                print('Object "%s" not declared at line %d in %s file' % (t, l, name))
                sys.exit(1)
        # check if end of predicate
        elif s == 21 and new_s != 21:
            self.init_.append(self.curr_pred)
            if len(self.curr_pred) - 1 != len(self.predicates[
                                                  self.curr_pred[0]]['params']):
                print('Different number of parameters in predicate '
                      '%s at line %d in %s file' % (self.curr_pred[0], l, name))
                sys.exit(1)
            if not self.not_:
                new_s += 1
        # reset negation
        elif s == 22 and self.not_:
            self.init_[-1] = ['not', self.init_[-1]]
            self.not_ = 0

        # print('token: %s \t\t state: %s' % (t, new_s))
        return new_s

    # check single element
    def check_element(self, t, s, l, p, name):
        if re.fullmatch(p, t):
            return s + 1
        else:
            e = 'param' if p == param else 'term' if p == term else p
            print('Missing "%s" at line %d in %s file' % (e, l, name))
            sys.exit(1)

    # check two elements
    def check_elements(self, t, s, l, p, name):
        if re.fullmatch(p[0], t):
            return s + 1
        elif re.fullmatch(p[1], t):
            return s + p[2]
        else:
            e = ['param' if i == param else 'term' if i == term else i for i in p]
            print('Missing "%s" or "%s" at line %d in %s file' % (e[0], e[1], l, name))
            sys.exit(1)

    # check logic of actions
    def check_logic(self, t, s, l, preds, logic, name):
        v = term if preds is self.goals else param
        curr_s = self.state[-1] if self.state else -1

        # create new state
        if len(self.state) == 1 or curr_s in [3, 5, 8, 10, 11]:
            self.create_state(t, curr_s, l, name)

        # check predicate or operator
        elif curr_s == 0:
            new_s = self.check_element(t, curr_s, l, term, name)
            self.state[-1] = 3 if t in ['and', 'or'] else \
                5 if t == 'not' else 7 if t in ['forall', 'exists'] else \
                10 if t == 'when' else new_s
            if self.state[-1] == new_s:
                self.curr_pred = t
                preds.add('not_' + t if self.state[-2] == 6 else t)
                if t not in self.predicates:
                    print('Predicate "%s" not declared at line %d in %s file' % (t, l,
                                                                                 name))
                    sys.exit(1)
                self.preds_not_to_remove.add(t)

        # check parameter
        elif curr_s == 1:
            self.state[-1] = self.check_element(t, curr_s, l, v, name)
            self.check_parameter(t, l, v, name)

        # check parameter or end of predicate
        elif curr_s == 2:
            if self.check_elements(t, 0, l, ['\)', v, 0], name):
                if self.state[-2] != 8:
                    if self.curr_length != len(self.predicates[self.curr_pred]['params']):
                        print('Different number of parameters in action "%s" at line '
                              '%d in %s file' % (self.curr_act, l, name))
                        sys.exit(1)
                self.curr_length = 0
                self.state.pop(-1)
            else:
                self.check_parameter(t, l, v, name)

        # check end of AND operator
        elif curr_s == 4:
            if self.check_elements(t, 0, l, ['\)', '\(', 0], name):
                self.state.pop(-1)
            else:
                self.state.append(0)
        # check end of other operators
        elif curr_s in [6, 9, 12]:
            self.remove_state(t, curr_s, l, name)
            if curr_s == 9:
                self.curr_params = []
        # check begin of FORALL and EXISTS operators
        elif curr_s == 7:
            self.state[-1] = 8
            self.state.append(self.check_element(t, 0, l, '\(', name))

        # exit logic check
        if len(self.state) == 1:
            return s + 1
        # continue logic check
        if t == '(':
            if len(self.state) - 2 > 0:
                x = logic
                for a in range(len(self.state) - 3):
                    x = x[-1]
                x.append([])
        elif t != ')':
            if len(self.state) - 2 == 0:
                logic.append(t)
            else:
                x = logic[-1]
                for a in range(len(self.state) - 3):
                    x = x[-1]
                x.append(t)
        return s

    # check parameter
    def check_parameter(self, t, l, v, name):
        # check for FORALL and EXISTS operator
        if self.state[-2] == 8:
            if v == param and t in self.actions[self.curr_act]['params']:
                print('Parameter "%s" already declared in action '
                      '"%s" at line %d in %s file' % (t, self.curr_act, l, name))
                sys.exit(1)
            self.curr_params.append(t)
        # check for other operators
        else:
            self.curr_length += 1
            if v == param and t not in self.actions[self.curr_act]['params'] + \
                    self.curr_params:
                print('Parameter "%s" not declared in action '
                      '"%s" at line %d in %s file' % (t, self.curr_act, l, name))
                sys.exit(1)
            elif v == term:
                if t not in self.objects:
                    print('Object "%s" not declared at line %d in %s file' % (t, l, name))
                    sys.exit(1)

    # create new state
    def create_state(self, t, s, l, name):
        self.state[-1] = s + 1
        self.state.append(self.check_element(t, -1, l, '\(', name))

    # remove last state
    def remove_state(self, t, s, l, name):
        self.check_element(t, s, l, '\)', name)
        self.state.pop(-1)

    # remove unexecutable or useless actions
    def remove_actions(self):
        flag = False
        while not flag:
            for action in self.actions:
                total_effs = {eff for other in self.actions for eff in
                              self.actions[other]['effs']
                              if other != action}.union(self.init_precs)
                total_precs = {prec for other in self.actions for prec in
                               self.actions[other]['precs']
                               if other != action}.union(self.goals)
                # check unexecutable action
                if any(prec not in total_effs for prec in
                       self.actions[action]['precs']):
                    self.actions_to_remove.add(action)
                    print('Unexecutable action "%s" removed!' % action)
                    break
                # check useless action
                elif all(eff not in total_precs for eff in
                         self.actions[action]['effs']):
                    self.actions_to_remove.add(action)
                    print('Useless action "%s" removed!' % action)
                    break
            flag = True

    # save new domain file
    def update_domain(self):
        pointers = set()
        for i in self.actions_to_remove:
            pointers.add((self.actions[i]['start'], self.actions[i]['end']))
        for i in self.predicates:
            if i not in self.preds_not_to_remove:
                print('Predicate "%s" removed!' % i)
                pointers.add((self.predicates[i]['start'],
                              self.predicates[i]['end']))

        if pointers:
            with open('new_domain.pddl', 'w') as f:
                for l, line in enumerate(self.files['domain']):
                    tokens = re.findall(r'[()]|[^\s()]+', line)
                    write = 1
                    for start, end in pointers:
                        # check if line is the begin of action
                        if start[0] == l + 1:
                            f.write(''.join(tokens[:start[1]]) + '\n')
                            write = 0
                        # check if line is the end of action
                        elif end[0] == l + 1:
                            f.write(''.join(tokens[end[1] + 1:]) + '\n')
                            write = 0
                        # check if line is in action
                        elif start[0] < l + 1 < end[0]:
                            write = 0
                    # if line not in action
                    if write:
                        f.write(line + '\n')
            print('New domain file created!')


def main():
    if len(sys.argv) != 3:
        if len(sys.argv) > 3:
            print('Too many arguments!')
        else:
            print('Too less arguments!')
        print('The command to launch it is:')
        print("python checker.py [domain_file] [problem_file]")
        sys.exit(1)

    domain = sys.argv[1]
    problem = sys.argv[2]

    checker = PDDL_Checker()
    # set domain and problem files
    checker.set_files(domain, problem)
    # parse domain file
    checker.parse_code(checker.files['domain'], checker.parse_token_domain)
    # parse problem file
    checker.parse_code(checker.files['problem'], checker.parse_token_problem)

    # print results
    print('\nCheck complete!')
    print('\nDomain name:', checker.names['domain'])
    print('Problem name:', checker.names['problem'])
    print('\nPredicates:', checker.predicates)
    print('Requirements:', checker.requirements)
    print('\nGoals:', checker.goals)
    print('Goal Logic:', checker.goal_logic)
    print('\nActions:', checker.actions)
    print('\nObjects:', checker.objects)
    print('\nInit:', checker.init_)
    print()

    # remove actions
    checker.remove_actions()
    # update domain
    checker.update_domain()


# if __name__ == '__main__':
#     main()
