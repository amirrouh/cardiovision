import sys
import os
from pathlib import Path
import customtkinter as ctk
import core

this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, '..'))
sys.path.append(working_dir)



print(working_dir)


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("Carviovision: AI-driven fully automatic medical image processing")

# My Variables
run_successfully = ctk.BooleanVar()

# My Functions
def select_directory():
    directory = ctk.filedialog.askdirectory(title="Please select the directory")
    return directory

def cv_install():
    run_successfully = core.CardioVision.install(button_output_directory)
    return run_successfully



def install():
    text = "Cardiovision will need at least 30 GB of storage. The installation will take up to 30 minutes depending on your system, are you sure you want to continue? type 'yes' to continue, 'no' to cancel:" 
    message =ctk.CTkInputDialog(title="Are you sure?", text=text).get_input()
    if "yes" in message.lower():
        textBox_output.insert(ctk.END, "Installing cardiovision...\nThis may take a while, please wait...\n\n")
        textBox_output.after(1, cv_install)
        if run_successfully.get() == "successfull":
            textBox_output.insert(ctk.END, "Installation finished")
        else:
            textBox_output.insert(ctk.END, "Installation failed, please check the cardiovision.log file for more information")


# Top and Bottom frames
frame_top = ctk.CTkFrame(master=root)
frame_top.pack(pady=10, padx=20, fill="both", expand=True)

frame_bottom = ctk.CTkFrame(master=root)
frame_bottom.pack(side="bottom", pady=10, padx=20, fill="both", expand=True)

# Installation
frame_install = ctk.CTkFrame(master=frame_top)
frame_install.pack(side="left", pady=10, padx=20, fill="both", expand=True)

label_cv = ctk.CTkLabel(master=frame_install, text="Cardiovision", font=("Arial", 25), text_color="gray")
button_output_directory = ctk.CTkButton(master=frame_install, text="Select output directory", text_color="black", command=select_directory)
button_install = ctk.CTkButton(master=frame_install, height=80, text="Install", fg_color="orange", text_color="black", command=install)

label_cv.grid(row=0, column=0, pady=12, padx=10)
button_output_directory.grid(row=1, column=0, pady=12, padx=10)
button_install.grid(row=2, column=0, pady=12, padx=10)


# training
frame_train = ctk.CTkFrame(master=frame_top)
frame_train.pack(side="left", pady=10, padx=20, fill="both", expand=True)

label_training = ctk.CTkLabel(master=frame_train, text="Training CV", font=("Arial", 25), text_color="gray")
button_import_images = ctk.CTkButton(master=frame_train, text="Select Images", text_color="black", command=select_directory)
button_import_labels = ctk.CTkButton(master=frame_train, text="Select Labels", text_color="black", command=select_directory)
button_train = ctk.CTkButton(master=frame_train, text="Train", fg_color="orange", text_color="black", command=install)

label_training.pack(pady=12, padx=10)
button_import_images.pack(pady=12, padx=10)
button_import_labels.pack(pady=12, padx=10)
button_train.pack(pady=12, padx=10)

# Running
frame_running = ctk.CTkFrame(master=frame_top)
frame_running.pack(side="left", pady=10, padx=20, fill="both", expand=True)


label_training = ctk.CTkLabel(frame_running, text="Predictions", font=("Arial", 25), text_color="gray")
button_input = ctk.CTkButton(frame_running, text="Select input file", text_color="black", command=select_directory)
button_prediction = ctk.CTkButton(frame_running, text="Prediction", fg_color="orange", text_color="black", command=install)
button_component = ctk.CTkOptionMenu(master=frame_running, values=core.CNN.GetCNNComponents(), text_color="black")

label_training.pack(pady=12, padx=10)
button_component.pack(pady=12, padx=10)
button_input.pack(pady=12, padx=10)
button_prediction.pack(pady=12, padx=10)



# outputs
frame_outputs = ctk.CTkFrame(master=frame_bottom)
frame_outputs.pack(side="bottom", pady=10, padx=20, fill="both", expand=True)

textBox_output = ctk.CTkTextbox(master=frame_outputs)

# textBox_output.tag_config("center", justify='center')
# textBox_output.tag_add("center", 1.0, "end")
textBox_output.pack()

root.mainloop()
