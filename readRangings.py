import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import sys
from Filter import Filter
import numpy as np



ANCHOR_NAME = 'D'
ANCHORS = ['A','B','C','D']
anchors_pos = {'A':(0,0,0),
               'B':(0,16,0),
               'C':(6,16,0),
               'D':(6,0,0)
              }

LOGSFILE = "A/logs1.txt"
SQUARE_SIZE = 0.304
ALL_IN_ONE = True
CORRECTION = True
FILTER_ON = False
THRESHOLD = 0
THOLD_ON = False
DISPLAY = True
ABS = True
TABFILE = "res.txt"



def read_mes(logsfile):
    logs = open(logsfile)

    new_rp = False
    end_of_serie = True
    ref_points = []
    rangings = []
    serie = []
    
   
    for line in logs:
        values = line.split()
        if ( (len(values) == 0) and new_rp):
            # empty line after a new RP
            new_rp = False
            
        elif(len(values) == 0):
            # empty line after the end of a measurements serie
            end_of_serie = True

            # adding the last serie of measurements to rangings list
            # resetting serie
            
            
        elif(end_of_serie):
            # reference point
            end_of_serie = False
            new_rp = True
            if (serie != [] ):
            # serie is empty at the first iteration
                rangings.append(serie)
                
            #print("serie :" + str(serie) )
            serie = []


            rp = (float(values[0]), float(values[1]), float(values[2]))
            
            ref_points.append(rp)
        else:
            # ranging value within a serie
            ranging = values[0]
            serie.append(float(ranging) )

    # appending last serie if completed
    if (len(serie) == len( rangings[len(rangings) - 1] ) ):
        rangings.append(serie)
        #print(serie)

    logs.close()

    return( (ref_points, rangings) )

def ranging_from_rp(rp, anchor_name):
    (a,b,c) = anchors_pos[anchor_name]
    (x,y,z) = rp
    X = (x - a) * SQUARE_SIZE
    Y = (y - b) * SQUARE_SIZE
    Z = (z - c) * SQUARE_SIZE
    
    distance = math.sqrt( pow(X,2) + pow(Y,2) + pow(Z,2) )
    return(distance)

def filter_rp(rp_list,rangings, threshold = THRESHOLD):
    rp_out = []
    rangings_out = []
    rangings_copy = rangings
    for rp in rp_list:
        ranging = rangings_copy.pop(0)
        if ( ranging_from_rp(rp,ANCHOR_NAME) > THRESHOLD):
            rp_out.append(rp)
            rangings_out.append(ranging)
    return(rp_out,rangings_out)
            
    

def extract_serie(serie,real_value,correction_coeff = 1, correction_offset = 0):
    # creating sliding window
    sw_filter = Filter("SW")
    corrected_serie = []
    
    # calculating average value
    
    average = 0
    nb_values = 0
    nb_failed = 0
    for ranging in serie:
        corrected_ranging = (ranging - correction_offset) / correction_coeff
        corrected_serie.append(corrected_ranging)
        if ( (ranging < 0) or (ranging > 5 * real_value)):
        # measurements too far away from actual value are considered as failed
            nb_failed +=1
            nb_values += 1
        else:           
            average += corrected_ranging
            nb_values += 1
    if ( nb_values - nb_failed > 0 ):
        average = average / (nb_values - nb_failed)
    else:
        average = 0
        
    # calculating variance
    sd_list = []
    variance = 0

    if (THOLD_ON):
        threshold = THRESHOLD
    else:
        threshold = 0
    for ranging in serie:
        if not( (ranging < threshold) or (ranging > 5 * real_value)):
            variance += pow( (ranging - average), 2)
            sd_list.append(ranging)
            

    # set variance to 0 if there isn't correct measurements
    if (nb_values - nb_failed > 0):
        variance = variance / len(sd_list)
        
    else:
        variance = 0
    # calculating standard deviation
    abs_sd = math.sqrt(variance)
    #abs_sd = np.std(sd_list)    

    #calculating relative standard deviation
    if (average > 0):
        relative_sd = abs_sd / average
    else:
        relative_sd = 1

    # calculating fail ratio
    if (real_value > 0):
        if (ABS):
            abs_accuracy = abs(average - real_value)
        else:
            abs_accuracy = (average - real_value)
        relative_accuracy = average / real_value
        
    else:
        abs_accuracy = 0
        relative_accuracy = 1
    fail_ratio = nb_failed / nb_values

    if (FILTER_ON):
        #print("before " + str(average) )
        average = sw_filter.apply([corrected_serie,20,0])[0]
        #print("after " + str(average) )
        abs_accuracy = abs(average - real_value) 
        
   

    return(average,abs_sd,relative_sd,abs_accuracy,relative_accuracy,fail_ratio)

