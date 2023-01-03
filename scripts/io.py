import sys
import os

args=sys.argv

if "export" in args[1]:
    if "results" in args[2]:
        os.system(f"docker cp cv_container:/home/data/cardiovision_results/ {args[3]}")
    elif "weight" in args[2]:
        pass
    else:
        pass