def read_GOCAD_ts_test(tsfile):
    import re
 
    fid = open(tsfile, 'r')
    vrtx = []
    trgl = []
    #split atom line by by space, make vertex at that point in VRTX list
    #go back and get atomlist[1]  VRTXLIST[atomlist[1]-1]
    
    for line in fid:
        if 'VRTX' in line:
            l_input = re.split('[\s*]', line)
            temp = np.array(l_input[2:5])
            #temp = np.array(l_input[2:6])
            vrtx.append(temp.astype(np.float))

        if 'ATOM' in line:
            l_input = re.split('[\s*]', line)
            vertex_id = l_input[1]
            vertex_id_atom = l_input[2]
            #print(len(vrtx), vertex_id, vertex_id_atom)
            vrtx.append(vrtx[ int(vertex_id_atom) -1])

        if 'TRGL' in line:
            l_input = re.split('[\s*]', line)
            temp = np.array(l_input[1:4])
            trgl.append(temp.astype(np.int))
            
    vrtx = np.asarray(vrtx)
    trgl = np.asarray(trgl)
 
    return vrtx, trgl

def check_GOCAD_ts(tsfile):
    import re
 
    fid = open(tsfile, 'r')
    tslist = tsfile.split('\\')
    crs_dict = {"NAME":None,"AXIS_NAME":None,"AXIS_UNIT":None,"ZPOSITIVE":None}
    check_dist = {"SURFACE":tslist[-1],"NAME":None,"COORD":0,"TFACE":0,"PVRTX":0,"VRTX":0,"TRGL":0,"ATOM":0,"CRS":crs_dict, "COLOR":None}

    for index, line in enumerate(fid):
        ##HEADER
        if 'color:' in line:
            strcolor = line.split(':')
            tricolor = re.split('[\s*]', strcolor[1])
            tricolor.pop()
            tricolor[0] = float(tricolor[0]) #rgb 0-1 colors R
            tricolor[1] = float(tricolor[1]) #rgb 0-1 colors G
            tricolor[2] = float(tricolor[2]) #rgb 0-1 colors B
            check_dist["COLOR"] = tricolor
        if 'name:' in line:
            strname = line.split(':')
            usename = strname[1].replace("\n",'')
            check_dist["NAME"] = usename
        if 'NAME ' in line and "AXIS" not in line:
            strname = re.split('[\s*]', line)
            crs = strname[1].replace("\n",'')
        if 'AXIS_NAME' in line:
            axis_name = re.split('[\s*]', line)
            axis_name.pop()
        if 'AXIS_UNIT' in line:
            axis_unit = re.split('[\s*]', line)
            axis_unit.pop()
        if 'ZPOSITIVE' in line:
            zpositive = re.split('[\s*]', line)[1].replace("\n",'')
        if 'END_ORIGINAL_COORDINATE' in line:
            crs_dict["NAME"] = crs
            crs_dict["AXIS_NAME"] = axis_name
            crs_dict["AXIS_UNIT"] = axis_unit
            crs_dict["ZPOSITIVE"] = zpositive

        
        #####
        ####Data
        if 'TFACE' in line:
            check_dist["TFACE"] += 1
        if 'COORDINATE_SYSTEM' in line:
            check_dist["COORD"] += 1
        if 'ATOM' in line:
            check_dist["ATOM"] += 1
        if 'PVRTX' in line:
            check_dist["PVRTX"] += 1
        if 'VRTX' in line:
            check_dist["VRTX"] += 1
        if 'TRGL' in line:
            check_dist["TRGL"] += 1
            
    return check_dist
    