def mean(list):
    mean = 0
    for x in list:
        mean += x
    if (len(list) > 0):
        return (mean / len(list) )
    else:
        return 0

def linear_approx(x,y):
    X = np.array(x)
    Y = np.array(y)

    (a,b) = np.polyfit(X,Y,1)
    print("equation : " + str(a) + "x +" + str(b) )
    return(a,b)


def interpolation(x,y,mode = 'linear'):
    vals = []
    previous = 0

    x_vals = []
    y_vals = []
    idx = 0
    for distance in x:
        if not(distance < previous):
            x_vals.append(distance)
            y_vals.append(y[idx])
        previous = distance
        idx += 1

            
    steps = 50
    for i in range(steps):
        vals.append(i * (5 / steps) )
    p = np.interp(vals,x_vals,y_vals)
    return (p,vals)
    
    
def angle(ref_points,anchor):
    # getting pos of the anchor
    (a,b,c) = anchors_pos[anchor]
    angles = []

    # calculating the angles
    for (x,y,z) in ref_points:
        vector = ( x - a, y - b, z -c )
        if (vector[1] > 0 ):
            theta = math.atan( vector[0] / vector[1] )
            theta = math.degrees(theta)
        else:
            theta = 90
            
        angles.append(theta)

    return(angles)

     
        

