# Submitter: bryanttp(Phan, Bryant)
# Partner  : dannyhn5(Nguyen, Danny)
# We certify that we worked cooperatively on this programming
#   assignment, according to the rules for pair programming

from goody import type_as_str
import inspect

class Check_All_OK:
    """
    Check_All_OK class implements __check_annotation__ by checking whether each
      annotation passed to its constructor is OK; the first one that
      fails (by raising AssertionError) prints its problem, with a list of all
      annotations being tried at the end of the check_history.
    """
       
    def __init__(self,*args):
        self._annotations = args
        
    def __repr__(self):
        return 'Check_All_OK('+','.join([str(i) for i in self._annotations])+')'

    def __check_annotation__(self, check,param,value,check_history):
        for annot in self._annotations:
            check(param, annot, value, check_history+'Check_All_OK check: '+str(annot)+' while trying: '+str(self)+'\n')


class Check_Any_OK:
    """
    Check_Any_OK implements __check_annotation__ by checking whether at least
      one of the annotations passed to its constructor is OK; if all fail 
      (by raising AssertionError) this classes raises AssertionError and prints
      its failure, along with a list of all annotations tried followed by the
      check_history.
    """
    
    def __init__(self,*args):
        self._annotations = args
        
    def __repr__(self):
        return 'Check_Any_OK('+','.join([str(i) for i in self._annotations])+')'

    def __check_annotation__(self, check,param,value,check_history):
        failed = 0
        for annot in self._annotations: 
            try:
                check(param, annot, value, check_history)
            except AssertionError:
                failed += 1
        if failed == len(self._annotations):
            assert False, repr(param)+' failed annotation check(Check_Any_OK): value = '+repr(value)+\
                         '\n  tried '+str(self)+'\n'+check_history                 



