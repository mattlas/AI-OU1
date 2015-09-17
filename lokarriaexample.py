"""
Example demonstrating how to communicate with Microsoft Robotic Developer
Studio 4 via the Lokarria http interface. 

Author: Erik Billing (billing@cs.umu.se)

Updated by Ola Ringdahl 204-09-11
"""

MRDS_URL = 'localhost:50000'

import httplib, json, time
from math import sin,cos,pi,atan2,sqrt

HEADERS = {"Content-type": "application/json", "Accept": "text/json"}

class UnexpectedResponse(Exception): pass

def postSpeed(angularSpeed,linearSpeed):
    """Sends a speed command to the MRDS server"""
    mrds = httplib.HTTPConnection(MRDS_URL)
    params = json.dumps({'TargetAngularSpeed':angularSpeed,'TargetLinearSpeed':linearSpeed})
    mrds.request('POST','/lokarria/differentialdrive',params,HEADERS)
    response = mrds.getresponse()
    status = response.status
    #response.close()
    if status == 204:
        return response
    else:
        raise UnexpectedResponse(response)

def getLaser():
    """Requests the current laser scan from the MRDS server and parses it into a dict"""
    mrds = httplib.HTTPConnection(MRDS_URL)
    mrds.request('GET','/lokarria/laser/echoes')
    response = mrds.getresponse()
    if (response.status == 200):
        laserData = response.read()
        response.close()
        return json.loads(laserData)
    else:
        return response
    
def getLaserAngles():
    """Requests the current laser properties from the MRDS server and parses it into a dict"""
    mrds = httplib.HTTPConnection(MRDS_URL)
    mrds.request('GET','/lokarria/laser/properties')
    response = mrds.getresponse()
    if (response.status == 200):
        laserData = response.read()
        response.close()
        properties = json.loads(laserData)
        beamCount = int((properties['EndAngle']-properties['StartAngle'])/properties['AngleIncrement'])
        a = properties['StartAngle']#+properties['AngleIncrement']
        angles = []
        while a <= properties['EndAngle']:
            angles.append(a)
            a+=pi/180 #properties['AngleIncrement']
        #angles.append(properties['EndAngle']-properties['AngleIncrement']/2)
        return angles
    else:
        raise UnexpectedResponse(response)

def getPose():
    """Reads the current position and orientation from the MRDS"""
    mrds = httplib.HTTPConnection(MRDS_URL)
    mrds.request('GET','/lokarria/localization')
    response = mrds.getresponse()
    if (response.status == 200):
        poseData = response.read()
        response.close()
        return json.loads(poseData)
    else:
        return UnexpectedResponse(response)

def bearing(q):
    return rotate(q,{'X':1.0,'Y':0.0,"Z":0.0})

def rotate(q,v):
    return vector(qmult(qmult(q,quaternion(v)),conjugate(q)))

def quaternion(v):
    q=v.copy()
    q['W']=0.0;
    return q

def vector(q):
    v={}
    v["X"]=q["X"]
    v["Y"]=q["Y"]
    v["Z"]=q["Z"]
    return v

def conjugate(q):
    qc=q.copy()
    qc["X"]=-q["X"]
    qc["Y"]=-q["Y"]
    qc["Z"]=-q["Z"]
    return qc

def qmult(q1,q2):
    q={}
    q["W"]=q1["W"]*q2["W"]-q1["X"]*q2["X"]-q1["Y"]*q2["Y"]-q1["Z"]*q2["Z"]
    q["X"]=q1["W"]*q2["X"]+q1["X"]*q2["W"]+q1["Y"]*q2["Z"]-q1["Z"]*q2["Y"]
    q["Y"]=q1["W"]*q2["Y"]-q1["X"]*q2["Z"]+q1["Y"]*q2["W"]+q1["Z"]*q2["X"]
    q["Z"]=q1["W"]*q2["Z"]+q1["X"]*q2["Y"]-q1["Y"]*q2["X"]+q1["Z"]*q2["W"]
    return q
    
def getHeading():
    """Returns the XY Orientation as a bearing unit vector"""
    return bearing(getPose()['Pose']['Orientation'])

def getAngSpeed(gp):
    speed = 0
    d = getDistanceTo(gp)

    rp = getPose()['Pose']

    dy = gp['Position']['Y'] - rp['Position']['Y']
    dx = gp['Position']['X'] - rp['Position']['X']
    
    angle = atan2(dy,dx)

    r_ori = getHeading()
    r_ori_x = r_ori['X']
    r_ori_y = r_ori['Y']

    r_angle = atan2(r_ori_y,r_ori_x)
    
    print(angle)
    print(r_angle)
    print(  )
    
    if(angle < -(pi/2) or angle > (pi/2)):
        turn = angle + r_angle
    else: 
        turn = angle - r_angle

    speed = turn
    
    
    return speed

def getLinSpeed(gp):
    speed = 0
    rp = getPose()['Pose']
    # gp = goal position, rp = robot position osv
    speed = getDistanceTo(gp)
    return speed

def pprint(p):
    print json.dumps(p,sort_keys=True,indent=4, separators=(',', ': '))

def getDistanceTo(gp):

    rp = getPose()['Pose']
    rx = rp['Position']['X']
    ry = rp['Position']['Y']
    
    gx = gp['Position']['X']
    gy = gp['Position']['Y']

    dx = gx-rx
    dy = gy-ry
    
    distanceToGoal = sqrt((dx * dx) + (dy * dy))
    return distanceToGoal

if __name__ == '__main__':

    json_data=open('Path-around-table-and-back.json').read()
    data = json.loads(json_data)
    for p in data:
        
        
        angSpeed = getAngSpeed(p['Pose'])
        linSpeed = getLinSpeed(p['Pose'])
        print(angSpeed)
        if(linSpeed > 0.4):
            postSpeed(angSpeed, linSpeed)
            time.sleep(linSpeed)
        #postSpeed(0,linSpeed)        
        #time.sleep(linSpeed)


    """print 'Sending commands to MRDS server', MRDS_URL
    try:
        print 'Telling the robot to go streight ahead.'
        response = postSpeed(0,0.1) 
        print 'Waiting for a while...'
        time.sleep(3)
        print 'Telling the robot to go in a circle.'
        response = postSpeed(0.4,0.1)        
    except UnexpectedResponse, ex:
        print 'Unexpected response from server when sending speed commands:', ex

    try:
        laser = getLaser()
        laserAngles = getLaserAngles()
        print 'The rightmost laser bean has angle %.3f deg from x-axis (streight forward) and distance %.3f meters.'%(
            laserAngles[0],laser['Echoes'][0]
        )
        print 'Beam 1: %.3f Beam 269: %.3f Beam 270: %.3f'%( laserAngles[0]*180/pi, laserAngles[269]*180/pi, laserAngles[270]*180/pi)
    except UnexpectedResponse, ex:
        print 'Unexpected response from server when reading laser data:', ex


    try:
        pose = getPose()
        print 'Current position: ', pose['Pose']['Position']
        for t in range(30):    
            print 'Current heading vector: X:{X:.3}, Y:{Y:.3}'.format(**getBearing())
            time.sleep(1)
    except UnexpectedResponse, ex:
        print 'Unexpected response from server when reading position:', ex"""
