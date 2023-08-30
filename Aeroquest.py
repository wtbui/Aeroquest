import os
import glob
import sys
import json
from time import sleep
import time

#############################################
##            GLOBAL VARIABLES             ##
#############################################

DEFAULT_PARAMS = {"Sref": "45.0", "Cref": "2.5", "Bref": "18", "X_cg": "0.",
                  "Y_cg ": "0.", "Z_cg": "0.", "Mach": "0.1", "AoA": "10.",
                  "Beta": "0.", "Vinf": "1.", "Rho": "0.002377", "ReCref": "2200000.",
                  "ClMax": "-1.", "Clo2D": "0.4", "MaxTurningAngle": "-1.", 
                  "Symmetry": "N", "FarDist": "-1", "NumWakeNodes": "-1", 
                  "WakeIters": "3", "NumberOfRotors": "0", "GMRESReductionFactor": "0.001"}

## READ File Paths ##
databasePath = "./database" # Path to database

## THICK WING ##
geomDataPath = "./TestCase.Fine/wing"
geomDataPathCoarse = "./TestCase.Fine/wingcoarse"
geomDataPathMed = "./TestCase.Fine/wingmed"

## THIN WING ##
# geomDataPath = "./TestCase.Thick/Fine/wing"
# geomDataPathCoarse = "./TestCase.Thick/Coarse/wing"
# geomDataPathMed = "./TestCase.Thick/Med/wing"

outputFile = "VSPAero" # Json filename header
vspAeroPath = "/home/wbui/VSPAERO-QUEST/bin/vspaero" # Path to VSPAero solver
questLauncherPath = "/home/wbui/questlaunchers/QuestLauncher.jar" # Path to quest launcher
slicerPath = "./Adb2Load/adb2loads" # Path to ADB slicer

questScriptPath = "./script" # Path to quest script
questScriptMeasurePath = "./configjsonmeasurement" # Path to quest script measure file

mainDir = "/home/wbui/Quest-VSP" # Path to Aeroquest


#############################################
##           PARSE DATABASE DATA           ##
#############################################

def genZeros(total_len, original_str):
    """Formats strings with 0's
    
    Args:
        total_len (int): Total length of formatted string
        original_str (str): Original string

    Returns:
        Formatted string with 0's
    
    """
    for i in range(total_len - len(original_str)):
        original_str = "0" + original_str

    return original_str

def parseDatabase(filePath, outputFileName, num_levels):
    """Parses Quest-prep database file
    
    Args:
        filePath (str): Path to database file
        outputFileName (str): Header for quest post json filename
        num_levels (int): Number of meshes

    Returns:
        2D list of dictionaries containing uncertainty parameters and filename for each case from each mesh
    """
    
    database = open(filePath)

    with database as file:
        databaseLines = [line.rstrip() for line in file]
    database.close()

    vspAero_runs = int(databaseLines[2].split(" ")[0])
    vspAero_runs_total = int(databaseLines[2].split(" ")[1])
    vsp_param_data = databaseLines[4:4 + int(vspAero_runs_total)]
    vsp_params = databaseLines[3].split()

    parsed_vsp_param_data = []
    parsed_vsp_param_data_all = []

    increment_value = vspAero_runs_total // vspAero_runs

    for i in range(increment_value):
        parsed_vsp_param_data = []
        for j in range(i, vspAero_runs_total, num_levels):
            param = vsp_param_data[j]
            parsed_vsp_param_data.append(parseLineData(param, vsp_params, outputFileName))

        parsed_vsp_param_data_all.append(parsed_vsp_param_data)

    return parsed_vsp_param_data_all

def parseLineData(param_string, uncertainty_param_names, outputFileName):
    """Parses an individual line from the Quest-prep database file

    Args:
        param_string (str): Individual line from database file
        uncertainty_param_names (string list): List of uncertainty parameters
        outputFileName (str): Name of json file for case

    Returns:
        Dictionary containing case filename and uncertainty parameter
    """
    param_arr = param_string.split()
    uncertainty_params = {}
    stringId = outputFileName
    xId = genZeros(5, param_arr[3])
    yId = genZeros(2, param_arr[2]) 
    zId = genZeros(5, param_arr[0])
    fileName = f"{stringId}.{xId}.{yId}.{zId}"

    for i, name in enumerate(uncertainty_param_names):
        uncertainty_params[name] = float(param_arr[5 + i])

    return {'filename': fileName, 'data': uncertainty_params}


