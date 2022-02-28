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
        
        # Not doing anything with check_history?
        
        WRONG_TYPE_MSG = f'{param} failed annotation check(wrong type): value = {value}\n\t'
        
        def check_none():
            if annot == None:
                return True
            
        def gen_check():
            if isinstance(value, annot):
                return True
            assert False, f'{param} failed annotation check(wrong type): value = {value}\n\twas type {type_as_str(value)} ...should be {annot}'
        
        def check_list_or_tuple(l_or_t):
            if len(annot) > len(value):
                assert False, f'{param} failed annotation check (wrong type): value = {value}\n\tannotation had {len(annot)} elements{annot}'
            elif len(annot) == 1:
                for i, x in enumerate(value):
                    self.check(param, annot[0], x, check_history=f'{l_or_t}[{i}] check: {annot}')
                return True
            elif len(annot) == len(value):
                for i in range(len(value)):
                    self.check(param, annot[i], value[i], check_history=f'{l_or_t}[{i}] check: {annot[i]}')
                return True
        
        def check_dict():
            if not isinstance(value, dict):
                assert False, f'{WRONG_TYPE_MSG}was type {type(value)} ...should be type dict'
            elif len(annot) > 1:
                assert False, f'{param} annotaions inconsistency: dict should have 1 item but had {len(annot)}\n\tannotation = {annot}'
            else:
                for key in value:
                    self.check(param, list(annot)[0], key, check_history=f'dict key check: {list(annot)[0]}')
                    self.check(param, list(annot.values())[0], value[key], check_history=f'dict value check: {list(annot.values())[0]}')
        def check_set_or_frozenset(s_or_f):
            pass
        
        if type(annot) is None:
            check_none()
        
        elif type(annot) is type:
            gen_check()
        
        elif type(annot) is list:
            check_list_or_tuple('list')
            
        elif type(annot) is tuple:
            check_list_or_tuple('tuple') 
            
        elif type(annot) is dict:
            check_dict()
            
        elif type(annot) is set:
            check_set_or_frozenset('set')
        
        elif type(annot) is frozenset:
            check_set_or_frozenset('frozenset')
        
        
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
        print(param_arg_bindings)
        # If annotation checking is turned off at the class or function level
        #   just return the result of calling the decorated function
        # Otherwise do all the annotation checking
        if self._checking_on and Check_Annotation.checking_on:
            return self._f(param_arg_bindings())
        
        
        try:
            annotations = self._f.__annotations__
            print(annotations)
            # For each detected annotation, check it using its argument's value
            for param in annotations.keys():
                self.check()
            # Compute/remember the value of the decorated function
            
            # If 'return' is in the annotation, check it
            
            # Return the decorated answer
            
            pass #remove after adding real code in try/except
            
        # On first AssertionError, print the source lines of the function and reraise 
        except AssertionError:
            print(80*'-')
            for l in inspect.getsourcelines(self._f)[0]: # ignore starting line #
                print(l.rstrip())
            print(80*'-')
            raise




  
if __name__ == '__main__':     
    # an example of testing a simple annotation  
    def f(x:int): pass
    f = Check_Annotation(f)
    f(3)
    f('a')
           
    #driver tests
    import driver
    driver.default_file_name = 'bscp4S22.txt'
#     driver.default_show_exception= True
#     driver.default_show_exception_message= True
#     driver.default_show_traceback= True
    driver.driver()
