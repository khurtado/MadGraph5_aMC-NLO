from __future__ import division
import collections
import math
import os

try:
    import madgraph
except ImportError:
    import internal.sum_html as sum_html
    import internal.misc as misc
else:
    import madgraph.madevent.sum_html as sum_html
    import madgraph.various.misc as misc

class grid_information(object):

    start, stop = -1,1 #original interval


    def __init__(self, mc_hel):
        # information that we need to get to create a new grid
        self.mc_hel= mc_hel 
        self.grid_base = collections.defaultdict(int)
        self.original_grid = collections.defaultdict(int) 
        self.non_zero_grid = collections.defaultdict(int)
        self.ng =0
        self.maxinvar=0
        self.nonzero = 0
        self.max_on_axis = collections.defaultdict(lambda: -1)
        self.min_on_axis = collections.defaultdict(lambda: 1)
        # information that we need to evaluate the cross-section/error
        self.sum_wgt = 0
        self.sum_abs_wgt = 0
        self.sum_wgt_square =0
        self.max_wgt = 0
        self.nb_ps_point = 0
        self.target_evt = 0
        
        #
        self.results = sum_html.Combine_results('combined')
        self.discrete_grid = ""

        
        

    def convert_to_number(self, value):
        return float(value.replace('d','e'))

    def add_one_grid_information(self, path):

        if isinstance(path, str):
            finput = open(path)
        elif isinstance(path, file):
            finput=path
        else:
            raise Exception, "path should be a path or a file descriptor"
        
        line = finput.readline()
        if self.nonzero == 0:
            #first information added
            try:
                self.nonzero, self.ng, self.maxinvar = [int(i) for i in line.split()]
            except ValueError:
                return
        else:
            nonzero, ng, maxinvar = [self.convert_to_number(i) for i in line.split()]
            self.nonzero+=nonzero
            assert ng == self.ng
            assert maxinvar == self.maxinvar


        line = finput.readline()
        data = [self.convert_to_number(i) for i in line.split()]
        for j in range(self.maxinvar):
            for i in range(self.ng): 
                self.grid_base[(i,j)] = data.pop(0)

        line = finput.readline()
        data = [self.convert_to_number(i) for i in line.split()]
        for j in range(self.maxinvar):
            for i in range(self.ng): 
                self.original_grid[(i,j)] = data.pop(0)

        line = finput.readline()
        data = [self.convert_to_number(i) for i in line.split()]
        for j in range(self.maxinvar):
            for i in range(self.ng): 
                self.non_zero_grid[(i,j)] = int(data.pop(0))

        #minimal value for each variable of integraion
        line = finput.readline()
        data = [self.convert_to_number(i) for i in line.split()]
        for j in range(self.maxinvar):                
            self.min_on_axis[j] = min(self.min_on_axis[j],data.pop(0))

        #maximum value for each variable of integraion
        line = finput.readline()
        data = [self.convert_to_number(i) for i in line.split()]
        for j in range(self.maxinvar):                
            self.max_on_axis[j] = max(self.max_on_axis[j],data.pop(0))

        # cumulative variable for the cross-section
        line = finput.readline()
        data = [self.convert_to_number(i) for i in line.split()]
        self.sum_wgt += data[0]
        self.sum_abs_wgt += data[1]
        self.sum_wgt_square += data[2]
        self.max_wgt = max(self.max_wgt, data[3])
        self.nb_ps_point += data[4]
        if self.target_evt:
            assert self.target_evt == data[5], "%s != %s" % (self.target_evt, data[5])
        else: 
            self.target_evt += data[5]  
            
        # discrete sampler/helicity information
        if not self.mc_hel:
            self.helicity_line = finput.readline()
            
        if not self.discrete_grid:
            self.discrete_grid = DiscreteSampler(finput)
        else:
            self.discrete_grid.add(finput)

        
        
    def add_results_information(self, path):
        
        if isinstance(path, str):
            finput = open(path)
            fname = path
        elif isinstance(path, file):
            finput=path
            fname = finput.name
        else:
            raise Exception, "path should be a path or a file descriptor"
         
        
        self.results.add_results(fname,finput)

    
    def write_associate_grid(self, path):
        """use the grid information to create the grid associate"""

        new_grid = self.get_new_grid()
        
        fsock = open(path, 'w')
        data = []
        for var in range(self.maxinvar):
            for i in range(self.ng):
                data.append(new_grid[(i,var)])
        
        while len(data) >= 4:
            v1, v2, v3, v4 = data[:4]
            data = data[4:]
            fsock.write('%+.16f %+.16f %+.16f %+.16f \n' % (v1, v2, v3, v4))
        
        # if data is not a multiple of 4 write the rest.
        for v in data:
            fsock.write('%+.16f' % v)
        if  data:
            fsock.write('\n')
        mean = self.sum_wgt*self.target_evt/self.nb_ps_point
        fsock.write('%s\n' %(mean*self.target_evt/self.nb_ps_point**2))            
        
        if not self.mc_hel:
            fsock.write(self.helicity_line)
        
        self.discrete_grid.write(fsock)
                    
    def get_cross_section(self):
        """return the cross-section error"""

        if self.nb_ps_point == 0:
            return 0, 0, 0
                
        mean = self.sum_wgt*self.target_evt/self.nb_ps_point
        rmean =  self.sum_abs_wgt*self.target_evt/self.nb_ps_point
        
        vol = 1/self.target_evt
        sigma = self.sum_wgt_square/vol**2
        sigma -= self.nonzero * mean**2
        sigma /= self.nb_ps_point*(self.nb_ps_point -1)

        return mean, rmean, math.sqrt(abs(sigma))
        
        
            


    def get_new_grid(self):
        
        new_grid = collections.defaultdict(int)
        
        for var in range(self.maxinvar):
            one_grid = self.get_new_grid_for_var(var)
            for j,value in enumerate(one_grid):
                new_grid[(j,var)] = value
        
        return new_grid
        


    def get_new_grid_for_var(self, var):
        
        #1. biais the grid to allow more points where the fct is zero.    
        grid = collections.defaultdict(int)
        for i in range(self.ng):
            if self.non_zero_grid[(i, var)] != 0:
                factor = min(10000, self.nonzero/self.non_zero_grid[(i,var)])
                grid[(i, var)] = self.grid_base[(i, var)] * factor


        #2. average the grid
        def average(a,b,c):
            if b==0:
                return 0
            elif a==0:
                return (b+c)/2
            elif c==0:
                return (a+b)/2
            else:
                return (a+b+c)/3
        
        tmp_grid = collections.defaultdict(int)
        for j in range(self.ng):
            tmp_grid[(j, var)] = average(grid[(j-1, var)],grid[(j, var)],grid[(j+1, var)])
        grid = tmp_grid


                                    
        #3. takes the logs to help the re-binning to converge faster
        sum_var = sum([grid[(j,var)] for j in range(self.ng)])  
        for j in range(self.ng):
            if grid[(j,var)]:
                x0 = 1e-14+grid[(j,var)]/sum_var
                grid[(j,var)] = ((x0-1)/math.log(x0))**1.5
        

        start, stop = 0, self.ng-1
        start_bin, end_bin = 0, 1 
        test_grid = [0]*self.ng   # a first attempt for the new grid

        # special Dealing with first/last bin for handling endpoint.
        xmin, xmax = self.min_on_axis[var], self.max_on_axis[var]
        if (xmin- (-1) > (self.original_grid[(1,var)] - self.original_grid[(0,var)])):
            start = 1
            start_bin = xmin - (self.original_grid[(1,var)] - self.original_grid[(0,var)])/5
            test_grid[0] = start_bin
        else:
            xmin = -1
        if (1- xmax) > (self.original_grid[(self.ng-1,var)] - self.original_grid[(self.ng-2, var)]):
            stop = self.ng -2
            xmax = xmax + (self.original_grid[(self.ng-1,var)] - self.original_grid[(self.ng-2, var)])/5
            test_grid[self.ng-1] = xmax
        else:
            xmax = 1
            test_grid[self.ng-1] = xmax


        #compute the value in order to have the same amount in each bin
        sum_var = sum([grid[(j,var)] for j in range(self.ng)])  
        avg = sum_var / (stop-start+1)
        cumulative = 0
        pos_in_original_grid = -1
        for j in range(start,stop):
            while cumulative < avg and pos_in_original_grid < self.ng:
                #the previous bin (if any) is fully belonging to one single bin
                #of the new grid. adding one to cumulative up to the point that 
                #we need to split it
                pos_in_original_grid += 1
                cumulative += grid[(pos_in_original_grid, var)]
                start_bin = end_bin
                end_bin = max(xmin,min(xmax,self.original_grid[(pos_in_original_grid, var)]))
            cumulative -= avg
            #if pos_in_original_grid == 0:
            #    print grid[(pos_in_original_grid,var)]
            #    print cumulative
            if end_bin != start_bin and cumulative and grid[(pos_in_original_grid,var)]: 
                test_grid[j] = end_bin - (end_bin-start_bin)*cumulative / \
                                                grid[(pos_in_original_grid,var)]
            else:
                test_grid[j] = end_bin
                      
        # Ensure a minimal distance between each element of the grid
        sanity = True
        for j in range(1, self.ng):
            if test_grid[j] - test_grid[j-1] < 1e-14:
                test_grid[j] = test_grid[j-1] + 1e-14
            if test_grid[j] > xmax:
                sanity = False
                break
        # not in fortran double check of the sanity from the top.
        if not sanity:
            for j in range(1, self.ng):
                if test_grid[-1*j] > xmax - j * 1e-14:
                    test_grid[-1*j] = xmax - j * 1e-14
                
        # return the new grid
        return test_grid
        