#############################################
##                 VSPAERO                 ##
#############################################

def writeVspAeroFiles(vspCases, geomData):
    """Writes out .vspaero config file containing runs from parsed database
    
    Args:
        vspCases (dictionary list): List containing cases from a single mesh
        geomData (str): Path to geometry

    Retruns:
        None, Writes out a .vspaero file to geomdata path
    """
    vspAeroFile = open(f"{geomData}.vspaero", 'w')

    for param in DEFAULT_PARAMS.keys():
        if param in list(vspCases[0]['data'].keys()):
            vspAeroFile.write(f"{param} = ")
            for vspCase in vspCases[:-1]:
                vspAeroFile.write(f"{vspCase['data'][param]}, ")

            vspAeroFile.write(f"{vspCases[-1]['data'][param]}\n")
                
        else:
            vspAeroFile.write(f"{param} = {DEFAULT_PARAMS[param]}\n")
        
    vspAeroFile.close()
    print("File Successfully Written")

def deleteVspAeroFiles(geomData):
    """Deletes .vspaero config file
    
    Args:
        geomData (str): Path to geometry

    Returns:
        None, Deletes .vspaero file in geomData path
    """
    files = glob.glob(f"{geomData}.vspaero")
    for f in files:
        os.remove(f)
    print("Files Successfully Deleted")

def runSolver(vspAeroFile, geomData):
    """Runs VSPAero solver
    
    Args:
        vspAeroFile (str): Path to .vspaero config file
        geomData (str): Path to geometry
        
    Returns:
        None, runs VSPAero solver
    """
    os.system(f"{vspAeroFile} -quest -omp 10 {geomData}")
    return None

def createSliceData(slicerFile, geomData):
    """Runs geometry slicer

    Args:
        slicerFile (str): Path to adb slicer
        geomData (str): Path to geometry

    Returns:
        None, runs ADB slicer
    """
    os.system(f"{slicerFile} -slice {geomData}")


#############################################
## PARSE VSPAERO OUTPUT (vsp -> questpost) ##
#############################################

def parseVSPAeroLineData(data_string):
    """Parses line from .polar file

    Args:
        data_string (str): Line from .polar file

    Returns:
        Dictionary containing CL, CDTot, and CMy values from line
    """
    data_arr = data_string.split()

    cl = data_arr[4]
    cdtot = data_arr[7]
    cmy = data_arr[-6]

    return {'CL': cl, 'CDTot': cdtot, 'CMy': cmy}

def parseVSPAeroData(filePath):
    """Parses VSPAero output from .polar file

    Args:
        filePath (str): Path to .polar file
    
    Returns:
        List of dictionaries containing outputs from VSPAero
    """
    vsp_out = open(filePath + ".polar")

    with vsp_out as file:
        vsp_out_lines = [line.rstrip() for line in file]
    vsp_out.close()

    parsed_vspout = []
    for line in vsp_out_lines[1:]:
        parsed_vspout.append(parseVSPAeroLineData(line))

    return parsed_vspout

def parseSliceLineData(data_string):
    """Parses line from .slc file
    
    Args:
        data_string (str): Line from .slc file
        
    Returns:
        Dictionary containing values from .slc file
    """
    data_arr = data_string.split()

    x = data_arr[0]
    y = data_arr[1]
    z = data_arr[2]
    dCp = data_arr[3]

    return {'x': float(x), 'y': float(y), 'z': float(z), 'dCp': float(dCp)}

