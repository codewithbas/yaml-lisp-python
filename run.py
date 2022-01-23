import sys
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class ControlException(Exception): pass
class BreakException(ControlException): pass


class Parser:
    def __init__(self, data):
        """ Constructor takes the parsed yaml file
        and initializes the variable storage."""
        self.data = data    # parsed yaml
        self._store = {}    # the variable store

    def run(self):
        """This function is the entry point for the interpreter."""
        for line in self.data:
            self.exec_line(line)
    
    def exec_line(self, line):
        # If the line is a string, it could still be an exposed function,
        # so call that.
        if type(line) == str or type(line) == int:
            return self.str_or_func(line)
        name = list(line.keys())[0]
        fn = self.__getattribute__("exp_"+name)
        return fn(line[name])

    def str_or_func(self, x):
        """Returns the result of an exposed function,
        or the string otherwise."""
        try:
            fn = self.__getattribute__("exp_"+x)
            return fn()
        except Exception as e:
            # Our own ControlExceptions must be re-raised.
            if isinstance(e, ControlException):
                raise e
            return x

    def car(self, arg):
        if type(arg) == dict:
            return self.exec_line(arg)
        if type(arg) == list:
            res = [self.exec_line(code) for code in arg]
            return res[0] if len(res) == 1 else res
        else:
            res = arg
        return self.exec_line(res)

    exp_from = exp_else = exp_then = exp_val1 = exp_val2 = exp_what = car

    def exp_break(self):
        raise BreakException

    def exp_get_store(self, arg):
        fr = arg[0]
        s = self.exp_what(fr)
        try:
            return self._store.get(s)
        except:
            print("ERR", s)

    def exp_store(self, arg):
        kwargs = (arg[0] | arg[1])
        self._store[kwargs['to']] = self.exp_what(kwargs['what'])
        # No return here, means, we have a statement, not an expression ;)

    def exp_input(self):
        return input("Please enter some value:")

    def exp_say(self, *args):
        for arg in args:
            for code in arg:
                what = self.exec_line(code)
        print(what)

    def exp_ifeq(self, arg):
        val1 = self.exec_line(arg[0])
        val2 = self.exec_line(arg[1])
        if str(val1) == str(val2):
            then = self.exec_line(arg[2])
            return then
        else:
            try:
                otherwise = self.exec_line(arg[3])
            except IndexError:
                pass
            except:
                raise
    
    def exp_repeat(self, arg):
        n = arg[0]
        for code in arg[1:]:
            for i in range(int(n)):
                try:
                    self.exec_line(code)
                except BreakException:
                    break

    def exp_concat(self, arg):
        s  = ""
        for code in arg:
            s += str(self.exp_what(code))
        return s

    def exp_plus(self, arg):
        return sum(int(self.exp_what(code)) for code in arg)



if __name__=="__main__":
    data = load(open(sys.argv[1], 'r'), Loader=Loader)
    parser = Parser(data)
    parser.run()