def display(anchor_name = ANCHOR_NAME,logsfile = LOGSFILE ,mode = '2D',directive = None):
    res = read_mes(logsfile)
    
    if (THOLD_ON):
        (ref_points,rangings) = filter_rp(res[0],res[1])

    else:
        ref_points = res[0]
        rangings = res[1]        

    # print(ref_points)
    # print(rangings)
    out = [] # will be returned
    measured_rangings = [] # measured ranging value for the reference point
    real_rangings = [] # real ranging value for the reference point
    abs_standard_deviation = []
    relative_standard_deviation = []
    ratios = []
    abs_accuracies = []
    relative_accuracies = []

    angles = angle(ref_points,anchor_name)
    

    # calculating real ranging values
    
    for rp in ref_points:
        real_rangings.append(ranging_from_rp(rp,anchor_name) )
    for idx,serie in enumerate(rangings):
        (average,abs_sd,relative_sd,abs_accuracy,relative_accuracy,ratio) = extract_serie(serie, real_rangings[idx] )
        measured_rangings.append(average)
        abs_standard_deviation.append(abs_sd)
        relative_standard_deviation.append(relative_sd)
        ratios.append(ratio)
        abs_accuracies.append(abs_accuracy)
        relative_accuracies.append(relative_accuracy)


    if (CORRECTION):
        print("Before correction :")
        acc = mean(abs_accuracies)
        rel_acc = mean(relative_accuracies)
        print(" absolute accuracy: " + str(acc) )
        print(" relative accuracy: " + str(rel_acc) )

        out.append(acc)
        out.append(rel_acc)
        

        
    # interpolating values

    (inter,vals) = interpolation(real_rangings,measured_rangings)

    # linear approximation

    (a,b) = linear_approx(measured_rangings,real_rangings)

    out.append((a,b))

    # recomputing accuracy with correction applied
    if (CORRECTION):
        abs_accuracies = []
        relative_accuracies = []
        for idx,serie in enumerate(rangings):
            # correcting accuracy 
            (average,abs_sd,relative_sd,abs_accuracy,relative_accuracy,ratio) = extract_serie(serie, real_rangings[idx],a,b)
            abs_accuracies.append(abs_accuracy)
            relative_accuracies.append(relative_accuracy)

    # displaying averaged values
    sd = mean(abs_standard_deviation)
   
    acc = mean(abs_accuracies)
    rel_sd = mean(relative_standard_deviation)
    rel_acc = mean(relative_accuracies)
            

    
   
        
    
    print("absolute standard deviation : " + str(sd) + " absolute accuracy: " + str(acc) )
    print("relative standard deviation : " + str(rel_sd) + " relative accuracy: " + str(rel_acc) )

    out.append(sd)
    out.append(rel_sd)
    out.append(acc)
    
    
    if (directive == '2D'):
        fig3 = plt.figure("Directive Results")

        ax1 = fig3.add_subplot(221)
        ax1.set_title("directive absolute accuracy")
        ax1.scatter(angles[:],abs_accuracies[:])

        ax2 = fig3.add_subplot(222)
        ax2.set_title("directive relative accuracy")
        ax2.scatter(angles[:],relative_accuracies[:])

        ax3 = fig3.add_subplot(223)
        ax3.set_title("directive absolute standard deviation")
        ax3.scatter(angles[:],abs_standard_deviation[:])

        ax4 = fig3.add_subplot(224)
        ax4.set_title("directive relative standard deviation")
        ax4.scatter(angles[:],relative_standard_deviation[:])

        

    if (directive == '3D'):

        fig3 = plt.figure("Directive 3D Results")

        ax1 = fig3.add_subplot(221,projection='3d')
        ax1.set_title("directive absolute accuracy")
        ax1.scatter(angles[:],real_rangings[:],abs_accuracies[:])

        ax2 = fig3.add_subplot(222,projection='3d')
        ax2.set_title("directive relative accuracy")
        ax2.scatter(angles[:],real_rangings[:],relative_accuracies[:])

        ax3 = fig3.add_subplot(223,projection='3d')
        ax3.set_title("directive absolute standard deviation")
        ax3.scatter(angles[:],real_rangings[:],abs_standard_deviation[:])

        ax4 = fig3.add_subplot(224,projection='3d')
        ax4.set_title("directive relative standard deviation")
        ax4.scatter(angles[:],real_rangings[:],relative_standard_deviation[:])

        
        

    if (mode == '2D'):
        # plotting results

        # creating figures 
        fig1 = plt.figure("Accuracy Results")
        fig2 = plt.figure("Stability Results") 

        # creating axes 
        ax1 = fig1.add_subplot(221)
        ax1.set_title("average measured values")
        ax1.scatter(real_rangings[:],measured_rangings[:])

        
        ax2 = fig2.add_subplot(223)
        ax2.set_title("ratio")
        ax2.scatter(real_rangings[:],ratios[:])

        
        ax3 = fig2.add_subplot(221)
        ax3.set_title("absolute standard deviation")
        ax3.scatter(real_rangings[:],abs_standard_deviation[:])

        
        ax5 = fig2.add_subplot(222)
        ax5.set_title("relative standard deviation")
        ax5.scatter(real_rangings[:],relative_standard_deviation[:])

        ax7 = fig2.add_subplot(224)
        ax7.set_title("accuracy / std")
        ax7.scatter(abs_standard_deviation[:],abs_accuracies[:])
        
        
        ax4 = fig1.add_subplot(223)
        ax4.set_title("absolute accuracy")
        ax4.scatter(real_rangings[:],abs_accuracies[:])

        
        ax6 = fig1.add_subplot(224)
        ax6.set_title("relative accuracy")
        ax6.scatter(real_rangings[:],relative_accuracies[:])


        
        
    if (mode == '3D'):
        x_list = []
        y_list = []
        for rp in ref_points:
            (x,y,z) = rp
            x_list.append(x)
            y_list.append(y)
        # plotting results
        
        # creating figure 
        fig1 = plt.figure("Accuracy Results")
        fig2 = plt.figure("Stability Results")

        # creating axes 
        ax1 = fig1.add_subplot(221,projection='3d')
        ax1.view_init(elev = 45, azim = 240)
        ax1.set_title("average measured values")
        ax1.plot(x_list[:],y_list[:],measured_rangings[:])


        
        ax4 = fig1.add_subplot(222,projection='3d')
        ax4.view_init(elev = 45, azim = 240)
        ax4.set_title("real values")
        ax4.plot(x_list[:],y_list[:],real_rangings[:])


        
        ax2 = fig2.add_subplot(223,projection='3d')
        ax2.view_init(elev = 45, azim = 240)
        ax2.set_title("ratio")
        ax2.plot(x_list[:],y_list[:],ratios[:])

       
        ax3 = fig2.add_subplot(221,projection='3d')
        ax3.view_init(elev = 45, azim = 240)
        ax3.set_title("absolute standard deviation")
        ax3.plot(x_list[:],y_list[:],abs_standard_deviation[:])

        
        ax6 = fig2.add_subplot(222,projection='3d')
        ax6.view_init(elev = 45, azim = 240)
        ax6.set_title("relative standard deviation")
        ax6.plot(x_list[:],y_list[:],relative_standard_deviation[:])

        
        ax5 = fig1.add_subplot(223,projection='3d')
        ax5.view_init(elev = 45, azim = 240)
        ax5.set_title("relative accuracy")
        ax5.plot(x_list[:],y_list[:],relative_accuracies[:])

        
        ax7 = fig1.add_subplot(224,projection='3d')
        ax7.view_init(elev = 45, azim = 240)
        ax7.set_title("absolute accuracy")
        ax7.plot(x_list[:],y_list[:],abs_accuracies[:])

    if (mode == 'inter'):
        fig1 = plt.figure("Interpolation") 

        # creating axes 


        
        
        approx = []
        for val in vals:
            approx.append(a * val + b)

        ax3 = fig1.add_subplot(111)
        ax3.set_title("measured")
        ax3.plot(real_rangings[:],measured_rangings[:])

        ax2 = fig1.add_subplot(111)
        ax2.set_title("approximation")
        ax2.plot(vals[:],approx[:])



        ax1 = fig1.add_subplot(111)
        ax1.set_title("interpolation")
        ax1.plot(vals[:],inter[:])

        
    if (DISPLAY):    
        plt.show()


    return(out)


        
            
            