def parseSliceData(filePath):
    """Parses slicer output from .slc file

    Args:
        filePath (str): Path to .slc file

    Returns:
        3D list containing slice data from each case

        EXAMPLE FORMAT:
        [
           [
               [{case 1 slice 1 data}, {case 1 slice 1 data}]
               [{case 1 slice 2 data}, {case 1 slice 2 data}]
           ], 
           [
               [{case 2 slice 1 data}, {case 2 slice 1 data}]
               [{case 2 slice 2 data}, {case 2 slice 2 data}]
           ]
        ]
    """
    slice_data = open(filePath)

    with slice_data as file:
        slice_data_lines = [line.rstrip() for line in file]

    slice_data.close()
 
    parsed_slice_data = [[]]
    case_num = -1
    i = 0

    while i < len(slice_data_lines):
        line = slice_data_lines[i]

        if len(line) > 0:
            if line[0] == 'B':
                case_num = int(slice_data_lines[i + 1].split()[1])
                i += 3  
            else:
                if len(parsed_slice_data) == case_num:
                    parsed_slice_data.append([])

                parsed_line = parseSliceLineData(line)
                parsed_slice_data[case_num].append(parsed_line)

        i += 1

    parsed_slice_data_reorg = []

    for case in parsed_slice_data[1:]:
        case_arr = []
        slice_arr = []
        for i, point in enumerate(case):
            if i == 0:
                slice_arr.append(point)
            else:
                if point['y'] != case[i - 1]['y']:
                    case_arr.append(slice_arr)
                    slice_arr = [point]
                else:
                    slice_arr.append(point)
        
        case_arr.append(slice_arr)
        parsed_slice_data_reorg.append(case_arr)

    for case_i, case in enumerate(parsed_slice_data_reorg):
        for slice_i, slice in enumerate(case):
            parsed_slice_data_reorg[case_i][slice_i] = edgeSort(slice)
            
            total_len = 0

            for point_i in range(1, len(parsed_slice_data_reorg[case_i][slice_i])):
                x1 = parsed_slice_data_reorg[case_i][slice_i][point_i - 1]['x']
                x2 = parsed_slice_data_reorg[case_i][slice_i][point_i]['x']
                diff = abs(x2 - x1)

                total_len += diff

            curr_len = 0
            parsed_slice_data_reorg[case_i][slice_i][0]['arclen'] = 0.0

            for point_i in range(1, len(parsed_slice_data_reorg[case_i][slice_i])):
                x1 = parsed_slice_data_reorg[case_i][slice_i][point_i - 1]['x']
                x2 = parsed_slice_data_reorg[case_i][slice_i][point_i]['x']
                diff = abs(x2 - x1)

                curr_len += diff

                parsed_slice_data_reorg[case_i][slice_i][point_i]['arclen'] = curr_len / total_len

    return parsed_slice_data_reorg

def edgeSort(slice):
    """Sorts slice points by upper and lower edge
    
    Args:
        slice (dict list): List of dictionaries containing points from a slice
        
    Returns:
        Dictionary list containing sorted slice    
    """
    upper_edge = [point for point in slice if point['z'] >= 0]
    lower_edge = [point for point in slice if point['z'] < 0]

    upper_edge = sorted(upper_edge, key = lambda point: point['x'])
    lower_edge = sorted(lower_edge, key = lambda point: -1 * point['x'])

    upper_edge.extend(lower_edge)

    return upper_edge

