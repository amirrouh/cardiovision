# -*- coding: utf-8 -*-
"""
Created on Mon May 30 11:39:30 2022

@author: rz445
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 12:30:08 2022

@author: rosss
"""
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import pathlib
from pathlib import Path
import subprocess
from tkinter import messagebox
from tkinter import ttk
import glob
import platform
import vtkplotlib as vpl
from stl.mesh import Mesh
from PIL import ImageTk, Image
from subprocess import call



def NRRD_open():
    file_selected = askopenfilename()
    NRRD_file_path.set(file_selected)
    
    if file_selected:
        btn_open.configure(bg = "Green",fg='white')
    if not file_selected.endswith('.nrrd'):
        messagebox.showerror("NRRD File Error",\
                             "Please select an NRRD file")
    if Output_folder_path.get() and NRRD_file_path.get():
        color_Process_button()
    
def Output_save():
    folder_selected = askdirectory()
    Output_folder_path.set(folder_selected)
    if folder_selected:
        btn_save.configure(bg = "Green",fg='white')
    if Output_folder_path.get() and NRRD_file_path.get():
        color_Process_button()

def Process():        
    Output_file_name=str(Output_name_value.get())
    
    if Output_folder_path.get() and NRRD_file_path.get() and Output_file_name:
        btn_run.configure(bg = "Green",fg='white')
            
    if not Output_folder_path.get():
        messagebox.showerror("Output Directory Error",\
                             "Please select a directory to save the Output")
    if not NRRD_file_path.get():
        messagebox.showerror("NRRD File Error",\
                             "Please select a file that is an NRRD image")
    if Output_folder_path.get() and NRRD_file_path.get() and Output_file_name:
        print(NRRD_file_path.get())
        print(Output_folder_path.get())
        print(Output_file_name)
        print(temp_path)
        
        output_dir=Output_folder_path.get()
        
        with open('utils/temp.txt', 'w') as f:
            f.write(str(output_dir))
        
        call(["python", "scripts/run.py"])
        colour_image_buttons()
    

def visualize(event=None):
    #Change button colour
    btn_vis.configure(bg = "Green",fg='white')
    # Read the Output using numpy-Output
    mesh = Mesh.from_file(Output_folder_path.get()+"/Segmentation_"+\
                          str(Output_name.get())+".Output")
    fig = vpl.figure("Segmented Output Figure")
    fig.background_color = "grey"
    fig.window_name = "Segmented Output"
    # Plot the mesh
    vpl.mesh_plot(mesh)
    #Adjust camera view
    vpl.view(camera_direction=[0, 1, 0])
    vpl.reset_camera()
    # Show the figure
    vpl.show()
    
def generate_valve(event=None):
    #Change button colour
    
    btn_valve.configure(bg = "Green",fg='white')
    # Read the CSV of the landmarks

    subprocess.call(["python",str(Path.cwd())+"\core.py"])

    
def color_Process_button(event=None):
    if Output_folder_path.get() and NRRD_file_path.get():
        btn_run.configure(bg = "Red",fg='white')   

def colour_image_buttons(event=None):
    btn_img.configure(bg = "Red",fg='white')
    btn_vis.configure(bg = "Red",fg='white')
        

        
def show_images():
    btn_img.configure(bg = "Green",fg='white')
    #Load second frame in window
    frame_window2.grid(row=0, column=0, sticky="W")
    #Creates a Tkinter-compatible photo image, which can be used 
    #everywhere Tkinter expects an image object.
    viewNodeIDs=["vtkMRMLSliceNodeRed", "vtkMRMLSliceNodeGreen",\
                 "vtkMRMLViewNode1","vtkMRMLSliceNodeYellow"]
    i=0
    for viewNode in viewNodeIDs:
        i=i+1
        org_img = Image.open(temp_path+"\\"+viewNode+".png")
        [img_width, img_height] = org_img.size
        resize_img=org_img.resize((int(img_width*0.5), int(img_height*0.5)), Image.ANTIALIAS)
        if i==1:
            img_1=ImageTk.PhotoImage(resize_img)
            img_panel_1.configure(image=img_1)
            img_panel_1.image=img_1
        if i==2:
            img_2=ImageTk.PhotoImage(resize_img)
            img_panel_2.configure(image=img_2)
            img_panel_2.image=img_2
        if i==3:
            img_3=ImageTk.PhotoImage(resize_img)
            img_panel_3.configure(image=img_3)
            img_panel_3.image=img_3
        if i==4:
            img_4=ImageTk.PhotoImage(resize_img)
            img_panel_4.configure(image=img_4)
            img_panel_4.image=img_4
        