def get_results(start_idx,stop_idx):

    label = ["ACC","REL ACC"," A * x + B","SD","REL SD", "FINAL ACC"]
    
    # disabling results display
    
    global DISPLAY
    DISPLAY = False

    # creating tab file to write results
    tab = open(TABFILE,'w+')
    for idx in range(start_idx,stop_idx + 1):
        for anchor in ANCHORS:
            res = "single_rangings/" + anchor + "/logs" + str(idx) + ".txt"
            print("results from log " + str(idx) + "of anchor " + anchor + " : ")
            out = display(anchor_name = anchor,logsfile = res,mode = None, directive = None)
            for (i,data) in enumerate(out):
                print( label[i] )
                print(data)
                if(label[i] == "ACC"):
                    
                    str_data = str(round(data, 3))
                    tab.write(str(str_data) + ",")

                elif (label[i] == " A * x + B"):
                    str_data = "y = " + str( round(data[0],3) ) + "x" + " + " + str( round(data[1],3) )
                    tab.write(str(str_data) + ",")
                    
                
            tab.write("\n")
        tab.write("\n\n")


def get_offset(logsfile,anchor_name,correction_coeff):
    (ref_points,rangings) = read_mes(logsfile)
    mean_offset = 0
    
    for (i,rp) in enumerate(ref_points):
        serie = rangings[i]
        real_ranging = ranging_from_rp(rp,anchor_name)
       

        
        mean_ranging = 0

        for ranging in serie:
            mean_ranging += (ranging * correction_coeff)

        mean_ranging = mean_ranging / len(serie)
        offset = (real_ranging - mean_ranging)
        
        mean_offset += offset

    mean_offset = mean_offset/ len(ref_points) 

    return(mean_offset)


def calibration(idx):
    out = open("calibration.txt", 'w+')

    for anchor in ANCHORS:
        file = "single_rangings/" + anchor + "/logs" + str(idx) + ".txt"
        
        res = read_mes(file)
    
    
        ref_points = res[0]
        rangings = res[1]

        real_rangings = []
        measured_rangings = []
      
        
        for rp in ref_points:
            real_rangings.append(ranging_from_rp(rp,anchor) )

        for (i,rp) in enumerate(ref_points):
            serie = rangings[i]
        
            (average,abs_sd,relative_sd,abs_accuracy,relative_accuracy,ratio) = extract_serie(serie, real_rangings[i] )

            # getting error for anchor A
            #print(get_ranging_error('A',mean_position,rp) )
            measured_rangings.append(average)
            

        # linearisation
        ratio = real_rangings[1] / real_rangings[0]
        print("ratio is :" + str(ratio) )
        offset = ( (measured_rangings[0] * ratio) - measured_rangings[1] ) / ( 1 - ratio)
        print("offset :" + str(offset) )
        print("measured : \n" + str(measured_rangings[0]) + "\n" + str(measured_rangings[1]) )
        print("real : \n" + str(real_rangings[0]) + "\n" + str(real_rangings[1]) )

        a = measured_rangings[0] + offset
        b = measured_rangings[1] + offset

        coeff = real_rangings[0] / a
        offset = offset * coeff

        out.write("y = " + str(coeff) + "x " + " + " + str(offset) + "\n" )
        
        

        

        

   



        
            

if __name__ == "__main__":
    
    get_results(int(sys.argv[1]),int(sys.argv[2]) )
    #calibration(sys.argv[1])
    
  
            
            
        
       
       
       
        
        


    
    
            
            