def genPoints(sliceData, arc_len_arr, x_arr):
    """Interpolates fine mesh points onto coarser meshes
    
    Args:
        sliceData (3D dict list): List containing slice points from all cases of a single mesh
        arc_len_arr (dict list): List containing arc lengths from finest mesh
        x_arr (dict list): List containing x values from finest mesh

    Returns:
        Interpolated slice data (3D list)
    """
    print("NUM CASES", len(sliceData))
    for j in range(len(sliceData)):
        max_point = len(sliceData[j][0])

        for slice_i in range(len(sliceData[j])): #slice_i correspond with x_arr_i
            lower_i = 0
            upper_i = 1
            new_slice = [] 

            for x_coor in x_arr[slice_i]:
                if x_coor == sliceData[j][slice_i][lower_i]["x"]:
                    new_slice.append(sliceData[j][slice_i][lower_i])
                
                elif x_coor == sliceData[j][slice_i][upper_i]["x"]:
                    new_slice.append(sliceData[j][slice_i][upper_i])
                    lower_i = upper_i
                    upper_i = (upper_i + 1) % max_point

                else:
                    if sliceData[j][slice_i][upper_i]["z"] < 0:
                        if x_coor < sliceData[j][slice_i][upper_i]["x"]:
                            lower_i = upper_i
                            upper_i = (upper_i + 1) % max_point
                    else:
                        if x_coor > sliceData[j][slice_i][upper_i]["x"]:
                            lower_i = upper_i
                            upper_i = (upper_i + 1) % max_point

                    new_point = {}
                    x1 = sliceData[j][slice_i][lower_i]['x']
                    z1 = sliceData[j][slice_i][lower_i]['z']
                    x2 = sliceData[j][slice_i][upper_i]['x']
                    z2 = sliceData[j][slice_i][upper_i]['z']
                    x = x_coor
                    print(x1, x2)
                    z = z1 + (x - x1) * ((z2 - z1) / (x2 - x1))
                    dCp = (sliceData[j][slice_i][lower_i]['dCp'] + sliceData[j][slice_i][upper_i]['dCp']) / 2

                    new_point['x'] = x
                    new_point['y'] = sliceData[j][slice_i][lower_i]['y']
                    new_point['z'] = z
                    new_point['dCp'] = dCp

                    new_slice.append(new_point)

            for arc_len_i, arc_len in enumerate(arc_len_arr[slice_i]):
                new_slice[arc_len_i]['arclen'] = arc_len

            sliceData[j][slice_i] = new_slice
    
    return sliceData

def writeJsonFilesSlice(slice_out, vsp_cases):
    """Writes JSON files from parsed slice data
    
    Args:
        slice_out (3D dict list): List of parsed slice data
        vsp_cases (2D list): List of parsed database data
        
    Returns:
        None, writes out json files for Quest-post
    """
    for i, case in enumerate(slice_out): 
        slice_out_dict = {"label": "VSPAero", "children":[]}

        for j, slice in enumerate(case):
            new_slice = {"label": f"cut y:{slice[0]['y']}", 
                         "leaf": {
                            "abscissa_names": ["arclen", "x", "y", "z"],
                            "ordinate_names": ["dCp"],
                            "ordinate_types": [0],
                            "data": []
                         }
                        }
            
            slice_out_dict["children"].append(new_slice)
            
            for k, point in enumerate(slice):
                slice_out_dict["children"][j]['leaf']["data"].append([k, [point['arclen'], point['x'], point['y'], point['z']], [point['dCp']]])
        
        print(f"Writing {vsp_cases[i]['filename']}.json...")
        slice_json = open(f"./QuestpostInputData/{vsp_cases[i]['filename']}.json", 'w')
        json.dump(slice_out_dict, slice_json)
    

def writeJsonFiles(vsp_out, vsp_cases):
    """Writes JSON files from parsed vspaero output
    
    Args:
        vsp_out (3D dict list): List of parsed vspaero data
        vsp_cases (2D list): List of parsed database data
        
    Returns:
        None, writes out json files for Quest-post
    """
    for i, data in enumerate(vsp_out):
        vsp_out_dict = {"label": "VSPAero",
                        "leaf": {
                            "abscissa_names": ["x"],
                            "ordinate_names": [],
                            "ordinate_types": [0, 0, 0],
                            "data": [[0, [1.0], []]]
                        },
                    }
        
        vsp_out_dict["leaf"]["ordinate_names"] = list(data.keys())
        vsp_out_dict["leaf"]["data"][0][2] = [float(data['CL']), float(data['CDTot']), float(data['CMy'])]

        print(f"Writing {vsp_cases[i]['filename']}.json...")
        vsp_json = open(f"./QuestpostInputData/{vsp_cases[i]['filename']}.json", 'w')
        json.dump(vsp_out_dict, vsp_json)

