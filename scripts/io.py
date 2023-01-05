import sys
import os

args=sys.argv

"""
args[1] can be either export ot import
args[2] can be results or weights
args[3] is outputs directory on the host machine
"""

if "export" in args[1]:
    if "geometries" in args[2]:
        os.system(f"docker cp cv_container:/home/data/cardiovision_results/ {args[3]}")
    elif "models" in args[2]:
        os.system(f"docker cp cv_container:/home/app/cnn/intermediate/models {args[3]}")
    elif "features" in args[2]:
        os.system("fine the best one")
        os.system("export the best one")
    else:
        print("The export parameter has not defined properly")