class DiscreteSampler(dict):
    """ """        
    
    def __init__(self, fpath=None):
        
        if fpath:
            self.read(fpath)
    
    def add(self, fpath):
        
        self.read(fpath, mode='add')
    
    def read(self, fpath, mode='init'):
        """parse the input"""

# Example of input:
#          <DiscreteSampler_grid>
#  Helicity
#  10 # Attribute 'min_bin_probing_points' of the grid.
#  1 # Attribute 'grid_mode' of the grid. 1=='default',2=='initialization'
# # binID   n_entries weight   weight_sqr   abs_weight
#    1   255   1.666491280568920E-002   4.274101502263763E-004   1.666491280568920E-002
#    2   0   0.000000000000000E+000   0.000000000000000E+000   0.000000000000000E+000
#    3   0   0.000000000000000E+000   0.000000000000000E+000   0.000000000000000E+000
#    4   235   1.599927969559557E-002   3.935536991290621E-004   1.599927969559557E-002
#  </DiscreteSampler_grid>
        
        

        if isinstance(fpath, str):
            if '\n' in fpath:
                fsock = (line+'\n' for line in fpath.split('\n'))
            else:
                fsock = open(fpath) 
        else:
            fsock =fpath
            
        while 1:
            try:
                line = fsock.next()
            except StopIteration:
                break
            line = line.lower()
            if '<discretesampler_grid>' in line:
                grid = self.get_grid_from_file(fsock)
                tag = (grid.name, grid.grid_type)
                if mode == 'init' or tag not in self:
                    self[tag] = grid
                elif mode == 'add':
                    if grid.grid_type == 1 and grid.grid_mode == 1:
                        # reference grid not in init mode. They should 
                        #all be the same so no need to make the sum
                        continue
                    self[tag] += grid

    def get_grid_from_file(self, fsock):
        """read the stream and define the grid"""
        