def bundleJson():
    """Creates a json bundle from json files
    
    Args:
        None (File path to json files as a global variable)
    
    Returns:
        None, bundles json files
    """
    print("Json files written, bundling...")
    os.system(f"cd QuestpostInputData; jar cf {outputFile}.bundle.json {outputFile}.*.json")

def deleteJsonFiles():
    """Deletes json files
    
    Args:
        None (File path to json files as a global variable)
    
    Returns:
        None, deletes json files
    """
    files = glob.glob(f"./QuestpostInputData/*.json")
    for f in files:
        os.remove(f)
    print("Files Successfully Deleted")

#############################################
##        RUN QUEST POSTPROCESSOR          ##
#############################################

def writePostFiles(questScript, questScriptMeasure, globalPath, output):
    """Writes script for Quest-post application
    
    Args:
       questScript (str): Path to Quest-post script
       questScriptMeasure (str): Path to Quest-post script measure file
       globalPath (str): Global path to Quest-post script file
       output (str): Name header for json file
    
    Returns:
        None, Writes script file for Quest-post
    """
    questScriptFile = open(f"{questScript}", 'w')

    questScriptFile.write(f"remote(false)\n")
    questScriptFile.write(f"cd({globalPath})\n")
    questScriptFile.write(f"panel(json) read_database(*) read_measurement(./QuestpostInputData/{output}.bundle.json) read_measurementconfig({questScriptMeasure})")
    questScriptFile.close()

    questScriptMeasureFile = open(f"{questScriptMeasure}", 'w')
    questScriptMeasureFile.write("VSPAero	true\n")
    questScriptMeasureFile.write("CL	false\n")
    questScriptMeasureFile.write("ParPanelNoError	false	0	0	x	false	false	false	true	false	false	false	1-σ	false	false	1.0	false\n")
    questScriptMeasureFile.write("CDTot	false\n")
    questScriptMeasureFile.write("ParPanelNoError	false	0	0	x	false	false	false	false	false	false	false	1-σ	false	false	1.0	false\n")
    questScriptMeasureFile.write("CMy	false\n")
    questScriptMeasureFile.write("ParPanelNoError	false	0	0	x	false	false	false	false	false	false	false	1-σ	false	false	1.0	false\n")
    questScriptMeasureFile.close()

def runPost(questScript, questLauncher):
    """Runs Quest-post application

    Args:
        questScript (str): Path to Quest-post script
        questLauncher (str): Path to Quest launcher
    """
    os.system(f"java -jar {questLauncher} -post -script {questScript} -debug")


#############################################
##               AEROQUEST                 ##
#############################################

def aeroquest(meshPathArr, num_levels):
    """Runs Aeroquest for non-slice data

    Args:
        meshPathArr (str list): List of strings containing paths to geometry files
        num_levels (int): Number of meshes

    Returns:
        None, Runs Aeroquest
    """
    vspCases = parseDatabase(databasePath, outputFile, num_levels)
    vspCases = vspCases[::-1]
    start = time.time()

    for i, meshPath in enumerate(meshPathArr):
        print("Current Mesh: ", meshPath)
        deleteVspAeroFiles(meshPath)
        writeVspAeroFiles(vspCases[i], meshPath)
        runSolver(vspAeroPath, meshPath)

    deleteJsonFiles()
    for i, vspCase in enumerate(vspCases):
        writeJsonFiles(parseVSPAeroData(meshPathArr[i]), vspCase)

    bundleJson()
    writePostFiles(questScriptPath, questScriptMeasurePath, mainDir, outputFile)
    end = time.time()

    time_file = open("execution.time", "w")
    time_file.write(f"Execution Time: {start - end} s")
    runPost(questScriptPath, questLauncherPath)