class Check_Annotation:
    # Initially bind the class attribute to True allowing checking to occur (but
    #   only if the object's self._checking_on attribute is also bound to True)
    checking_on  = True
  
    # Initially bind self._checking_on = True, to check the decorated function f
    def __init__(self, f):
        self._f = f
        self._checking_on = True

    # Check whether param's annot is correct for value, adding to check_history
    #    if recurs; defines many local function which use it parameters.  
    def check(self,param,annot,value,check_history=''):
        
        
        def _WRONG_TYPE_MSG(ch=''): 
            return f'{param} failed annotation check(wrong type): value = {value}\n\twas type {type_as_str(value)} ...should be type {type_as_str(annot)}\n{ch}'
        def _WRONG_ANNOT_LEN_MSG(ch=''): 
            return f'{param} annotaions inconsistency: {type(annot)} should have 1 item but had {len(annot)}\n\tannotation = {annot}\n{ch}'
        
        def check_none():
            if annot == None:
                return True
            
        def gen_check():
            if isinstance(value, annot):
                return True
            assert False, _WRONG_TYPE_MSG(check_history)
        
        def check_list_or_tuple(l_or_t):
            if (l_or_t == 'list' and type(value) is not list) or (l_or_t == 'tuple' and type(value) is not tuple):
                assert False, _WRONG_TYPE_MSG(check_history)
            elif len(annot) > len(value):
                assert False, f'{param} failed annotation check (wrong type): value = {value}\n\tannotation had {len(annot)} elements{annot}\n{check_history}'
            elif len(annot) == 1:
                for i, x in enumerate(value):
                    self.check(param, annot[0], x, check_history + f'{l_or_t}[{i}] check: {annot}\n')
                return True
            elif len(annot) == len(value):
                for i in range(len(value)):
                    self.check(param, annot[i], value[i], check_history + f'{l_or_t}[{i}] check: {annot[i]}\n')
                return True
        
        def check_dict():
            if not isinstance(value, dict):
                assert False, _WRONG_TYPE_MSG(check_history)
            elif len(annot) > 1:
                assert False, _WRONG_ANNOT_LEN_MSG(check_history)
            else:
                for key in value:
                    self.check(param, list(annot)[0], key, check_history + f'{type_as_str(annot)} key check: {list(annot)[0]}\n')
                    self.check(param, list(annot.values())[0], value[key], check_history + f'{type_as_str(annot)} value check: {list(annot.values())[0]}\n')
                return True
        def check_set_or_frozenset(s_or_f):
            if (s_or_f == 'set' and type(value) is not set) or (s_or_f == 'frozenset' and type(value) is not frozenset):
                assert False, _WRONG_TYPE_MSG(check_history)
            elif len(annot) > 1:
                assert False, _WRONG_ANNOT_LEN_MSG(check_history)
            elif len(annot) > 1 and len(annot) != len(value):
                assert False, f'{param} failed annotation check (wrong type): value = {value}\n\tannotation had {len(annot)} elements{annot}\n{check_history}'
            else:
                for elem in value:
                    self.check(param, list(annot)[0], elem, check_history + f'{s_or_f} value check: {list(annot)[0]}\n')
                return True
            
        def check_func():
            annot_sig = inspect.signature(annot)
            if len(annot_sig.parameters.values()) != 1:
                assert False, f'{param} annotation inconsistency: predicate should have 1 parameter but had {annot_sig.parameters.values()}\n\tpredicate = {annot}\n{check_history}'
            try: 
                if annot(value) == False:
                    assert False, f'{param} failed annotation check: value = {value}\n\tpredicate = {annot}\n{check_history}'
            except BaseException as e:
                assert False, f'{param} annotation predicate({annot}) raised exception\n\texception = {type_as_str(e)}:{str(e)}\n{check_history}' 
            return True
                
        def check_other():
            if not hasattr(type(annot), '__check_annotation__'):
                assert False, f'{param} annotation undecipherable: {annot}'
            try:
                annot.__check_annotation__(self.check, param, value, check_history + f'{type_as_str(annot)} value check: {type_as_str(annot)}\n')
            except AssertionError as e:
                assert False, f'{str(e)}\n{type_as_str(annot)} value check: {type_as_str(annot)}\n{check_history}'
            except BaseException as e:
                assert False, f'{str(e)}\n{type_as_str(annot)} value check: {type_as_str(annot)}\n{check_history}'
            return True 
        
        def check_eval_str(self):
            # implement with _return
            try:
                for key in self.param_args_dict:
                    if type(self.param_args_dict[key]) == str:
                        exec(f'{key} = \'{self.param_args_dict[key]}\'')
                    else:
                        exec(f'{key} = {self.param_args_dict[key]}')
                if eval(annot) == False:
                    thing = ', '.join([f'{arg}->{self.param_args_dict[arg]}' for arg in self.param_args_dict])
                    assert False, f'{param} failed annotation check(str predicate: {annot}) args for evaluation: {thing}'
                return True
            except AssertionError as e:
                raise e
            except BaseException as e:
                assert False, f'{param} annotation check(str predicate: {annot}) raised exception exception = {e}: {str(e)}'
            
        if type(annot) == type(None):
            check_none()
        
        elif type(annot) is type:
            gen_check()
        
        elif type(annot) == list:
            check_list_or_tuple('list')
            
        elif type(annot) == tuple:
            check_list_or_tuple('tuple') 
            
        elif isinstance(annot, dict):
            check_dict()
            
        elif type(annot) == set:
            check_set_or_frozenset('set')
        
        elif type(annot) == frozenset:
            check_set_or_frozenset('frozenset')
            
        elif inspect.isfunction(annot):
            check_func()
            
        elif type(annot) == str:
            check_eval_str(self)
            
        else:
            check_other()
        
        
        # Define local functions for checking, list/tuple, dict, set/frozenset,
        #   lambda/functions, and str (str for extra credit)
        # Many of these local functions called by check, call check on their
        #   elements (thus are indirectly recursive)
        # Initially compare check's function annotation with its arguments

        pass 
        
    # Return result of calling decorated function call, checking present
    #   parameter/return annotations if required
    def __call__(self, *args, **kargs):
        
        # Return argument/parameter bindings in an OrderedDict (derived from a
        #   regular dict): bind the function header's parameters with that order
        def param_arg_bindings():
            f_signature  = inspect.signature(self._f)
            bound_f_signature = f_signature.bind(*args,**kargs)
            for param in f_signature.parameters.values():
                if not (param.name in bound_f_signature.arguments):
                    bound_f_signature.arguments[param.name] = param.default
            return bound_f_signature.arguments
        # print(param_arg_bindings())
        # If annotation checking is turned off at the class or function level
        #   just return the result of calling the decorated function
        # Otherwise do all the annotation checking
        if not self._checking_on or not Check_Annotation.checking_on:
            return self._f(**param_arg_bindings())
        
        
        try:
            self.annotations = self._f.__annotations__
            self.param_args_dict = param_arg_bindings()
            # print(annotations)
            # For each detected annotation, check it using its argument's value
            for param in self.annotations.keys():
                if param in self.param_args_dict:
                    self.check(param, self.annotations[param], self.param_args_dict[param])
            
            # Compute/remember the value of the decorated function
            return_value = self._f(**self.param_args_dict)
            
            # If 'return' is in the annotation, check it
            self.param_args_dict['_return'] = return_value
            if 'return' in self.annotations:
                self.check('return', self.annotations['return'], return_value)
            
            
            # Return the decorated answer
            return return_value
            
        # On first AssertionError, print the source lines of the function and reraise 
        except AssertionError as e:
            # print(80*'-')
            # for l in inspect.getsourcelines(self._f)[0]: # ignore starting line #
            #     print(l.rstrip())
            # print(80*'-')
            raise e




  
if __name__ == '__main__':     
    # an example of testing a simple annotation  
    def f(x:int): pass
    f = Check_Annotation(f)
    f(3)
    def f(x,y : 'x>y'): pass
    f = Check_Annotation(f)
    f(1,2)
    # f('a')
           
    #driver tests
    import driver
    driver.default_file_name = 'bscp4W22.txt'
#     driver.default_show_exception= True
#     driver.default_show_exception_message= True
#     driver.default_show_traceback= True
    driver.driver()