#          <DiscreteSampler_grid>
#    Helicity
#  1 # grid_type: 1 for a reference and 2 for a running grid.
#  10 # Attribute 'min_bin_probing_points' of the grid.
#  1 # Attribute 'grid_mode' of the grid. 1=='default',2=='initialization'
# # binID   n_entries weight   weight_sqr   abs_weight
#    1   512   7.658545534133427E-003   9.424671508005602E-005   7.658545534133427E-003
#    4   478   8.108669631788431E-003   1.009367301168054E-004   8.108669631788431E-003
#  </DiscreteSampler_grid>
  
        
        def next_line(fsock):
            line = fsock.next()
            if '#' in line:
                line = line.split('#',1)[0]
            line = line.strip()
            if line == '':
                return next_line(fsock)
            else:
                return line
        
        #name
        firstline = next_line(fsock)
        if '#' in firstline:
            firstline = firstline.split('#',1)[0]
        name = firstline.strip()
        grid = DiscreteSamplerDimension(name)

        # line 2 grid_type
        line = next_line(fsock)
        grid.grid_type = int(line)

        # line 3 min_bin_probing_points
        line = next_line(fsock)
        grid.min_bin_probing_points = int(line)

        # line 4  grid_mode
        line = next_line(fsock)
        grid.grid_mode = int(line)


        # line 5 and following grid information
        line = next_line(fsock)
        while 'discretesampler_grid' not in line.lower():
            grid.add_bin_entry(*line.split())
            line = next_line(fsock)
        return grid
    
    def write(self, path):
        """write into a file"""
        
        if isinstance(path, str):
            fsock = open(path, 'w')
        else:
            fsock = path
        
        for  dimension in self.values():
            if dimension.grid_type != 1: #1 is for the reference grid
                continue
            dimension.update(self[(dimension.name, 2)]) #2 is for the run grid
            dimension.write(fsock)
        
            