def aeroquest_mg(geomDataPath, polarPathArr):
  """Runs Aeroquest for non-slice data with mglevel

    Args:
        geomDataPath (str): Contains path to fine mesh
        polarPathArr (str list): List of strings containing paths to polar files

    Returns:
        None, Runs Aeroquest
    """
    vspCases = parseDatabase(databasePath, outputFile)
    print(len(vspCases))

    deleteJsonFiles()
    for i, meshPath in enumerate(polarDataArr):
        deleteVspAeroFiles(geomDataPath)
        writeVspAeroFiles(vspCases[i], geomDataPath)
        runSolver(vspAeroPath, i + 1, geomDataPath)
        
        writeJsonFiles(parseVSPAeroData(polarPathArr[i]), vspCases[i])

    bundleJson()
    writePostFiles(questScriptPath, questScriptMeasurePath, mainDir, outputFile)
    runPost(questScriptPath, questLauncherPath)
  
def aeroquestSlice(meshPathArr, num_levels):
    """Runs Aeroquest for slice data

    Args:
        meshPathArr (str list): List of strings containing paths to geometry files
        num_levels (int): Number of meshes

    Returns:
        None, Runs Aeroquest for slice data
    """
    vspCases = parseDatabase(databasePath, outputFile, num_levels)
    vspCases = vspCases[::-1]

    for i, meshPath in enumerate(meshPathArr):
        print("Current Mesh: ", meshPath)
        deleteVspAeroFiles(meshPath)
        writeVspAeroFiles(vspCases[i], meshPath)
        runSolver(vspAeroPath, meshPath)
        createSliceData(slicerPath, meshPath)

    deleteJsonFiles()

    arc_len_arr = []
    x_arr = []

    for i in range(len(vspCases)):
        filePath = meshPathArr[i] + ".slc"
        sliceData = parseSliceData(filePath)

        if i == 0:
            for slice in sliceData[0]:
                arc_len_arr.append([point['arclen'] for point in slice])
                x_arr.append([point['x'] for point in slice])

        sliceData = genPoints(sliceData, arc_len_arr, x_arr) # Interpolation and Sorting
        writeJsonFilesSlice(sliceData, vspCases[i])

    bundleJson()
    writePostFiles(questScriptPath, questScriptMeasurePath, mainDir, outputFile)
    runPost(questScriptPath, questLauncherPath)

#############################################
##              FLAG PARSING               ##
#############################################

if len(sys.argv) > 1:
    match sys.argv[1]:
        case "-h":
            print("Format: python3 Aeroquest.py <command type> <mesh number (1-3)> <-slice (for slice)>\n")
            print("-h: Help Menu")
            print("-w: Write .VSPAero Files")
            print("-d: Delete .VSPAero Files")
            print("-s: Runs VSPAero Solver")
            print("-ws: Runs full Quest/VSP Wrapper, to run for slice data add -slice flag")
            print("-wsmg: Runs full Quest/VSP Wrapper with mglevel")
        case "-d":
            deleteVspAeroFiles(geomDataPath)
        case "-w":
            vspCases = parseDatabase(databasePath, outputFile)
            writeVspAeroFiles(vspCases[0], geomDataPath)

        case "-s":
            runSolver(vspAeroPath, geomDataPath)
        
        case "-ws":
            if len(sys.argv) < 3:
                print("Error: Missing Mesh Number Arg")
            else:
                geomDataArr = []
                polarDataArr = []
                match sys.argv[2]:
                    case "1":
                        geomDataArr = [geomDataPath]
                    case "2":
                        geomDataArr = [geomDataPath, geomDataPathCoarse]
                    case "3":
                        geomDataArr = [geomDataPath, geomDataPathMed, geomDataPathCoarse]
                    case _:
                        print("Error: Invalid Mesh Number")
                        sys.exit()

            if len(sys.argv) < 4:
                aeroquest(geomDataArr, int(sys.argv[2]))
            else:
                print(len(sys.argv))
                if sys.argv[3] == "-slice":
                    print("Outputting Slice Data")
                    aeroquestSlice(geomDataArr, int(sys.argv[2]))
                  
        case "-wsmg":
                  polarDataArr = [polarFilePath, polarFilePathMed, polarFilePathCoarse]
                  aeroquest_mg(geomDataPath, polarDataArr)
          
        case "-test":
            print("Nothing to see here")

        case _:
            print("Error: Invalid Argument Provided")
else:
    print("Error: No Arguments Provided")