#Path to temp image files
temp_path=str(Path.cwd().joinpath("temp"))

#Create window
window = tk.Tk()
window.title("Processer")

window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

NRRD_file_path = tk.StringVar()
Output_folder_path = tk.StringVar()

frame_window = tk.Frame(window)
frame_window2 = tk.Frame(window)

#Buttons
btn_open = tk.Button(frame_window, text="NRRD File", command=NRRD_open)
btn_save = tk.Button(frame_window, text="Output Directory", command=Output_save)
btn_run = tk.Button(frame_window, text="Process Image", command=Process,\
                    bg='Gray', fg='white', font=('helvetica', 14, 'bold'))
btn_img = tk.Button(frame_window, text="Show Images", command=show_images,\
                    bg='Gray', fg='white', font=('helvetica', 14, 'bold'))
btn_vis = tk.Button(frame_window, text="Visualize Output", command=visualize,\
                    bg='Gray', fg='white', font=('helvetica', 14, 'bold'))
btn_valve = tk.Button(frame_window, text="Generate Valve", command=generate_valve,\
                    bg='Gray', fg='white', font=('helvetica', 14, 'bold'))

btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_run.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
btn_img.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
btn_vis.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
btn_valve.grid(row=2, column=1, sticky="ew", padx=5, pady=5)




#Text Entries

#Output save name
label_Output_text=tk.StringVar()
label_Output_text.set("Segmented Name")
label_Output_name=tk.Label(frame_window, textvariable=label_Output_text,\
                        relief="groove",bg = "Green",fg='white')
label_Output_name.grid(row=0,column=1)
Output_name=tk.StringVar(value='Image')
Output_name_value=tk.Entry(frame_window,textvariable=Output_name, width=10)
Output_name_value.grid(row=1,column=1)

#Display Images
#Images will only be displayed once defintion show_images is started
img_panel_text_1=tk.StringVar()
img_panel_text_1.set("Transverse Plane")
img_panel_name_1=tk.Label(frame_window2, textvariable=img_panel_text_1,\
                          relief="groove",bg = "Black",fg='white')
img_panel_name_1.grid(row=8,column=4) 
img_1=[]
img_panel_1 = tk.Label(frame_window2, image = img_1)
img_panel_1.grid(row=9,column=4)

img_panel_text_2=tk.StringVar()
img_panel_text_2.set("Frontal Plane")
img_panel_name_2=tk.Label(frame_window2, textvariable=img_panel_text_2,\
                          relief="groove",bg = "Black",fg='white')
img_panel_name_2.grid(row=10,column=4)
img_2=[]
img_panel_2 = tk.Label(frame_window2, image = img_2)
img_panel_2.grid(row=11,column=4)

img_panel_text_3=tk.StringVar()
img_panel_text_3.set("3D View")
img_panel_name_3=tk.Label(frame_window2, textvariable=img_panel_text_3,\
                          relief="groove",bg = "Black",fg='white')
img_panel_name_3.grid(row=8,column=5)
img_3=[]
img_panel_3 = tk.Label(frame_window2, image = img_3)
img_panel_3.grid(row=9,column=5)

img_panel_text_4=tk.StringVar()
img_panel_text_4.set("Sagittal Plane")
img_panel_name_4=tk.Label(frame_window2, textvariable=img_panel_text_4,\
                          relief="groove",bg = "Black",fg='white')
img_panel_name_4.grid(row=10,column=5)
img_4=[]
img_panel_4 = tk.Label(frame_window2, image = img_4)
img_panel_4.grid(row=11,column=5)


frame_window.grid(row=0, column=0, sticky="NW")

window.mainloop()