class DiscreteSamplerDimension(dict):
    """ """
    
    def __init__(self, name):
        
        self.name = name
        self.min_bin_probing_points = 10
        self.grid_mode = 1 #1=='default',2=='initialization'
        self.grid_type = 1 # 1=='ref', 2=='run'

    def update(self, running_grid):
        """update the reference with the associate running grid """

        assert self.name == running_grid.name
        assert self.grid_type == 1 and running_grid.grid_type == 2
        
        if self.grid_mode == 1:
            #no need of special update just the sum is fine
            self += running_grid
        else:
            self.grid_mode = 1 #end initialisation
            #need to check if running_grid has enough entry bin per bin
            # if this is the case take that value
            # otherwise use the ref one (but rescaled)
            sum_ref = sum(w.abs_weight for w in self.values())
            sum_run =  sum(w.abs_weight for w in running_grid.values())
            ratio = sum_run / sum_ref
            sum_ref_sqr = sum(w.weight_sqr for w in self.values())
            sum_run_sqr =  sum(w.weight_sqr for w in running_grid.values())            
            ratio_sqr = sum_run_sqr / sum_ref_sqr
            
            self.min_bin_probing_points = 80
            for bin_id, bin_info in running_grid.items():
                if bin_info.n_entries > self.min_bin_probing_points:
                    bin_ref = self[bin_id]
                    self[bin_id] = bin_info
                else:                    
                    wgt_run = bin_info.n_entries / self.min_bin_probing_points
                    wgt_ref = (self.min_bin_probing_points - bin_info.n_entries)/ self.min_bin_probing_points       
                    bin_ref = self[bin_id]
                    # modify the entry
                    bin_ref.weight = bin_ref.weight * ratio * wgt_ref  + bin_info.weight * wgt_run
                    bin_ref.abs_weight = bin_ref.abs_weight * ratio * wgt_ref + bin_info.abs_weight * wgt_run
                    bin_ref.weight_sqr = bin_ref.weight_sqr *ratio_sqr * wgt_ref + bin_info.weight_sqr * wgt_run
                    bin_ref.n_entries = self.min_bin_probing_points                 

        #remove bin if entry if zero
        for key in self.keys():
            if not self[key].abs_weight:
                del self[key]
    

        return self

    def add_bin_entry(self, bin_id, n_entries, weight, weight_sqr, abs_weight):
# # binID   n_entries weight   weight_sqr   abs_weight
#    3   0   0.000000000000000E+000   0.000000000000000E+000   0.000000000000000E+000
#    4   235   1.599927969559557E-002   3.935536991290621E-004   1.599927969559557E-002
                
        self[bin_id] = Bin_Entry(n_entries,  weight, weight_sqr, abs_weight)

    def __iadd__(self, grid):
        """adding the entry of the second inside this grid"""

        for bin_id, bin_info in grid.items():
            if bin_id in self:
                self[bin_id] += bin_info
            else:
                self[bin_id] = bin_info
        return self
        
    def write(self, path):
        """write the grid in the correct formatted way"""
        
        if isinstance(path, str):
            fsock = open(path, 'w')
        else:
            fsock = path
                
        template = """  <DiscreteSampler_grid>
  %(name)s
  %(grid_type)s # grid_type. 1=='ref', 2=='run'
  %(min_bin_probing_points)s # Attribute 'min_bin_probing_points' of the grid.
  %(grid_mode)s # Attribute 'grid_mode' of the grid. 1=='default',2=='initialization'
#  binID   n_entries weight   weight_sqr   abs_weight
%(bins_informations)s
  </DiscreteSampler_grid>
"""
        
        #order the bin from higest contribution to lowest
        bins = [o for o in self.items()]
        def compare(x,y):
            if x[1].weight - y[1].weight <0:
                return 1
            else:
                return -1

        bins.sort(cmp=compare)
            
        data = {'name': self.name,
                'min_bin_probing_points': self.min_bin_probing_points,
                'grid_mode': self.grid_mode,
                'grid_type': self.grid_type,
                'bins_informations' : '\n'.join('    %s %s' % (bin_id,str(bin_info)) \
                                            for (bin_id, bin_info) in bins)
                }
        
        fsock.write(template % data)
    
            
class Bin_Entry(object):
    """ One bin (of the Discrite Sampler grid) """
    
    def __init__(self, n_entries, weight, weight_sqr, abs_weight):
        """initialize the bin information"""
        
        self.n_entries = int(n_entries)
        self.weight = float(weight)
        self.weight_sqr = float(weight_sqr)
        self.abs_weight = float(abs_weight)
    
    def __iadd__(self, other):
        """adding two bin together"""
        tot_entries = (self.n_entries + other.n_entries)
        if not tot_entries:
            return self
        
        self.weight = (self.n_entries * self.weight + 
                       other.n_entries * other.weight) / tot_entries 
        
        self.weight_sqr = (self.n_entries * self.weight_sqr + 
                       other.n_entries * other.weight_sqr) / tot_entries 
                       
        self.abs_weight = (self.n_entries * self.abs_weight + 
                       other.n_entries * other.abs_weight) / tot_entries                                
        
        
        self.n_entries = tot_entries
        
        return self
            
    def __str__(self):
        
        return '  %s %s %s %s' % (self.n_entries, self.weight, self.weight_sqr,
                                 self.abs_weight)
            
                          
        
        
        
        
        
        
        


            
            


