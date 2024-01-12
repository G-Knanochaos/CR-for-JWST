import numpy as np
import math
#https://arxiv.org/pdf/1109.2626.pdf

class ramp_generator:

    def __init__(self,slope=70.0,yint=21000.0,num_samp=40,samp_time=27.7,read_noise=16.0/math.sqrt(8)):
        self.slope = slope
        self.yint = yint
        self.num_samp = num_samp
        self.samp_time = samp_time
        self.read_noise = read_noise #uncorrelated
        self.exp_sig = slope*samp_time#number of expected electrons detected in sample time

    def noisy_sample(self,previous_value):
        return ((previous_value if previous_value != None else self.yint)
                + self.exp_sig
                + np.random.poisson(self.exp_sig,1))
    
    def cr_sample(self,previous_value,num,avg_mag):
        return self.noisy_sample(previous_value) + num*avg_mag
    
    def full_sample(self,previous_value,num=0,avg_mag=0):
        return self.cr_sample(num,avg_mag) + np.random.normal(0,self.read_noise)

    def generate_integration(self,
                         num_samp=None,
                         cr_num_loc = 0,  #num of CRs generated form poisson dist
                         cr_mag_loc=20.0, 
                         cr_mag_scale=2.0):
        if not num_samp:
            num_samp = self.num_samp
        sample_matrix = zip(np.random.poisson(self.exp_sig,size=num_samp), #photon noise (correlated)
                            np.random.normal(loc=0,scale=self.read_noise,size=num_samp), #readout noise (uncorrelated)
                            abs(np.random.poisson(cr_num_loc,size=num_samp))*np.random.normal(loc=cr_mag_loc,scale=cr_mag_scale,size=num)) #total CR mag
        # print(enumerate(sample_matrix))
        samples = [self.yint]
        for i,row in enumerate(sample_matrix):
            # print(i,row)
            # print("ITER!")
            samples.append(sum(row)+samples[i]+self.exp_sig) #add previous sample value and expected signal 
        return samples
    
    def generate_set(self,num,**kwargs):
        integrations = [self.generate_integration(**kwargs) for i in range(num)]
        return integrations



    
if __name__ == "__main__":
    JWST_ramp = ramp_generator()
    print(JWST_ramp.generate_integration())
    print(JWST_ramp.generate_set(100))
